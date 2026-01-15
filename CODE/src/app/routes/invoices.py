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
    InvoiceSearchFilters,
    ImportStatusEnum,
    DocumentTypeEnum,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/invoices", tags=["invoices"])
templates = Jinja2Templates(directory="/app/src/templates", auto_reload=True)


# ========================================
# VISTAS HTML
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
    status: str = None,
    iva_filter: str = None,
    show_inactive: bool = False,
    fecha_desde: str = None,
    fecha_hasta: str = None,
    total_min: str = None,
    total_max: str = None,
    producto: str = None,
    doc_type: str = None,
    order_by: str = "fecha_emision",
    order_dir: str = "desc",
):
    """Lista de facturas importadas con filtros avanzados"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    # Convertir total_min y total_max a int si tienen valor
    total_min_int = None
    total_max_int = None
    if total_min and total_min.strip():
        try:
            total_min_int = int(total_min)
        except ValueError:
            pass
    if total_max and total_max.strip():
        try:
            total_max_int = int(total_max)
        except ValueError:
            pass
    service = InvoiceService(db)
    
    # Parsear fechas
    fecha_desde_dt = None
    fecha_hasta_dt = None
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.fromisoformat(fecha_desde)
        except:
            pass
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.fromisoformat(fecha_hasta)
        except:
            pass
    
    # Determinar filtro de IVA
    iva_incluido = None
    iva_desconocido = False
    if iva_filter == "incluido":
        iva_incluido = True
    elif iva_filter == "no_incluido":
        iva_incluido = False
    elif iva_filter == "desconocido":
        iva_desconocido = True
    
    # Construir filtros
    filters = InvoiceSearchFilters(
        query=search,
        supplier_nit=supplier,
        import_status=ImportStatusEnum(status) if status else None,
        is_active=None if show_inactive else True,
        fecha_desde=fecha_desde_dt,
        fecha_hasta=fecha_hasta_dt,
        total_min=total_min_int,
        total_max=total_max_int,
        producto_descripcion=producto,
        producto_codigo=producto,
        document_type=DocumentTypeEnum(doc_type) if doc_type else None,
        iva_incluido=iva_incluido,
        iva_desconocido=iva_desconocido,
        order_by=order_by,
        order_dir=order_dir,
        page=page,
        per_page=20,
    )
    
    invoices, total = service.search_invoices(filters)
    suppliers = service.get_all_suppliers()
    
    # Obtener nombre del proveedor actual
    current_supplier_name = None
    if supplier:
        for s in suppliers:
            if s.nit == supplier:
                current_supplier_name = s.razon_social
                break
    
    # Construir query string para paginación (sin page)
    query_params = []
    if search: query_params.append(f"search={search}")
    if supplier: query_params.append(f"supplier={supplier}")
    if status: query_params.append(f"status={status}")
    if iva_filter: query_params.append(f"iva_filter={iva_filter}")
    if fecha_desde: query_params.append(f"fecha_desde={fecha_desde}")
    if fecha_hasta: query_params.append(f"fecha_hasta={fecha_hasta}")
    if total_min_int: query_params.append(f"total_min={total_min_int}")
    if total_max_int: query_params.append(f"total_max={total_max_int}")
    if producto: query_params.append(f"producto={producto}")
    if doc_type: query_params.append(f"doc_type={doc_type}")
    if show_inactive: query_params.append("show_inactive=on")
    if order_by != "fecha_emision": query_params.append(f"order_by={order_by}")
    if order_dir != "desc": query_params.append(f"order_dir={order_dir}")
    
    # Calcular fechas para atajos
    from datetime import timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    context["invoices"] = invoices
    context["total"] = total
    context["page"] = page
    context["pages"] = (total + 19) // 20
    context["suppliers"] = suppliers
    context["current_supplier"] = supplier
    context["current_supplier_name"] = current_supplier_name
    context["search"] = search or ""
    context["current_status"] = status
    context["show_inactive"] = show_inactive
    context["iva_filter"] = iva_filter
    context["fecha_desde"] = fecha_desde
    context["fecha_hasta"] = fecha_hasta
    context["total_min"] = total_min_int
    context["total_max"] = total_max_int
    context["producto"] = producto
    context["doc_type"] = doc_type
    context["order_by"] = order_by
    context["order_dir"] = order_dir
    context["query_string"] = "&".join(query_params)
    context["today"] = today
    context["week_ago"] = week_ago
    context["month_ago"] = month_ago
    context["show_advanced"] = bool(fecha_desde or fecha_hasta or total_min_int or total_max_int or producto or doc_type or iva_filter)
    
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
    invoice = service.get_invoice(invoice_id, include_inactive=True)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Obtener irregularidades
    irregularities = service.get_invoice_irregularities(invoice_id)
    
    context["invoice"] = invoice
    context["irregularities"] = irregularities
    context["unresolved_count"] = sum(1 for i in irregularities if not i.resuelto)
    
    return templates.TemplateResponse("invoices/detail.html", context)


@router.get("/irregularities", response_class=HTMLResponse)
async def irregularities_list(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    page: int = 1,
    tipo: str = None,
    categoria: str = None,
    only_unresolved: bool = True,
):
    """Lista de irregularidades del sistema con categorías"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    # Mapear categorías a tipos
    categoria_map = {
        'criticas': ['cufe_invalido', 'nit_invalido', 'fecha_invalida'],
        'validacion': ['total_no_coincide', 'iva_inconsistente', 'cantidad_invalida'],
        'informacion': ['codigo_faltante', 'descripcion_vacia', 'precio_anomalo']
    }
    
    # Si se especifica categoría, filtrar por esos tipos
    if categoria and categoria in categoria_map:
        tipos_filtro = categoria_map[categoria]
        # Si también hay un tipo específico, usarlo
        if tipo and tipo in tipos_filtro:
            tipo_final = tipo
        else:
            tipo_final = None  # Se filtrará en el servicio
    else:
        tipo_final = tipo
        tipos_filtro = None
    
    service = InvoiceService(db)
    
    # Si hay categoría, obtener irregularidades de esos tipos
    if tipos_filtro:
        all_irregularities = []
        total_count = 0
        for t in tipos_filtro:
            irrs, count = service.get_all_irregularities(
                only_unresolved=only_unresolved,
                tipo=t,
                page=1,
                per_page=1000  # Obtener todas para luego paginar
            )
            all_irregularities.extend(irrs)
            total_count += count
        
        # Paginar manualmente
        start = (page - 1) * 50
        end = start + 50
        irregularities = all_irregularities[start:end]
        total = total_count
    else:
        irregularities, total = service.get_all_irregularities(
            only_unresolved=only_unresolved,
            tipo=tipo_final,
            page=page,
            per_page=50
        )
    
    context["irregularities"] = irregularities
    context["total"] = total
    context["page"] = page
    context["pages"] = (total + 49) // 50
    context["current_tipo"] = tipo
    context["current_categoria"] = categoria
    context["only_unresolved"] = only_unresolved
    
    return templates.TemplateResponse("invoices/irregularities.html", context)


