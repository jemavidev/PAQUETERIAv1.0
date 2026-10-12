"""
Vista "Avisos especiales" (`.scratch/avisos-especiales`): el ADMIN avisa a mano, por SMS o WhatsApp, a los clientes
con algo pendiente que ciertos días no hay servicio de paquetes. Solo ADMIN (`require_admin`). Las reglas viven en
`app.domain.aviso_especial_service`; esta capa solo arma la pantalla.

El mensaje elegido en el selector viaja en la URL (`?mensaje=<id>`): se conserva al recargar, buscar y filtrar.
"""

import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.domain.aviso_especial_service import (
    AvisoNoEnviable,
    elegir_mensaje,
    enlaces_whatsapp,
    enviar_sms,
    listar_clientes,
    listar_mensajes,
)
from app.domain.notification_sender import NotificationSender
from app.domain.usuario import Usuario

from ..db import get_db
from ..notifications import get_notification_sender, sms_configurado
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


# Resultado de un envío sin JS (Post/Redirect/Get): el POST redirige con `?resultado=` y la vista muestra el aviso.
_AVISOS_RESULTADO = {
    "enviado": ("SMS enviado.", "success"),
    "fallo": ("No se pudo enviar el SMS. Intenta de nuevo.", "danger"),
}


@router.get("/administracion/avisos-especiales", response_class=HTMLResponse)
def avisos_especiales(
    request: Request,
    mensaje: str = None,
    resultado: str = None,
    error: str = None,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    contexto = _contexto(request, db, admin, mensaje)
    if resultado in _AVISOS_RESULTADO:
        contexto["aviso"], contexto["aviso_variante"] = _AVISOS_RESULTADO[resultado]
    elif error:
        contexto["aviso"], contexto["aviso_variante"] = error, "danger"
    return templates.TemplateResponse("admin/avisos_especiales.html", contexto)


@router.post("/administracion/avisos-especiales/sms", response_class=HTMLResponse)
def avisos_especiales_enviar_sms(
    request: Request,
    persona_id: str = Form(None),
    mensaje: str = Form(None),
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
    sender: NotificationSender = Depends(get_notification_sender),
):
    """Envía por SMS el mensaje elegido a UN cliente (ticket 05). Síncrono: espera la respuesta real del proveedor.

    Con JS (`X-Requested-With: fetch`) responde la fila de ese cliente ya actualizada (nuevo "Último SMS" o el aviso
    rojo de falla) para reemplazarla sin recargar; un error que impide intentar el envío responde 400 con el texto.
    Sin JS, redirige a la vista con el resultado (Post/Redirect/Get)."""
    es_fetch = request.headers.get("X-Requested-With") == "fetch"
    mensaje_id, pid = _uuid_o_none(mensaje), _uuid_o_none(persona_id)

    def _error(texto: str):
        if es_fetch:
            return HTMLResponse(texto, status_code=400)
        return _volver(mensaje, error=texto)

    if not sms_configurado():
        return _error("El SMS no está configurado todavía (Administración → Proveedores).")
    if mensaje_id is None or pid is None:
        return _error("Datos de envío inválidos.")
    try:
        resultado = enviar_sms(db, pid, mensaje_id, sender, usuario_id=admin.id)
    except AvisoNoEnviable as exc:
        return _error(str(exc))

    if not es_fetch:
        return _volver(mensaje, resultado="enviado" if resultado.enviado else "fallo")
    mensaje_actual = elegir_mensaje(db, mensaje_id)
    return templates.TemplateResponse(
        "admin/_aviso_cliente.html",
        {
            "request": request,
            "cliente": resultado.cliente,
            "mensaje": mensaje_actual,
            "whatsapp": {resultado.cliente.persona.id: enlaces_whatsapp(resultado.cliente, mensaje_actual)},
            "fallo_sms": None if resultado.enviado else resultado.cliente.persona.id,
        },
    )


def _volver(mensaje: str | None, **params) -> RedirectResponse:
    consulta = urlencode({k: v for k, v in {"mensaje": mensaje, **params}.items() if v})
    return RedirectResponse(f"/administracion/avisos-especiales?{consulta}", status_code=303)
