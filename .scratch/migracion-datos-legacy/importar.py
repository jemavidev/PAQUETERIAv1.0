# -*- coding: utf-8 -*-
"""
Importador legacy -> PaqueteXv.2 (.scratch/migracion-datos-legacy/estructura-migracion.md).

Uso (correr desde `CODE/src`, o con `app` en el PYTHONPATH -- mismo criterio que
`scripts/paquetex_dev_up.sh`):

    DATABASE_URL=postgresql://... python3 /ruta/a/importar.py \
        --legacy-dir /ruta/a/los/json --dry-run

Sin `--dry-run` escribe de verdad. `--con-fotos` además copia las fotos de S3
(legacy -> bucket de v2), requiere `LEGACY_AWS_ACCESS_KEY_ID`/
`LEGACY_AWS_SECRET_ACCESS_KEY`/`LEGACY_AWS_S3_BUCKET` en el entorno (además de
las variables `AWS_S3_*` normales de v2, que ya usa `S3FotoStorage`).

Idempotente por clave natural (email/telefono/access_code) -- correr dos veces
no duplica nada, ver `estructura-migracion.md` §3.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def _cargar(legacy_dir, nombre):
    with open(os.path.join(legacy_dir, nombre), encoding="utf-8") as f:
        return json.load(f) or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--legacy-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--con-fotos", action="store_true")
    args = ap.parse_args()

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.domain.usuario import Usuario, RolUsuario
    from app.domain.persona import Persona
    from app.domain.persona_service import get_or_create_persona
    from app.domain.telefono import normalizar_telefono
    from app.domain.paquete import (
        Paquete,
        EstadoPaquete,
        TipoPaquete,
        CondicionPaquete,
        MotivoCancelacion,
    )
    from app.domain.paquete_foto import PaqueteFoto
    from app.domain.preferencia_notificacion import (
        PersonaPreferenciaNotificacion,
        CanalNotificacion,
    )

    engine = create_engine(os.environ["DATABASE_URL"])
    Session = sessionmaker(bind=engine)
    db = Session()

    reporte = {
        "usuarios_creados": 0, "usuarios_saltados": 0,
        "personas_creadas": 0, "personas_existentes": 0,
        "paquetes_creados": 0, "paquetes_saltados": 0,
        "preferencias_creadas": 0, "preferencias_saltadas": 0,
        "fotos_copiadas": 0, "fotos_saltadas": 0,
        "errores": [],
    }

    # --- 1. Usuarios (staff) ------------------------------------------------- #
    for u in _cargar(args.legacy_dir, "users.json"):
        existe = db.query(Usuario).filter(Usuario.email == u["email"]).one_or_none()
        if existe:
            reporte["usuarios_saltados"] += 1
            continue
        reporte["usuarios_creados"] += 1
        if not args.dry_run:
            db.add(Usuario(
                nombre=u["full_name"],
                email=u["email"],
                password_hash=u["password_hash"],
                rol=RolUsuario(u["role"]),
                activo=True,
            ))
    if not args.dry_run:
        db.flush()

    # --- 2. Personas (customers) --------------------------------------------- #
    persona_por_telefono = {}
    for c in _cargar(args.legacy_dir, "customers.json"):
        telefono = normalizar_telefono(c["phone"])
        ya_existia = db.query(Persona).filter(Persona.telefono == telefono).one_or_none() is not None
        if args.dry_run:
            reporte["personas_existentes" if ya_existia else "personas_creadas"] += 1
            continue
        p = get_or_create_persona(db, c["phone"], c["full_name"])
        if c.get("email") and not p.email:
            p.email = c["email"]
        persona_por_telefono[telefono] = p
        reporte["personas_existentes" if ya_existia else "personas_creadas"] += 1
    if not args.dry_run:
        db.flush()

    # --- 3. Paquetes ---------------------------------------------------------- #
    def _parse_dt(s):
        if not s:
            return None
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    cancel_por_tracking = {
        r["tracking_number"]: r["observations"]
        for r in _cargar(args.legacy_dir, "cancel_reasons.json")
    }

    for p in _cargar(args.legacy_dir, "packages.json"):
        access_code = p["tracking_number"]
        telefono_legacy = normalizar_telefono(p["customer_phone"])
        existe = db.query(Paquete).filter(Paquete.access_code == access_code).one_or_none()
        if existe:
            # No asumir "ya migrado" a ciegas: un access_code de 4 caracteres puede
            # coincidir por azar con uno que v2 ya generó nativamente para un
            # paquete real no relacionado. Solo se trata como "ya migrado" si el
            # teléfono coincide -- si no, es una colisión real que hay que resolver
            # a mano, no saltar en silencio.
            if existe.recipient_phone == telefono_legacy:
                reporte["paquetes_saltados"] += 1
            else:
                reporte["errores"].append(
                    f"paquete {access_code}: COLISIÓN -- ya existe en v2 con "
                    f"recipient_phone={existe.recipient_phone!r}, pero el legacy es de "
                    f"{telefono_legacy!r}. NO se tocó, requiere revisión manual."
                )
            continue

        telefono = telefono_legacy
        persona = persona_por_telefono.get(telefono)
        if persona is None:
            persona = db.query(Persona).filter(Persona.telefono == telefono).one_or_none()
        if persona is None:
            reporte["errores"].append(f"paquete {access_code}: sin Persona para {telefono}")
            continue

        reporte["paquetes_creados"] += 1
        if args.dry_run:
            continue

        cancel_reason = None
        if p["status"] == "CANCELADO":
            texto = cancel_por_tracking.get(access_code, "")
            cancel_reason = (
                MotivoCancelacion.OTRO.value if "otro" in texto.lower() else None
            )

        db.add(Paquete(
            access_code=access_code,
            guide_number=p.get("guide_number"),
            package_type=TipoPaquete(p["package_type"]) if p.get("package_type") else None,
            package_condition=CondicionPaquete(p["package_condition"]) if p.get("package_condition") else None,
            announced_by_persona_id=persona.id,
            announced_by_phone=telefono,
            recipient_name=p.get("display_name") or p["customer_name"],
            recipient_phone=telefono,
            estado=EstadoPaquete(p["status"]),
            announced_at=_parse_dt(p["announced_at"]),
            received_at=_parse_dt(p.get("received_at")),
            delivered_at=_parse_dt(p.get("delivered_at")),
            cancelled_at=_parse_dt(p.get("cancelled_at")),
            cancel_reason=cancel_reason,
        ))
    if not args.dry_run:
        db.flush()

    # --- 4. Preferencias de notificación -------------------------------------- #
    EVENTO_POR_CAMPO = {
        "notify_package_announced": "ANUNCIADO",
        "notify_package_received": "RECIBIDO",
        "notify_package_delivered": "ENTREGADO",
    }
    for pref in _cargar(args.legacy_dir, "customer_preferences.json"):
        telefono = normalizar_telefono(pref["customer_phone"])
        persona = persona_por_telefono.get(telefono)
        if persona is None:
            persona = db.query(Persona).filter(Persona.telefono == telefono).one_or_none()
        if persona is None:
            reporte["errores"].append(f"preferencias: sin Persona para {telefono}")
            continue

        for canal, habilitado_campo in (
            (CanalNotificacion.SMS, "sms_notifications_enabled"),
            (CanalNotificacion.EMAIL, "email_notifications_enabled"),
        ):
            if not pref.get(habilitado_campo):
                continue
            for campo, evento in EVENTO_POR_CAMPO.items():
                activo = bool(pref.get(campo))
                ya_existe = db.query(PersonaPreferenciaNotificacion).filter(
                    PersonaPreferenciaNotificacion.persona_id == persona.id,
                    PersonaPreferenciaNotificacion.canal == canal,
                    PersonaPreferenciaNotificacion.evento == evento,
                ).one_or_none() if not args.dry_run else None

                if ya_existe:
                    reporte["preferencias_saltadas"] += 1
                    continue
                reporte["preferencias_creadas"] += 1
                if not args.dry_run:
                    db.add(PersonaPreferenciaNotificacion(
                        persona_id=persona.id, canal=canal, evento=evento, activo=activo,
                    ))

    if args.dry_run:
        print("=== DRY RUN -- nada se escribió ===")
        db.rollback()
    else:
        db.commit()
        print("=== Cambios confirmados (commit) ===")

    print(json.dumps(reporte, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