@router.get("/rejected", response_class=HTMLResponse)
async def rejected_files_list(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    page: int = 1,
):
    """Lista de archivos rechazados"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    service = InvoiceService(db)
    files, total = service.get_rejected_files(page=page, per_page=20)
    
    context["rejected_files"] = files
    context["total"] = total
    context["page"] = page
    context["pages"] = (total + 19) // 20
    
    return templates.TemplateResponse("invoices/rejected.html", context)


@router.get("/products", response_class=HTMLResponse)
async def products_search_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    q: str = None,
    iva_status: str = None,
):
    """Página de búsqueda global de productos"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    service = InvoiceService(db)
    
    products = []
    if q:
        products = service.search_products_global(q, limit=100)
    elif iva_status:
        iva_incluido = True if iva_status == "incluido" else (False if iva_status == "no_incluido" else None)
        products = service.get_products_by_iva_status(iva_incluido)
    
    context["products"] = products
    context["search_query"] = q or ""
    context["iva_status"] = iva_status
    
    return templates.TemplateResponse("invoices/products.html", context)


# ========================================
# API ENDPOINTS - CRUD
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
    Guarda el PDF en el servidor para poder re-procesarlo después.
    """
    if not file.filename.lower().endswith('.pdf'):
        # Guardar como archivo rechazado
        service = InvoiceService(db)
        content = await file.read()
        service.save_rejected_file(
            archivo_nombre=file.filename,
            razon_rechazo="Formato de archivo no soportado. Solo se permiten archivos PDF.",
            detalles_error={"tipo": "formato_invalido", "extension": file.filename.split('.')[-1]},
            file_content=content,
            user_id=current_user.id,
            puede_reintentar=False
        )
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    # Guardar archivo temporal
    content = await file.read()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        extractor = PDFExtractorService()
        extracted, warnings = extractor.extract_from_pdf(tmp_path, file.filename)
        
        # Calcular hash del archivo
        service = InvoiceService(db)
        file_hash = service.calculate_file_hash(content)
        extracted.file_hash = file_hash
        
        # Guardar PDF (S3 o localmente según configuración)
        metadata = {
            'filename': file.filename,
            'cufe_cude': extracted.cufe_cude if extracted.cufe_cude else 'unknown',
            'document_type': extracted.document_type if extracted.document_type else 'unknown'
        }
        service.save_pdf(content, file_hash, metadata)
        
        # Verificar duplicado por CUFE (activas e inactivas)
        if extracted.cufe_cude:
            existing_active = service.check_duplicate(extracted.cufe_cude)
            existing_any = service.check_duplicate_any(extracted.cufe_cude)
            
            if existing_active:
                extracted.is_duplicate = True
                extracted.warnings.append({
                    "field": "cufe_cude",
                    "message": f"Este documento ya fue importado (Factura #{existing_active.id})",
                    "severity": "error",
                    "tipo": "duplicado"
                })
            elif existing_any:
                # Hay una factura inactiva - se puede restaurar
                extracted.is_duplicate = True
                extracted.can_restore = True
                extracted.warnings.append({
                    "field": "cufe_cude",
                    "message": f"Este documento fue importado anteriormente pero está inactivo (Factura #{existing_any.id}). Se restaurará automáticamente al guardar.",
                    "severity": "warning",
                    "tipo": "duplicado_inactivo"
                })
        
        # Verificar duplicado por hash
        existing_hash = service.check_file_hash(file_hash)
        if existing_hash and not extracted.is_duplicate:
            extracted.warnings.append({
                "field": "archivo",
                "message": f"Este archivo ya fue procesado anteriormente (Factura #{existing_hash.id})",
                "severity": "warning",
                "tipo": "archivo_duplicado"
            })
        
        # Validar datos y detectar irregularidades
        is_valid, irregularities = service.validate_invoice_data(extracted)
        extracted.is_valid = is_valid
        extracted.irregularities = irregularities
        
        return JSONResponse(content={
            "success": True,
            "data": extracted.model_dump(),
            "warnings": [w.model_dump() if hasattr(w, 'model_dump') else w for w in warnings],
            "irregularities": irregularities,
            "is_valid": is_valid,
        })
        
    except Exception as e:
        logger.error(f"Error extrayendo PDF: {e}", exc_info=True)
        
        # Guardar como archivo rechazado
        service = InvoiceService(db)
        service.save_rejected_file(
            archivo_nombre=file.filename,
            razon_rechazo=f"Error procesando archivo: {str(e)}",
            detalles_error={"tipo": "error_extraccion", "error": str(e)},
            file_content=content,
            user_id=current_user.id,
            puede_reintentar=True
        )
        
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
        replace_existing = data.pop('replace_existing', False)
        extracted_data = ExtractedInvoiceData(**data)
        
        service = InvoiceService(db)
        
        # Verificar duplicado si no se va a reemplazar
        if not replace_existing and extracted_data.cufe_cude:
            existing = service.check_duplicate(extracted_data.cufe_cude)
            if existing:
                return JSONResponse(
                    status_code=409,
                    content={
                        "success": False,
                        "error": "duplicate",
                        "message": f"Este documento ya fue importado (Factura #{existing.id})",
                        "existing_id": existing.id,
                        "existing_numero": existing.numero_documento,
                        "can_replace": True
                    }
                )
        
        invoice = service.save_invoice(
            extracted_data, 
            user_id=current_user.id,
            replace_existing=replace_existing
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "Factura guardada exitosamente",
            "invoice_id": invoice.id,
            "import_status": invoice.import_status,
            "replaced": replace_existing,
        })
        
    except HTTPException:
        raise
    except ValueError as e:
        # Error de validación (ej: duplicado detectado por el servicio)
        error_msg = str(e)
        if "CUFE" in error_msg or "duplicado" in error_msg.lower():
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "error": "duplicate",
                    "message": error_msg,
                    "can_replace": True
                }
            )
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        error_msg = str(e)
        # Capturar error de duplicado de la base de datos
        if "UniqueViolation" in error_msg or "duplicate key" in error_msg.lower():
            logger.warning(f"Intento de guardar factura duplicada: {error_msg}")
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "error": "duplicate",
                    "message": "Este documento ya existe en el sistema. Use la opción de reemplazar si desea actualizar.",
                    "can_replace": True
                }
            )
        logger.error(f"Error guardando factura: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error guardando factura: {error_msg}")


@router.delete("/api/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    hard_delete: bool = False,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Elimina una factura (soft delete por defecto)"""
    service = InvoiceService(db)
    
    if not service.delete_invoice(invoice_id, hard_delete=hard_delete):
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return JSONResponse(content={
        "success": True, 
        "message": "Factura eliminada permanentemente" if hard_delete else "Factura desactivada"
    })


