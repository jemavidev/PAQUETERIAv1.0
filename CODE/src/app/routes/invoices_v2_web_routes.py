"""
Rutas web para las vistas HTML del sistema de facturas V2
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db

router = APIRouter(prefix="/invoices", tags=["Invoices V2 Web"])

# Configurar templates
templates = Jinja2Templates(directory="src/templates")


@router.get("/facturas", response_class=HTMLResponse)
async def facturas_page(request: Request):
    """
    TAB 1: Vista de gestión de facturas de proveedores
    """
    return templates.TemplateResponse("invoices_v2/facturas.html", {
        "request": request,
        "active_tab": "facturas"
    })


@router.get("/cufe", response_class=HTMLResponse)
async def cufe_page(request: Request):
    """
    TAB 2: Vista de gestión de códigos CUFE y archivos DIAN
    """
    return templates.TemplateResponse("invoices_v2/cufe.html", {
        "request": request,
        "active_tab": "cufe"
    })


@router.get("/productos", response_class=HTMLResponse)
async def productos_page(request: Request):
    """
    TAB 3: Vista de catálogo de productos
    """
    return templates.TemplateResponse("invoices_v2/productos.html", {
        "request": request,
        "active_tab": "productos"
    })


@router.get("/", response_class=HTMLResponse)
async def index_redirect(request: Request):
    """
    Redirige a la vista de facturas por defecto
    """
    return templates.TemplateResponse("invoices_v2/facturas.html", {
        "request": request,
        "active_tab": "facturas"
    })
