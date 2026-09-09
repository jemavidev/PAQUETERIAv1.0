# -*- coding: utf-8 -*-
"""
Ruta `/consultar` — consultar el estado de un paquete (vista pública, sin
sesión).

Busca SOLO por `access_code` o `guide_number` exactos (Grupo 2 de
`ajustes-post-referencia-funcional/REQUERIMIENTOS.md`) — a propósito, NUNCA
por teléfono: el `access_code` únicamente lo conoce quien anunció, así que es
la única llave de consulta pública. El timeline (con actor por hito, y
`dias_desde_recibido`) vive en `paquete_timeline_service` — compartido con
`/mis-paquetes`, que cuenta la misma historia del mismo paquete para el
cliente autenticado.

Botones "Entregar"/"Recibir" (issue 124/171, staff únicamente): esta vista
sigue sin `Depends(current_staff)` -- el gate real de AMBOS vive en el
endpoint que el form de cada modal termina llamando (`/paquetes/{id}/recibir`,
`/paquetes/{id}/entregar`, los mismos que usa `/paquetes`), no acá. El
contexto extra que necesita el modal "Recibir" (catálogo de torres, tipos,
condiciones, residentes de la unidad, candidatos de corrección) solo se
calcula cuando SÍ hay una sesión de staff activa -- evita ese trabajo de más
en la inmensa mayoría de las consultas, que son de residentes anónimos sin
sesión.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse

from sqlalchemy import or_

from app.domain.apartamento_service import listar_catalogo_por_torre
from app.domain.cobro_service import (
    calcular_cobro,
    listar_motivos_anulacion,
    obtener_tarifas_vigentes,
)
from app.domain.ocupante_service import residentes_por_torre_apartamento
from app.domain.paquete import CondicionPaquete, EstadoPaquete, Paquete, TipoPaquete
from app.domain.paquete_correccion_service import candidatos_correccion
from app.domain.paquete_foto_service import listar_fotos
from app.domain.paquete_service import es_primera_entrega_a_telefono
from app.domain.paquete_timeline_service import dias_desde_recibido, timeline_de_paquete

from ..db import get_db
from ..rate_limit import rate_limit
from ..security import SESSION_KEY
from ..templating import templates

router = APIRouter()

_MENSAJE_RATE_LIMIT = "Demasiados intentos. Espera un momento e inténtalo de nuevo."


@router.get("/consultar", response_class=HTMLResponse)
def search(
    request: Request,
    q: str = None,
    db: Session = Depends(get_db),
    # .scratch/migracion-por-anio, ticket 02: 10/60s por IP, mismo mecanismo
    # genérico ya usado en OTP/login/restablecer contraseña -- mitigación
    # parcial del riesgo aceptado de reciclar access_code entre años (ver
    # spec.md).
    permitido: bool = Depends(rate_limit("consultar_publico", 10, 60)),
):
    if not permitido:
        return templates.TemplateResponse(
            "search/form.html",
            {"request": request, "q": q or "", "error": _MENSAJE_RATE_LIMIT},
            status_code=429,
        )

    termino = (q or "").strip()
    if not termino:
        return templates.TemplateResponse(
            "search/form.html", {"request": request, "q": ""}
        )

    paquete = (
        db.query(Paquete)
        .filter(
            or_(Paquete.access_code == termino, Paquete.guide_number == termino)
        )
        .one_or_none()
    )
    if paquete is not None:
        contexto = {
            "request": request,
            "q": termino,
            "paquete": paquete,
            "timeline": timeline_de_paquete(db, paquete),
            "fotos": listar_fotos(db, paquete),
            "dias_desde_recibido": dias_desde_recibido(paquete),
        }
        # Issue 171 (.scratch/pendientes-cliente): mismo contexto que ya
        # arma `packages.py` para el modal `modal_recibir` compartido --
        # nada nuevo, solo reusado acá para el único Paquete de esta vista.
        if request.session.get(SESSION_KEY) and paquete.estado == EstadoPaquete.ANUNCIADO:
            contexto.update(
                {
                    "tipos": list(TipoPaquete),
                    "condiciones": list(CondicionPaquete),
                    "catalogo_torres": listar_catalogo_por_torre(db),
                    "residentes_por_unidad": residentes_por_torre_apartamento(db),
                    "candidatos_correccion": candidatos_correccion(db, paquete),
                }
            )
        # Issue 314/316 (.scratch/pendientes-cliente): el modal Entregar de
        # esta vista es un DUPLICADO del de `/paquetes` (`packages.py::
        # _listar` calcula esto mismo en batch para su propia lista) -- acá
        # solo hay UN paquete, así que se resuelve directo, sin batch,
        # gated igual que el propio modal (staff + RECIBIDO) para no pagar
        # el query de más en la inmensa mayoría de consultas anónimas.
        if request.session.get(SESSION_KEY) and paquete.estado == EstadoPaquete.RECIBIDO:
            paquete.primera_entrega_a_telefono = es_primera_entrega_a_telefono(
                db, paquete.recipient_phone
            )
            # .scratch/cobro-bodegaje, ticket 02: mismo criterio que arriba
            # -- acá solo hay UN paquete, se resuelve directo sin batch.
            contexto["cobro_desglose"] = calcular_cobro(
                paquete,
                obtener_tarifas_vigentes(db),
                datetime.now(timezone.utc),
                paquete.primera_entrega_a_telefono,
            )
            contexto["motivos_anulacion_cobro"] = listar_motivos_anulacion(db)
        return templates.TemplateResponse("search/form.html", contexto)

    return templates.TemplateResponse(
        "search/form.html", {"request": request, "q": termino, "sin_resultados": True}
    )