@router.post("/api/{invoice_id}/restore")
async def restore_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Restaura una factura eliminada"""
    service = InvoiceService(db)
    
    if not service.restore_invoice(invoice_id):
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return JSONResponse(content={"success": True, "message": "Factura restaurada"})


# ========================================
# API ENDPOINTS - IRREGULARIDADES
# ========================================

@router.post("/api/irregularity/{irregularity_id}/resolve")
async def resolve_irregularity(
    irregularity_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Resuelve una irregularidad"""
    try:
        data = await request.json()
        service = InvoiceService(db)
        
        if not service.resolve_irregularity(
            irregularity_id,
            user_id=current_user.id,
            notas=data.get('notas'),
            accion=data.get('accion', 'ignorar')
        ):
            raise HTTPException(status_code=404, detail="Irregularidad no encontrada")
        
        return JSONResponse(content={"success": True, "message": "Irregularidad resuelta"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolviendo irregularidad: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/rejected/{file_id}")
async def delete_rejected_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Elimina un registro de archivo rechazado"""
    service = InvoiceService(db)
    
    if not service.delete_rejected_file(file_id):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    return JSONResponse(content={"success": True, "message": "Registro eliminado"})


# ========================================
# API ENDPOINTS - IVA
# ========================================

@router.post("/api/item/{item_id}/iva")
async def update_item_iva(
    item_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Actualiza el estado de IVA de un item"""
    try:
        data = await request.json()
        iva_incluido = data.get('iva_incluido')  # True, False, or None
        
        service = InvoiceService(db)
        if not service.update_item_iva_status(item_id, iva_incluido):
            raise HTTPException(status_code=404, detail="Item no encontrado")
        
        return JSONResponse(content={"success": True, "message": "Estado de IVA actualizado"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando IVA: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/items/iva/bulk")
async def bulk_update_iva(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Actualiza el estado de IVA de múltiples items"""
    try:
        data = await request.json()
        item_ids = data.get('item_ids', [])
        iva_incluido = data.get('iva_incluido')
        
        service = InvoiceService(db)
        count = service.bulk_update_iva_status(item_ids, iva_incluido)
        
        return JSONResponse(content={
            "success": True, 
            "message": f"{count} items actualizados",
            "updated_count": count
        })
    except Exception as e:
        logger.error(f"Error actualizando IVA masivo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# API ENDPOINTS - EXPORTACIÓN
# ========================================

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
            only_active=data.get('only_active', True),
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
# API ENDPOINTS - ANÁLISIS Y BÚSQUEDA
# ========================================

@router.get("/api/search")
async def search_invoices_api(
    request: Request,
    q: str = Query(None),
    supplier_nit: str = Query(None),
    fecha_desde: str = Query(None),
    fecha_hasta: str = Query(None),
    status: str = Query(None),
    page: int = Query(1),
    per_page: int = Query(20),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """API de búsqueda avanzada de facturas"""
    service = InvoiceService(db)
    
    filters = InvoiceSearchFilters(
        query=q,
        supplier_nit=supplier_nit,
        fecha_desde=datetime.fromisoformat(fecha_desde) if fecha_desde else None,
        fecha_hasta=datetime.fromisoformat(fecha_hasta) if fecha_hasta else None,
        import_status=ImportStatusEnum(status) if status else None,
        page=page,
        per_page=per_page,
    )
    
    invoices, total = service.search_invoices(filters)
    
    return JSONResponse(content={
        "invoices": [
            {
                "id": inv.id,
                "numero_documento": inv.numero_documento,
                "document_type": inv.document_type.value,
                "fecha_emision": inv.fecha_emision.isoformat() if inv.fecha_emision else None,
                "supplier_razon_social": inv.supplier.razon_social,
                "supplier_nit": inv.supplier.nit,
                "total_neto": inv.total_neto,
                "total_iva": inv.total_iva,
                "items_count": len(inv.items),
                "import_status": inv.import_status,
                "is_active": inv.is_active,
            }
            for inv in invoices
        ],
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page,
    })


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
    """Busca productos por código o descripción (búsqueda global)"""
    service = InvoiceService(db)
    results = service.search_products_global(q)
    return JSONResponse(content={"results": results})


@router.get("/api/search/products/invoice/{invoice_id}")
async def search_products_in_invoice(
    invoice_id: int,
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Busca productos dentro de una factura específica (búsqueda local)"""
    service = InvoiceService(db)
    items = service.search_products_in_invoice(invoice_id, q)
    
    return JSONResponse(content={
        "results": [
            {
                "id": item.id,
                "codigo": item.codigo,
                "descripcion": item.descripcion,
                "cantidad": item.cantidad,
                "precio_unitario": item.precio_unitario,
                "iva_porcentaje": item.iva_porcentaje,
                "iva_incluido": item.iva_incluido,
                "valor_total": item.valor_total,
            }
            for item in items
        ]
    })


@router.get("/api/products/iva")
async def get_products_by_iva(
    status: str = Query(None),  # "incluido", "no_incluido", "desconocido"
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene productos filtrados por estado de IVA"""
    service = InvoiceService(db)
    
    iva_incluido = None
    if status == "incluido":
        iva_incluido = True
    elif status == "no_incluido":
        iva_incluido = False
    # None para "desconocido"
    
    products = service.get_products_by_iva_status(iva_incluido)
    return JSONResponse(content={"products": products})


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


@router.get("/api/stats")
async def get_stats(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene estadísticas del dashboard"""
    service = InvoiceService(db)
    stats = service.get_dashboard_stats()
    
    # Serializar facturas recientes
    stats['recent_invoices'] = [
        {
            "id": inv.id,
            "numero_documento": inv.numero_documento,
            "supplier_razon_social": inv.supplier.razon_social,
            "total_neto": inv.total_neto,
            "fecha_emision": inv.fecha_emision.isoformat() if inv.fecha_emision else None,
        }
        for inv in stats['recent_invoices']
    ]
    
    return JSONResponse(content=stats)


# ========================================
# API ENDPOINTS - RE-PROCESAMIENTO
# ========================================

@router.post("/api/{invoice_id}/reprocess")
async def reprocess_invoice(
    invoice_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """
    Re-procesa una factura desde su archivo PDF original.
    Útil para corregir errores de extracción.
    """
    try:
        service = InvoiceService(db)
        invoice = service.get_invoice(invoice_id, include_inactive=True)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        
        if not invoice.file_hash:
            raise HTTPException(status_code=400, detail="Esta factura no tiene archivo asociado")
        
        # Obtener PDF desde S3 o localmente
        pdf_content = service.get_pdf(invoice.file_hash)
        
        if not pdf_content:
            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")
        
        # Guardar temporalmente para re-procesar
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_content)
            tmp_path = tmp.name
        
        try:
            success = service.reprocess_invoice_from_file(invoice_id, tmp_path)
            
            if success:
                return JSONResponse(content={
                    "success": True,
                    "message": "Factura re-procesada exitosamente",
                    "invoice_id": invoice_id
                })
            else:
                raise HTTPException(status_code=500, detail="Error re-procesando la factura")
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reprocess_invoice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/reprocess-all-errors")
async def reprocess_all_with_errors(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """
    Re-procesa todas las facturas que tienen irregularidades de totales.
    Solo para administradores.
    """
    try:
        # Verificar que el usuario sea admin (puedes agregar esta validación)
        # if not current_user.is_admin:
        #     raise HTTPException(status_code=403, detail="Solo administradores")
        
        service = InvoiceService(db)
        pdf_directory = "/app/src/uploads/invoices"
        
        results = service.reprocess_all_invoices_with_errors(pdf_directory)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Re-procesamiento completado",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error en reprocess_all_with_errors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# API ENDPOINTS - DESCARGA DE PDFs
# ========================================

@router.get("/api/{invoice_id}/download-pdf")
async def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Descarga el PDF original de una factura"""
    try:
        service = InvoiceService(db)
        invoice = service.get_invoice(invoice_id, include_inactive=True)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        
        if not invoice.file_hash:
            raise HTTPException(status_code=400, detail="Esta factura no tiene archivo asociado")
        
        # Obtener PDF desde S3 o localmente
        pdf_content = service.get_pdf(invoice.file_hash)
        
        if not pdf_content:
            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")
        
        # Retornar como descarga
        filename = invoice.archivo_nombre or f"factura_{invoice.numero_documento}.pdf"
        
        return StreamingResponse(
            iter([pdf_content]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error descargando PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/{invoice_id}/view-pdf")
async def view_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Visualiza el PDF de una factura en el navegador"""
    try:
        service = InvoiceService(db)
        invoice = service.get_invoice(invoice_id, include_inactive=True)
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        
        if not invoice.file_hash:
            raise HTTPException(status_code=400, detail="Esta factura no tiene archivo asociado")
        
        # Si S3 está habilitado, generar URL firmada
        if service.s3_service.is_enabled():
            url = service.s3_service.generate_presigned_url(invoice.file_hash, expiration=3600)
            if url:
                return JSONResponse(content={"url": url, "type": "presigned"})
        
        # Fallback: obtener PDF y retornarlo
        pdf_content = service.get_pdf(invoice.file_hash)
        
        if not pdf_content:
            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")
        
        return StreamingResponse(
            iter([pdf_content]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error visualizando PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# CUFE IMPORT - Importación desde DIAN
# ========================================

from app.services.dian_cufe_service import get_cufe_service, CufeStatus


@router.get("/cufe-import", response_class=HTMLResponse)
async def cufe_import_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Página de importación de facturas desde DIAN por CUFE"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    return templates.TemplateResponse("invoices/cufe_import.html", context)


@router.post("/api/cufe/init")
async def init_cufe_import(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Inicializa una sesión de importación de CUFEs"""
    try:
        data = await request.json()
        cufes = data.get('cufes', [])
        
        if not cufes:
            return JSONResponse(content={"success": False, "message": "No se proporcionaron CUFEs"})
        
        service = get_cufe_service()
        service.clear_tasks()  # Limpiar tareas anteriores
        
        created = []
        for cufe in cufes:
            task = service.create_task(cufe)
            created.append(task.to_dict())
        
        return JSONResponse(content={
            "success": True,
            "message": f"{len(created)} CUFEs inicializados",
            "tasks": created,
            "stats": service.get_stats()
        })
        
    except Exception as e:
        logger.error(f"Error inicializando CUFEs: {e}", exc_info=True)
        return JSONResponse(content={"success": False, "message": str(e)})


@router.post("/api/cufe/update")
async def update_cufe_status(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Actualiza el estado de un CUFE"""
    try:
        data = await request.json()
        cufe = data.get('cufe')
        status = data.get('status')
        
        if not cufe or not status:
            return JSONResponse(content={"success": False, "message": "Faltan parámetros"})
        
        service = get_cufe_service()
        
        try:
            cufe_status = CufeStatus(status)
        except ValueError:
            return JSONResponse(content={"success": False, "message": f"Estado inválido: {status}"})
        
        task = service.update_task_status(
            cufe=cufe,
            status=cufe_status,
            error_message=data.get('error_message'),
            invoice_id=data.get('invoice_id'),
            invoice_number=data.get('invoice_number'),
            supplier_name=data.get('supplier_name'),
            total=data.get('total')
        )
        
        if not task:
            return JSONResponse(content={"success": False, "message": "CUFE no encontrado"})
        
        return JSONResponse(content={
            "success": True,
            "task": task.to_dict(),
            "stats": service.get_stats()
        })
        
    except Exception as e:
        logger.error(f"Error actualizando CUFE: {e}", exc_info=True)
        return JSONResponse(content={"success": False, "message": str(e)})


@router.get("/api/cufe/status")
async def get_cufe_import_status(
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Obtiene el estado actual de la importación de CUFEs"""
    service = get_cufe_service()
    
    return JSONResponse(content={
        "tasks": [t.to_dict() for t in service.get_all_tasks()],
        "stats": service.get_stats()
    })


@router.get("/api/cufe/dian-url/{cufe}")
async def get_dian_url(
    cufe: str,
    current_user: User = Depends(get_current_active_user_from_cookies),
):
    """Genera la URL de búsqueda en la DIAN para un CUFE"""
    service = get_cufe_service()
    
    is_valid, result = service.validate_cufe(cufe)
    if not is_valid:
        return JSONResponse(content={"success": False, "message": result})
    
    url = service.get_dian_search_url(result)
    
    return JSONResponse(content={
        "success": True,
        "url": url,
        "cufe": result
    })



# ========================================
# SUPPLIER INVOICES - Facturas de Proveedores
# ========================================

from app.services.supplier_invoice_service import SupplierInvoiceService
from app.models.invoice import SupplierInvoiceStatus


@router.get("/supplier-invoices", response_class=HTMLResponse)
async def supplier_invoices_page(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    page: int = 1,
    status: str = None,
):
    """Página de gestión de facturas de proveedores"""
    context = get_auth_context_from_request(request)
    context["user"] = current_user
    
    service = SupplierInvoiceService(db)
    
    # Convertir status string a enum
    status_enum = None
    if status:
        try:
            status_enum = SupplierInvoiceStatus(status)
        except ValueError:
            pass
    
    invoices, total = service.get_all(status=status_enum, page=page, per_page=50)
    stats = service.get_stats()
    
    context["invoices"] = invoices
    context["total"] = total
    context["page"] = page
    context["pages"] = (total + 49) // 50
    context["stats"] = stats
    context["current_status"] = status
    
    return templates.TemplateResponse("invoices/supplier_invoices.html", context)


@router.post("/api/supplier-invoices/upload")
async def upload_supplier_invoice(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Sube una factura de proveedor y extrae el CUFE"""
    from app.services.s3_storage_service import S3StorageService
    
    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(content={
            "success": False,
            "message": "Solo se permiten archivos PDF"
        })
    
    content = await file.read()
    
    # Guardar temporalmente para procesar
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = SupplierInvoiceService(db)
        invoice, info = service.process_uploaded_file(
            filename=file.filename,
            content=content,
            pdf_path=tmp_path,
            user_id=current_user.id
        )
        
        # Guardar PDF en S3
        s3_service = S3StorageService()
        if s3_service.is_enabled() and invoice.original_file_hash:
            metadata = {
                'type': 'supplier_invoice',
                'filename': file.filename,
                'supplier_invoice_id': str(invoice.id),
                'cufe': invoice.cufe or '',
            }
            s3_key = f"supplier-invoices/{invoice.original_file_hash}.pdf"
            if s3_service.upload_pdf(content, f"supplier-invoices/{invoice.original_file_hash}", metadata):
                # Guardar la ruta en el modelo
                invoice.original_file_path = s3_key
                db.commit()
                logger.info(f"PDF de proveedor guardado en S3: {s3_key}")
        
        return JSONResponse(content={
            "success": True,
            "invoice_id": invoice.id,
            "cufe_found": info['cufe_found'],
            "cufe_source": info['cufe_source'],
            "is_duplicate": info['is_duplicate'],
            "warnings": info['warnings'],
        })
        
    except Exception as e:
        logger.error(f"Error procesando factura de proveedor: {e}", exc_info=True)
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        })
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/api/supplier-invoices/{invoice_id}/pdf")
async def get_supplier_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene el PDF original de una factura de proveedor"""
    from app.services.s3_storage_service import S3StorageService
    
    service = SupplierInvoiceService(db)
    invoice = service.get_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    if not invoice.original_file_hash:
        raise HTTPException(status_code=404, detail="PDF no disponible")
    
    s3_service = S3StorageService()
    
    # Intentar obtener URL firmada de S3
    if s3_service.is_enabled():
        url = s3_service.generate_presigned_url(f"supplier-invoices/{invoice.original_file_hash}", expiration=3600)
        if url:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=url)
    
    # Fallback: buscar localmente
    local_path = f"/app/src/uploads/invoices/{invoice.original_file_hash}.pdf"
    if os.path.exists(local_path):
        with open(local_path, 'rb') as f:
            content = f.read()
        return StreamingResponse(
            iter([content]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={invoice.original_filename}"}
        )
    
    raise HTTPException(status_code=404, detail="PDF no encontrado en S3 ni localmente")


@router.post("/api/supplier-invoices/{invoice_id}/cufe")
async def update_supplier_invoice_cufe(
    invoice_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Actualiza el CUFE de una factura de proveedor manualmente"""
    try:
        data = await request.json()
        cufe = data.get('cufe', '').strip()
        
        service = SupplierInvoiceService(db)
        success, message = service.update_cufe(invoice_id, cufe, source='manual')
        
        return JSONResponse(content={
            "success": success,
            "message": message
        })
    except Exception as e:
        logger.error(f"Error actualizando CUFE: {e}", exc_info=True)
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        })


@router.get("/api/supplier-invoices/pending-cufes")
async def get_pending_cufes(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene lista de CUFEs pendientes para procesar en DIAN"""
    service = SupplierInvoiceService(db)
    cufes = service.get_cufes_for_dian()
    
    return JSONResponse(content={"cufes": cufes})


@router.post("/api/supplier-invoices/{invoice_id}/mark-downloaded")
async def mark_dian_downloaded(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Marca una factura como descargada de DIAN"""
    service = SupplierInvoiceService(db)
    invoice = service.mark_dian_downloaded(invoice_id)
    
    if not invoice:
        return JSONResponse(content={"success": False, "message": "Factura no encontrada"})
    
    return JSONResponse(content={"success": True})


@router.post("/api/supplier-invoices/{invoice_id}/mark-processed")
async def mark_processed(
    invoice_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Marca una factura como procesada"""
    try:
        data = await request.json()
        processed_invoice_id = data.get('processed_invoice_id')
        
        service = SupplierInvoiceService(db)
        invoice = service.mark_processed(invoice_id, processed_invoice_id)
        
        if not invoice:
            return JSONResponse(content={"success": False, "message": "Factura no encontrada"})
        
        return JSONResponse(content={"success": True})
    except Exception as e:
        logger.error(f"Error marcando como procesada: {e}", exc_info=True)
        return JSONResponse(content={"success": False, "message": str(e)})


@router.delete("/api/supplier-invoices/{invoice_id}")
async def delete_supplier_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Elimina una factura de proveedor"""
    service = SupplierInvoiceService(db)
    
    if not service.delete(invoice_id):
        return JSONResponse(content={"success": False, "message": "Factura no encontrada"})
    
    return JSONResponse(content={"success": True})
