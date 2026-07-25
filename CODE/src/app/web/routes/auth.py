# -*- coding: utf-8 -*-
"""
Rutas de autenticación de staff — `/auth/login`, `/auth/logout`, `/auth/me`.

Login con email + contraseña (server-rendered). La sesión guarda el `usuario_id`;
`current_staff` la lee para producir el actor de las acciones. Mensajes de error
GENÉRICOS (no revelan si el email existe).
"""

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.domain.staff_service import verify_credentials
from app.domain.usuario import Usuario

from ..db import get_db
from ..security import SESSION_KEY, current_staff
from ..templating import templates

router = APIRouter()


@router.get("/auth/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/auth/login")
def login_submit(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(None),
    password: str = Form(None),
):
    def _error():
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Email o contraseña incorrectos.",
                "email": email or "",
            },
            status_code=400,
        )

    if not (email or "").strip() or not (password or ""):
        return _error()

    usuario = verify_credentials(db, email, password)
    if usuario is None:
        return _error()

    request.session[SESSION_KEY] = str(usuario.id)
    return RedirectResponse("/auth/me", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/auth/logout")
def logout(request: Request):
    # pop, no clear: la sesión de cliente (persona_id) es independiente y no debe
    # cerrarse al cerrar la de staff.
    request.session.pop(SESSION_KEY, None)
    return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/auth/me", response_class=HTMLResponse)
def me(request: Request, usuario: Usuario = Depends(current_staff)):
    return templates.TemplateResponse(
        "auth/me.html", {"request": request, "usuario": usuario}
    )
