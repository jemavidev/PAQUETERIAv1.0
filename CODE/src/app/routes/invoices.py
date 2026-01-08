# ========================================
# PAQUETES EL CLUB - Rutas de Facturas/CUFE
# ========================================

import os
import tempfile
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_active_user_from_cookies
from app.models.user import User
from app.utils.auth_context import get_auth_context_from_request
from app.services.invoice_service import InvoiceService
from app.services.pdf_extractor_service import PDFExtractorService
from app.schemas.invoice import (
    ExtractedInvoiceData,
    ExportableColumn,
    DEFAULT_EXPORT_COLUMNS,
    COLUMN_DISPLAY_NAMES,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/invoices", tags=["invoices"])
templates = Jinja2Templates(directory="/app/src/templates", auto_reload=True)


# ========================================
# Vistas HTML
# ========================================

@router.get("", response_class=HTMLResponse)
async def invoices_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Dashboard principal de facturas"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    service = InvoiceService(db)
    stats = service.get_dashboard_stats()
    suppliers = service.get_all_suppliers()
    
    context["stats"] = stats
    context["suppliers"] = suppliers
    context["export_columns"] = [
        {"value": col.value, "label": COLUMN_DISPLAY_NAMES[col]}
        for col in ExportableColumn
    ]
    context["default_columns"] = [col.value for col in DEFAULT_EXPORT_COLUMNS]
    
    return templates.TemplateResponse("invoices/dashboard.html", context)


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Página de carga de PDF"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    return templates.TemplateResponse("invoices/upload.html", context)


@router.get("/list", response_class=HTMLResponse)
async def invoices_list(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    page: int = 1,
    supplier: str = None,
    search: str = None,
):
    """Lista de facturas importadas"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    service = InvoiceService(db)
    invoices, total = service.get_invoices(
        page=page,
        per_page=20,
        supplier_nit=supplier,
        search=search,
    )
    
    suppliers = service.get_all_suppliers()
    
    context["invoices"] = invoices
    context["total"] = total
    context["page"] = page
    context["pages"] = (total + 19) // 20
    context["suppliers"] = suppliers
    context["current_supplier"] = supplier
    context["search"] = search or ""
    
    return templates.TemplateResponse("invoices/list.html", context)


@router.get("/detail/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail(
    invoice_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Detalle de una factura"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    service = InvoiceService(db)
    invoice = service.get_invoice(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    context["invoice"] = invoice
    return templates.TemplateResponse("invoices/detail.html", context)


# ========================================
# API Endpoints
# ========================================

@router.post("/api/extract")
async def extract_pdf(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """
    Extrae datos de un PDF sin guardar.
    Retorna los datos para revisión y corrección.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    # Guardar archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        extractor = PDFExtractorService()
        extracted, warnings = extractor.extract_from_pdf(tmp_path, file.filename)
        
        # Verificar duplicado
        service = InvoiceService(db)
        if extracted.cufe_cude and service.check_duplicate(extracted.cufe_cude):
            extracted.is_duplicate = True
            extracted.warnings.append({
                "field": "cufe_cude",
                "message": "Este documento ya fue importado anteriormente",
                "severity": "error"
            })
        
        return JSONResponse(content={
            "success": True,
            "data": extracted.model_dump(),
            "warnings": [w.model_dump() for w in warnings],
        })
        
    except Exception as e:
        logger.error(f"Error extrayendo PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")
    
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/api/save")
async def save_invoice(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Guarda una factura después de revisión"""
    try:
        data = await request.json()
        extracted_data = ExtractedInvoiceData(**data)
        
        service = InvoiceService(db)
        
        # Verificar duplicado
        if service.check_duplicate(extracted_data.cufe_cude):
            raise HTTPException(status_code=400, detail="Este documento ya fue importado")
        
        invoice = service.save_invoice(extracted_data, user_id=current_user.id)
        
        return JSONResponse(content={
            "success": True,
            "message": "Factura guardada exitosamente",
            "invoice_id": invoice.id,
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error guardando factura: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error guardando factura: {str(e)}")


@router.delete("/api/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Elimina una factura"""
    service = InvoiceService(db)
    
    if not service.delete_invoice(invoice_id):
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return JSONResponse(content={"success": True, "message": "Factura eliminada"})


@router.post("/api/export")
async def export_invoices(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Exporta facturas a CSV con columnas seleccionadas"""
    try:
        data = await request.json()
        
        # Parsear columnas
        columns = [ExportableColumn(c) for c in data.get('columns', [])]
        if not columns:
            columns = DEFAULT_EXPORT_COLUMNS
        
        service = InvoiceService(db)
        csv_content, row_count = service.export_to_csv(
            columns=columns,
            invoice_ids=data.get('invoice_ids'),
            supplier_nit=data.get('supplier_nit'),
            date_from=datetime.fromisoformat(data['date_from']) if data.get('date_from') else None,
            date_to=datetime.fromisoformat(data['date_to']) if data.get('date_to') else None,
            include_headers=data.get('include_headers', True),
        )
        
        # Retornar como archivo descargable
        filename = f"facturas_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Row-Count": str(row_count),
            }
        )
        
    except Exception as e:
        logger.error(f"Error exportando: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error exportando: {str(e)}")


# ========================================
# API de Análisis
# ========================================

@router.get("/api/product/{codigo}")
async def get_product_info(
    codigo: str,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene información y historial de precios de un producto"""
    service = InvoiceService(db)
    
    summary = service.get_product_summary(codigo)
    if not summary:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    history = service.get_product_price_history(codigo)
    
    return JSONResponse(content={
        "summary": summary.model_dump(),
        "price_history": history.model_dump() if history else None,
    })


@router.get("/api/supplier/{nit}")
async def get_supplier_info(
    nit: str,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene resumen de un proveedor"""
    service = InvoiceService(db)
    
    summary = service.get_supplier_summary(nit)
    if not summary:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    return JSONResponse(content=summary.model_dump())


@router.get("/api/search/products")
async def search_products(
    q: str = Query(..., min_length=2),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Busca productos por código o descripción"""
    service = InvoiceService(db)
    results = service.search_products(q)
    return JSONResponse(content={"results": results})


@router.get("/api/columns")
async def get_export_columns(
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Obtiene las columnas disponibles para exportación"""
    return JSONResponse(content={
        "columns": [
            {"value": col.value, "label": COLUMN_DISPLAY_NAMES[col]}
            for col in ExportableColumn
        ],
        "defaults": [col.value for col in DEFAULT_EXPORT_COLUMNS],
    })
