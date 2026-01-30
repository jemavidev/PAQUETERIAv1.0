# ========================================
# PAQUETES EL CLUB - Rutas de Facturas/CUFE
# VERSIÓN MOCKUP - Solo interfaz visual sin lógica de backend
# ========================================

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_current_active_user_from_cookies
from app.models.user import User
from app.utils.auth_context import get_auth_context_from_request

router = APIRouter()
templates = Jinja2Templates(directory="/app/src/templates", auto_reload=True)


# ========================================
# VISTAS HTML - MOCKUP
# ========================================

@router.get("", response_class=HTMLResponse)
async def invoices_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Dashboard principal de facturas - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    # Datos estáticos de ejemplo
    context["stats"] = {
        "total_facturas": 6,
        "procesadas": 0,
        "pendientes": 5,
        "total_valor": 0
    }
    
    context["suppliers"] = [
        {"id": 1, "nit": "900123456", "razon_social": "AUTORIZACIÓN NUMERACIÓN DE FACTURACIÓN"},
        {"id": 2, "nit": "900654321", "razon_social": "DIRECCION CL 31 42 11 P 1 BARRANQUILLA"},
        {"id": 3, "nit": "900111222", "razon_social": "RIAL S A"},
    ]
    
    context["export_columns"] = [
        {"value": "proveedor", "label": "Proveedor"},
        {"value": "fecha", "label": "Fecha"},
        {"value": "numero", "label": "Número"},
        {"value": "cufe", "label": "CUFE"},
        {"value": "total", "label": "Total"},
    ]
    context["default_columns"] = ["proveedor", "fecha", "numero", "cufe"]
    
    return templates.TemplateResponse("invoices/dashboard.html", context)


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Página de carga de PDF - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    return templates.TemplateResponse("invoices/upload.html", context)


@router.get("/list", response_class=HTMLResponse)
async def invoices_list(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Lista de facturas - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    # Datos de ejemplo
    context["invoices"] = [
        {
            "id": 1,
            "proveedor": "AUTORIZACIÓN NUMERACIÓN DE FACTURACIÓN",
            "fecha": "18/10/2025",
            "numero": "ELECTR",
            "cufe": "BRF545e4a155619...",
            "estado": "CUFE ✓",
            "total": "$0"
        },
        {
            "id": 2,
            "proveedor": "AUTORIZACIÓN NUMERACIÓN DE FACTURACIÓN",
            "fecha": "30/08/2025",
            "numero": "ELECTR",
            "cufe": "468e25d8772687...",
            "estado": "CUFE ✓",
            "total": "$0"
        },
        {
            "id": 3,
            "proveedor": "DIRECCION CL 31 42 11 P 1 BARRANQUILLA",
            "fecha": "11/11/2025",
            "numero": "ELECTRONICA",
            "cufe": "CUFE ✗",
            "estado": "CUFE ✗",
            "total": "$0"
        },
        {
            "id": 4,
            "proveedor": "RIAL S A",
            "fecha": "24/07/2025",
            "numero": "ELECTRONICA",
            "cufe": "9a882208275f54c8...",
            "estado": "CUFE ✓",
            "total": "$0"
        },
        {
            "id": 5,
            "proveedor": "RIAL S A",
            "fecha": "24/07/2025",
            "numero": "ELECTRONICA",
            "cufe": "6ee372e238cc82c...",
            "estado": "CUFE ✓",
            "total": "$0"
        },
        {
            "id": 6,
            "proveedor": "RIAL S A",
            "fecha": "11/07/2025",
            "numero": "CION",
            "cufe": "4f2d6e9624794065...",
            "estado": "CUFE ✓",
            "total": "$0"
        },
    ]
    
    context["total_pages"] = 1
    context["current_page"] = 1
    context["total_count"] = 6
    
    return templates.TemplateResponse("invoices/list.html", context)


@router.get("/detail/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail(
    invoice_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Detalle de factura - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    # Datos de ejemplo
    context["invoice"] = {
        "id": invoice_id,
        "numero_documento": "ELECTR-001",
        "fecha_emision": "18/10/2025",
        "proveedor": "AUTORIZACIÓN NUMERACIÓN DE FACTURACIÓN",
        "cufe": "BRF545e4a155619...",
        "total_neto": 0,
        "items": []
    }
    
    return templates.TemplateResponse("invoices/detail.html", context)


@router.get("/irregularities", response_class=HTMLResponse)
async def irregularities_list(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Lista de irregularidades - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    context["irregularities"] = []
    return templates.TemplateResponse("invoices/irregularities.html", context)


@router.get("/rejected", response_class=HTMLResponse)
async def rejected_files_list(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Lista de archivos rechazados - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    context["rejected_files"] = []
    return templates.TemplateResponse("invoices/rejected.html", context)


@router.get("/products", response_class=HTMLResponse)
async def products_search_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Página de búsqueda de productos - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    return templates.TemplateResponse("invoices/products.html", context)


@router.get("/cufe-import", response_class=HTMLResponse)
async def cufe_import_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Página de importación de CUFE - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    return templates.TemplateResponse("invoices/cufe_import.html", context)


@router.get("/supplier-invoices", response_class=HTMLResponse)
async def supplier_invoices_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Página de facturas de proveedores - MOCKUP"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    context["stats"] = {
        "total": 0,
        "pending": 0,
        "processed": 0,
        "errors": 0
    }
    
    context["invoices"] = []
    
    return templates.TemplateResponse("invoices/supplier_invoices.html", context)


# ========================================
# API ENDPOINTS - MOCKUP (respuestas vacías)
# ========================================

@router.get("/api/stats")
async def get_stats(
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Stats API - MOCKUP"""
    return {
        "success": True,
        "data": {
            "total_facturas": 6,
            "procesadas": 0,
            "pendientes": 5,
            "total_valor": 0
        }
    }


@router.get("/api/search")
async def search_invoices_api(
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Search API - MOCKUP"""
    return {
        "success": True,
        "data": [],
        "total": 0
    }


@router.post("/api/extract")
async def extract_pdf(
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Extract PDF API - MOCKUP"""
    return {
        "success": False,
        "message": "Esta funcionalidad está deshabilitada (solo mockup visual)"
    }


@router.post("/api/save")
async def save_invoice(
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Save invoice API - MOCKUP"""
    return {
        "success": False,
        "message": "Esta funcionalidad está deshabilitada (solo mockup visual)"
    }


# Todas las demás rutas API retornan respuesta mockup
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all_api(
    path: str,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Catch-all para todas las rutas API - MOCKUP"""
    return {
        "success": False,
        "message": "Esta funcionalidad está deshabilitada (solo mockup visual)"
    }
