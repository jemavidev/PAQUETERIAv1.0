# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Vistas del Portal de Clientes
Versión: 1.0.0
Fecha: 2025-01-30
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/templates")

router = APIRouter(
    prefix="/customer-portal",
    tags=["Portal de Clientes - Vistas"]
)


@router.get("/", response_class=HTMLResponse)
async def customer_portal_index(request: Request):
    """Página de entrada - Solicitar código OTP"""
    return templates.TemplateResponse(
        "customer_portal/index.html",
        {"request": request}
    )


@router.get("/verify", response_class=HTMLResponse)
async def customer_portal_verify(request: Request):
    """Página de verificación de código OTP"""
    return templates.TemplateResponse(
        "customer_portal/verify.html",
        {"request": request}
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def customer_portal_dashboard(request: Request):
    """Dashboard del cliente - Ver/editar datos y paquetes"""
    return templates.TemplateResponse(
        "customer_portal/dashboard.html",
        {"request": request}
    )
