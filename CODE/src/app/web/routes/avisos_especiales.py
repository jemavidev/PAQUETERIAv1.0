"""
Vista "Avisos especiales" (`.scratch/avisos-especiales`): el ADMIN avisa a mano, por SMS o WhatsApp, a los clientes
con algo pendiente que ciertos días no hay servicio de paquetes. Solo ADMIN (`require_admin`). Las reglas viven en
`app.domain.aviso_especial_service`; esta capa solo arma la pantalla.

El mensaje elegido en el selector viaja en la URL (`?mensaje=<id>`): se conserva al recargar, buscar y filtrar.
"""

import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.domain.aviso_especial_service import (
    elegir_mensaje,
    enlaces_whatsapp,
    listar_clientes,
    listar_mensajes,
)
from app.domain.usuario import Usuario

from ..db import get_db
from ..security import require_admin
from ..templating import templates

router = APIRouter()


def _uuid_o_none(valor: str | None):
    try:
        return uuid.UUID(valor) if valor else None
    except ValueError:
        return None


def _contexto(request: Request, db: Session, admin: Usuario, mensaje_id: str | None) -> dict:
    mensaje = elegir_mensaje(db, _uuid_o_none(mensaje_id))
    clientes = listar_clientes(db)
    return {
        "request": request,
        "admin": admin,
        "clientes": clientes,
        "mensajes": listar_mensajes(db),
        "mensaje": mensaje,
        "whatsapp": {c.persona.id: enlaces_whatsapp(c, mensaje) for c in clientes} if mensaje else {},
    }


@router.get("/administracion/avisos-especiales", response_class=HTMLResponse)
def avisos_especiales(
    request: Request,
    mensaje: str = None,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    return templates.TemplateResponse("admin/avisos_especiales.html", _contexto(request, db, admin, mensaje))
