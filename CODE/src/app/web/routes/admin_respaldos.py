# -*- coding: utf-8 -*-
"""
Pantalla "Respaldos" (`.scratch/respaldos-y-restauracion`, tickets 08-11) -- solo ADMIN.

Lista los respaldos del disco del servidor (las últimas 3 copias; los anteriores viven en S3 y se descargan con la
cuenta de AWS: la llave del servidor, a propósito, no puede leer el bucket), los entrega como `.zip` por partes y
muestra el comando exacto para restaurar cada uno por SSH. Restaurar NO se hace desde la web.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.domain.respaldo_service import (
    leer_historial,
    leer_manifiesto,
    listar_respaldos,
    zip_de_respaldo,
)
from app.domain.operacion_respaldo import TipoOperacion
from app.domain.operacion_respaldo_service import OperacionEnCurso, en_curso, iniciar_operacion, ultima_operacion
from app.domain.usuario import Usuario
from app.domain.zona_horaria import ZONA_HORARIA_APP

from ..db import get_db
from ..security import require_admin
from ..templating import templates

router = APIRouter()

MOTIVOS = {
    "diario": "Diario",
    "antes_de_deploy": "Antes de deploy",
    "a_pedido": "A pedido",
    "antes_de_restaurar": "Antes de restaurar",
}


def _carpeta() -> Path:
    return Path(os.environ.get("RESPALDO_DIR", "/respaldos"))


def _lanzar_respaldo(operacion_id) -> None:
    """"Respaldar ahora" en un proceso aparte (sesión propia): sigue aunque se cierre la pantalla o termine la
    petición, y es el mismo comando que usan el cron y el deploy. Su salida va al log de operaciones."""
    src = Path(__file__).resolve().parents[3]
    log = open(_carpeta() / ".operaciones.log", "a")
    subprocess.Popen(
        [sys.executable, "-m", "app.respaldo_cli", "respaldar", "--motivo", "a_pedido", "--operacion", str(operacion_id)],
        cwd=src,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )


def get_lanzador_respaldo():
    return _lanzar_respaldo


def _fila(carpeta: Path) -> dict:
    try:
        m = leer_manifiesto(carpeta)
        fecha, motivo, conteos = m.fecha_hora_colombia[:16], MOTIVOS.get(m.motivo.value, m.motivo.value), m.conteos
    except Exception:
        fecha, motivo, conteos = carpeta.name, "(manifiesto ilegible)", {}
    return {
        "nombre": carpeta.name,
        "fecha": fecha,
        "motivo": motivo,
        "tamano_mb": sum(a.stat().st_size for a in carpeta.iterdir() if a.is_file()) / 1_000_000,
        "paquetes": conteos.get("paquetes"),
        "personas": conteos.get("personas"),
    }


def _pantalla(request: Request, db: Session, admin: Usuario, aviso: str | None = None):
    carpeta = _carpeta()
    corridas = [c for c in leer_historial(carpeta) if c["motivo"] in MOTIVOS]
    ultima = None
    if corridas:
        ultima = dict(corridas[-1])
        ultima["fecha"] = datetime.fromisoformat(ultima["fecha_utc"]).astimezone(ZONA_HORARIA_APP).strftime("%Y-%m-%d %H:%M")
        ultima["motivo_texto"] = MOTIVOS[ultima["motivo"]]
    return templates.TemplateResponse(
        "admin/respaldos.html",
        {
            "request": request,
            "admin": admin,
            "respaldos": [_fila(c) for c in reversed(listar_respaldos(carpeta))],
            "ultima_corrida": ultima,
            "carpeta_host": os.environ.get("RESPALDO_DIR_HOST", "/home/ubuntu/paquetex-respaldos"),
            "app_host": os.environ.get("RESPALDO_APP_DIR_HOST", "/home/ubuntu/app/PaqueteX"),
            "bucket": os.environ.get("RESPALDO_S3_BUCKET", "paquetex-respaldos"),
            "a_pedido": _estado_operacion(ultima_operacion(db, TipoOperacion.RESPALDO)),
            "aviso": aviso,
        },
    )


def _estado_operacion(operacion) -> dict | None:
    if operacion is None:
        return None
    return {
        "en_curso": en_curso(operacion),
        "interrumpida": operacion.estado == "en_curso" and not en_curso(operacion),
        "ok": operacion.estado == "ok",
        "desde": operacion.inicio.astimezone(ZONA_HORARIA_APP).strftime("%Y-%m-%d %H:%M"),
        "solicitado_por": operacion.solicitado_por,
        "detalle": operacion.detalle,
        "avance_actual": operacion.avance_actual,
        "avance_total": operacion.avance_total,
    }


@router.get("/administracion/respaldos", response_class=HTMLResponse)
def admin_respaldos(request: Request, db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    return _pantalla(request, db, admin)


@router.post("/administracion/respaldos/ahora")
def admin_respaldos_ahora(
    request: Request,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
    lanzar=Depends(get_lanzador_respaldo),
):
    try:
        operacion = iniciar_operacion(db, TipoOperacion.RESPALDO, admin.email)
    except OperacionEnCurso:
        return _pantalla(request, db, admin, aviso="Ya hay un respaldo en curso: espera a que termine.")
    db.commit()
    lanzar(operacion.id)
    return RedirectResponse("/administracion/respaldos", status_code=303)


@router.get("/administracion/respaldos/{nombre}/descargar")
def admin_respaldos_descargar(nombre: str, admin: Usuario = Depends(require_admin)):
    # Solo un nombre de la lista: nunca una ruta armada con lo que mande el navegador.
    respaldo = next((c for c in listar_respaldos(_carpeta()) if c.name == nombre), None)
    if respaldo is None:
        raise HTTPException(status_code=404)
    return StreamingResponse(
        zip_de_respaldo(respaldo),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{respaldo.name}.zip"'},
    )
