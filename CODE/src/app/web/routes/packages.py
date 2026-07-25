# -*- coding: utf-8 -*-
"""
Vista de staff `/packages` — lista + acciones del ciclo de vida.

Protegida por `current_staff`: el `Usuario` de la sesión es el **actor** de cada
transición (recibir/entregar/cancelar), nunca un id enviado por el cliente. Las
acciones exitosas redirigen a `/packages` (PRG); las transiciones inválidas
re-muestran la lista con un aviso, sin efecto.
"""

import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.domain.paquete import Paquete
from app.domain.paquete_lifecycle import TransicionInvalida, deliver, receive
from app.domain.usuario import Usuario

from ..db import get_db
from ..security import current_staff
from ..templating import templates

router = APIRouter()


def _listar(db: Session):
    return db.query(Paquete).order_by(Paquete.announced_at.desc()).all()


def _render_lista(request, db, staff, error=None, status_code=200):
    return templates.TemplateResponse(
        "packages/list.html",
        {"request": request, "paquetes": _listar(db), "staff": staff, "error": error},
        status_code=status_code,
    )


def _get_paquete_o_404(db: Session, paquete_id: str) -> Paquete:
    try:
        pid = uuid.UUID(paquete_id)
    except (ValueError, TypeError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Paquete no encontrado")
    paquete = db.get(Paquete, pid)
    if paquete is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Paquete no encontrado")
    return paquete


@router.get("/packages", response_class=HTMLResponse)
def packages_list(
    request: Request,
    db: Session = Depends(get_db),
    staff: Usuario = Depends(current_staff),
):
    return _render_lista(request, db, staff)


@router.post("/packages/{paquete_id}/receive")
def receive_action(
    paquete_id: str,
    request: Request,
    db: Session = Depends(get_db),
    staff: Usuario = Depends(current_staff),
    guide_number: str = Form(None),
):
    paquete = _get_paquete_o_404(db, paquete_id)
    guia = (guide_number or "").strip() or None
    try:
        receive(db, paquete, staff, guia)
    except TransicionInvalida as exc:
        return _render_lista(request, db, staff, error=str(exc), status_code=400)
    return RedirectResponse("/packages", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/packages/{paquete_id}/deliver")
def deliver_action(
    paquete_id: str,
    request: Request,
    db: Session = Depends(get_db),
    staff: Usuario = Depends(current_staff),
):
    paquete = _get_paquete_o_404(db, paquete_id)
    try:
        deliver(db, paquete, staff)
    except TransicionInvalida as exc:
        return _render_lista(request, db, staff, error=str(exc), status_code=400)
    return RedirectResponse("/packages", status_code=status.HTTP_303_SEE_OTHER)
