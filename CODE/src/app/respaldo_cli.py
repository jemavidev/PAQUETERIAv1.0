# -*- coding: utf-8 -*-
"""
Respaldos de esta instalación (`.scratch/respaldos-y-restauracion`).

Un solo comando para el cron diario, el paso previo al deploy y el botón
"Respaldar ahora": todos respaldan por el mismo camino (`respaldo_service`).

Variables de entorno:
    DATABASE_URL            la base de esta instalación
    PUBLIC_BASE_URL         de ahí sale el dominio (la carpeta del respaldo en S3, y la
                            protección de "mismo sistema" al restaurar)
    RESPALDO_DIR            carpeta de respaldos locales (default `/respaldos`)
    RESPALDO_CHECKOUT_DIR   checkout desplegado, montado en solo lectura (default
                            `/app/checkout`): de ahí sale el commit
    RESPALDO_CODIGO_DIR     carpeta con `alembic.ini` del código instalado (default `/app`)

Uso (dentro del contenedor, desde `/app/src`; ver `scripts/respaldos/`):
    python -m app.respaldo_cli respaldar --motivo diario
    python -m app.respaldo_cli verificar /respaldos/<carpeta>
    python -m app.respaldo_cli restaurar /respaldos/<carpeta> --confirmacion <dominio> [--otro-destino]
    (restaurar se corre desde `scripts/respaldos/restaurar.sh`, que detiene y enciende la app)

Código de salida distinto de cero si el respaldo no se completó (o si ya había otro en curso).
"""

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from app.domain.respaldo_service import (
    Instalacion,
    MotivoRespaldo,
    RespaldoEnCurso,
    RespaldoFallido,
    RestauracionRechazada,
    crear_respaldo,
    leer_commit,
    restaurar,
    verificar_respaldo,
)


def _requerida(nombre: str) -> str:
    valor = os.environ.get(nombre)
    if not valor:
        raise SystemExit(f"Falta {nombre} en el entorno.")
    return valor


def _instalacion() -> Instalacion:
    dominio = urlparse(_requerida("PUBLIC_BASE_URL")).hostname
    if not dominio:
        raise SystemExit("PUBLIC_BASE_URL no tiene un dominio válido.")
    checkout = Path(os.environ.get("RESPALDO_CHECKOUT_DIR", "/app/checkout"))
    return Instalacion(database_url=_requerida("DATABASE_URL"), dominio=dominio, commit=leer_commit(checkout))


def _resumen(carpeta: Path) -> str:
    m = verificar_respaldo(carpeta)
    conteos = ", ".join(f"{n} {t}" for t, n in m.conteos.items())
    return (
        f"Respaldo {carpeta.name}: {m.dominio} ({m.conjunto}), {m.fecha_hora_colombia} hora Colombia, "
        f"motivo {m.motivo.value}, commit {m.commit[:12]}, versión {m.version_bd}. Huellas OK. {conteos}."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Respaldos de PaqueteX")
    sub = parser.add_subparsers(dest="accion", required=True)
    respaldar = sub.add_parser("respaldar", help="Saca un respaldo ahora")
    respaldar.add_argument("--motivo", choices=[m.value for m in MotivoRespaldo], default=MotivoRespaldo.DIARIO.value)
    verificar = sub.add_parser("verificar", help="Comprueba las huellas de un respaldo y dice qué contiene")
    verificar.add_argument("carpeta", type=Path)
    rest = sub.add_parser("restaurar", help="Restaura un respaldo (usar scripts/respaldos/restaurar.sh)")
    rest.add_argument("carpeta", type=Path)
    rest.add_argument("--confirmacion", required=True, help="El dominio de esta instalación, escrito a mano")
    rest.add_argument("--otro-destino", action="store_true", help="Restaurar un respaldo de otro dominio a propósito")
    args = parser.parse_args()

    carpeta = Path(os.environ.get("RESPALDO_DIR", "/respaldos"))
    try:
        if args.accion == "verificar":
            print(_resumen(args.carpeta))
            return 0
        if args.accion == "restaurar":
            restaurar(
                args.carpeta,
                _instalacion(),
                confirmacion=args.confirmacion,
                carpeta_respaldos=carpeta,
                codigo=Path(os.environ.get("RESPALDO_CODIGO_DIR", "/app")),
                permitir_otro_destino=args.otro_destino,
            )
            print(f"Restaurado: {args.carpeta.name}")
            return 0
        respaldo = crear_respaldo(_instalacion(), carpeta, MotivoRespaldo(args.motivo))
    except RestauracionRechazada as exc:
        print(f"NO se restauró: {exc}", file=sys.stderr)
        return 2
    except RespaldoEnCurso as exc:
        print(f"No se hizo: {exc}", file=sys.stderr)
        return 3
    except RespaldoFallido as exc:
        print(f"Respaldo FALLIDO en el paso «{exc.paso}»: {exc.detalle}", file=sys.stderr)
        return 1
    print(f"Respaldo listo: {respaldo.carpeta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
