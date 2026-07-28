# -*- coding: utf-8 -*-
"""
Ruta `/mis-datos` — tablero de autoedición del cliente.

Protegida por `current_customer`. El residente edita sus datos ampliables
(`update_datos_personales`, actualización parcial) y puede **declarar su
Apartamento** — reutilizando `get_or_create_apartamento` + `declare_unit` sin
cambios, pasando UN solo miembro (él mismo): es la forma correcta de "declarar a
propósito" desde esta vista (§6.4), no un "a nombre de" casual.

Validación "todo o nada por request": cualquier error (email inválido, o
Apartamento con campos incompletos) hace `rollback` antes de re-mostrar el
formulario, de modo que ningún cambio del envío queda a medias.
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.domain.apartamento import Apartamento
from app.domain.apartamento_service import declare_unit, get_or_create_apartamento
from app.domain.persona import Persona
from app.domain.persona_service import set_notificaciones_activas, update_datos_personales

from ..db import get_db
from ..security import current_customer
from ..templating import templates

router = APIRouter()


def _blank_to_none(valor: str):
    valor = (valor or "").strip()
    return valor or None


def _apartamento_actual(db: Session, persona: Persona):
    if persona.apartamento_actual_id is None:
        return None
    return db.get(Apartamento, persona.apartamento_actual_id)


@router.get("/mis-datos", response_class=HTMLResponse)
def customer_verify_form(
    request: Request,
    persona: Persona = Depends(current_customer),
    db: Session = Depends(get_db),
):
    return templates.TemplateResponse(
        "customer/verify.html",
        {
            "request": request,
            "persona": persona,
            "apartamento": _apartamento_actual(db, persona),
            "guardado": request.query_params.get("guardado") == "1",
        },
    )


@router.post("/mis-datos", response_class=HTMLResponse)
def customer_verify_submit(
    request: Request,
    persona: Persona = Depends(current_customer),
    db: Session = Depends(get_db),
    nombre: str = Form(None),
    email: str = Form(None),
    segundo_contacto: str = Form(None),
    torre: str = Form(None),
    apartamento: str = Form(None),
    notificaciones_activas: str = Form(None),
):
    def _error(mensaje: str):
        db.rollback()  # "todo o nada": deshace cualquier mutación de este request
        return templates.TemplateResponse(
            "customer/verify.html",
            {
                "request": request,
                "persona": persona,
                "apartamento": _apartamento_actual(db, persona),
                "error": mensaje,
            },
            status_code=400,
        )

    # El Conjunto NUNCA lo escribe el cliente (Grupo 12, Ronda 2) — solo el
    # staff lo asigna. Se toma tal cual del apartamento ya asignado, si hay
    # alguno; nunca de lo que venga en el formulario.
    apartamento_existente = _apartamento_actual(db, persona)
    conjunto_v = apartamento_existente.conjunto if apartamento_existente else None
    torre_v = _blank_to_none(torre)
    apartamento_v = _blank_to_none(apartamento)

    if (torre_v or apartamento_v) and conjunto_v is None:
        return _error(
            "Tu conjunto todavía no ha sido asignado por el staff — "
            "avísales en portería antes de declarar torre y apartamento."
        )

    partes_apto = [conjunto_v, torre_v, apartamento_v]
    if any(partes_apto) and not all(partes_apto):
        return _error("Completa Torre y Apartamento, o deja los dos vacíos.")

    try:
        update_datos_personales(
            db,
            persona,
            nombre=_blank_to_none(nombre),
            email=_blank_to_none(email),
            segundo_contacto=_blank_to_none(segundo_contacto),
        )
    except ValueError as exc:
        return _error(str(exc))

    # Checkbox: presente (marcado) = True; ausente (desmarcado, HTML no lo
    # envía) = False. Distinto del resto de campos, cuya ausencia significa
    # "no tocar" — un checkbox siempre representa su estado actual.
    set_notificaciones_activas(db, persona, notificaciones_activas is not None)

    if all(partes_apto):
        apto = get_or_create_apartamento(db, conjunto_v, torre_v, apartamento_v)
        # Un solo miembro (el propio cliente): declaración a propósito, no agrupa
        # a nadie más que a sí mismo.
        declare_unit(db, apto, [(persona.telefono, persona.nombre)])

    return RedirectResponse("/mis-datos?guardado=1", status_code=303)
