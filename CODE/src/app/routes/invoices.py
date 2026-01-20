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
router = APIRouter()
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
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Sube una o múltiples facturas de proveedor y extrae el CUFE"""
    from app.services.s3_storage_service import S3StorageService
    
    results = []
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            results.append({
                "filename": file.filename,
                "success": False,
                "message": "Solo se permiten archivos PDF"
            })
            continue
        
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
                
                # Construir la key completa para S3
                s3_key = f"supplier-invoices/{invoice.original_file_hash}.pdf"
                
                # Subir directamente con put_object para tener control total de la key
                try:
                    s3_service.s3_client.put_object(
                        Bucket=s3_service.bucket_name,
                        Key=s3_key,
                        Body=content,
                        ContentType='application/pdf',
                        Metadata=metadata,
                        ServerSideEncryption='AES256',
                    )
                    # Guardar la ruta en el modelo
                    invoice.original_file_path = s3_key
                    db.commit()
                    logger.info(f"PDF de proveedor guardado en S3: {s3_key}")
                except Exception as e:
                    logger.error(f"Error guardando PDF en S3: {e}")
                    # Intentar guardar localmente como fallback
                    local_dir = "/app/src/uploads/supplier-invoices"
                    os.makedirs(local_dir, exist_ok=True)
                    local_path = f"{local_dir}/{invoice.original_file_hash}.pdf"
                    with open(local_path, 'wb') as f:
                        f.write(content)
                    logger.info(f"PDF guardado localmente: {local_path}")
            
            results.append({
                "filename": file.filename,
                "success": True,
                "invoice_id": invoice.id,
                "cufe_found": info['cufe_found'],
                "cufe_source": info['cufe_source'],
                "is_duplicate": info['is_duplicate'],
                "warnings": info['warnings'],
            })
            
        except Exception as e:
            logger.error(f"Error procesando {file.filename}: {e}", exc_info=True)
            results.append({
                "filename": file.filename,
                "success": False,
                "message": str(e)
            })
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    # Retornar resumen
    success_count = sum(1 for r in results if r['success'])
    return JSONResponse(content={
        "success": success_count > 0,
        "total": len(files),
        "uploaded": success_count,
        "failed": len(files) - success_count,
        "results": results
    })


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
    
    # Intentar obtener desde S3 - Descargar y servir directamente (evita problemas de CORS)
    if s3_service.is_enabled():
        # Opción 1: Usar la ruta guardada en original_file_path si existe
        s3_key = invoice.original_file_path or f"supplier-invoices/{invoice.original_file_hash}.pdf"
        
        try:
            # Descargar desde S3
            pdf_content = s3_service.download_pdf(invoice.original_file_hash, prefix="supplier-invoices")
            if pdf_content:
                logger.info(f"PDF descargado desde S3: {s3_key}")
                return StreamingResponse(
                    iter([pdf_content]),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f"inline; filename={invoice.original_filename}",
                        "Cache-Control": "public, max-age=3600"
                    }
                )
        except Exception as e:
            logger.error(f"Error descargando PDF desde S3: {e}")
    
    # Fallback: buscar localmente en carpeta supplier-invoices
    local_path = f"/app/src/uploads/supplier-invoices/{invoice.original_file_hash}.pdf"
    if os.path.exists(local_path):
        logger.info(f"PDF encontrado localmente: {local_path}")
        with open(local_path, 'rb') as f:
            content = f.read()
        return StreamingResponse(
            iter([content]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={invoice.original_filename}"}
        )
    
    # Fallback 2: buscar en carpeta invoices (por compatibilidad)
    local_path_alt = f"/app/src/uploads/invoices/{invoice.original_file_hash}.pdf"
    if os.path.exists(local_path_alt):
        logger.info(f"PDF encontrado en carpeta alternativa: {local_path_alt}")
        with open(local_path_alt, 'rb') as f:
            content = f.read()
        return StreamingResponse(
            iter([content]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename={invoice.original_filename}"}
        )
    
    logger.error(f"PDF no encontrado para supplier_invoice {invoice_id} (hash: {invoice.original_file_hash})")
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


# ========================================
# API ENDPOINTS - DASHBOARD TABS
# ========================================

@router.get("/api/supplier-invoices/stats")
async def get_supplier_invoices_stats(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene estadísticas de facturas de proveedores para el dashboard"""
    try:
        from app.models.invoice import SupplierInvoice, SupplierInvoiceStatus, Invoice
        from sqlalchemy import func
        
        total = db.query(func.count(SupplierInvoice.id)).scalar() or 0
        processed = db.query(func.count(SupplierInvoice.id)).filter(
            SupplierInvoice.status == SupplierInvoiceStatus.PROCESSED
        ).scalar() or 0
        pending = db.query(func.count(SupplierInvoice.id)).filter(
            SupplierInvoice.status.in_([SupplierInvoiceStatus.PENDING, SupplierInvoiceStatus.CUFE_EXTRACTED])
        ).scalar() or 0
        
        # Calcular valor total (de las procesadas que tienen processed_invoice_id)
        total_value_raw = db.query(func.sum(Invoice.total_neto)).filter(
            Invoice.id.in_(
                db.query(SupplierInvoice.processed_invoice_id).filter(
                    SupplierInvoice.processed_invoice_id.isnot(None)
                )
            )
        ).scalar()
        
        total_value = int(total_value_raw) if total_value_raw else 0
        
        return JSONResponse(content={
            "total": total,
            "processed": processed,
            "pending": pending,
            "total_value": total_value
        })
    except Exception as e:
        logger.error(f"Error obteniendo stats de supplier invoices: {e}", exc_info=True)
        return JSONResponse(content={
            "total": 0,
            "processed": 0,
            "pending": 0,
            "total_value": 0
        })


@router.get("/api/supplier-invoices/list")
async def get_supplier_invoices_list(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    """Obtiene lista de facturas de proveedores para el dashboard"""
    try:
        from app.models.invoice import SupplierInvoice, Invoice
        
        invoices = db.query(SupplierInvoice).order_by(
            SupplierInvoice.uploaded_at.desc()
        ).limit(limit).all()
        
        result = []
        for inv in invoices:
            try:
                # Inicializar datos con los de SupplierInvoice
                proveedor = inv.supplier_name or "N/A"
                fecha_emision = inv.invoice_date.isoformat() if inv.invoice_date else None
                numero_documento = inv.invoice_number or "N/A"
                total = inv.total_amount or 0
                
                # Si tiene factura procesada, usar esos datos (son más completos)
                if inv.processed_invoice_id:
                    processed_inv = db.query(Invoice).filter(Invoice.id == inv.processed_invoice_id).first()
                    if processed_inv:
                        if processed_inv.supplier:
                            proveedor = processed_inv.supplier.razon_social
                        if processed_inv.fecha_emision:
                            fecha_emision = processed_inv.fecha_emision.isoformat()
                        if processed_inv.numero_documento:
                            numero_documento = processed_inv.numero_documento
                        if processed_inv.total_neto:
                            total = int(processed_inv.total_neto)
                
                # Limpiar proveedor si es muy largo o tiene datos extraños
                if proveedor and len(proveedor) > 100:
                    # Extraer solo el nombre principal si tiene mucho texto
                    proveedor = proveedor.split('FECHA')[0].strip()
                    proveedor = proveedor.split('NIT')[0].strip()
                    if len(proveedor) > 50:
                        proveedor = proveedor[:50] + "..."
                
                result.append({
                    "id": inv.id,
                    "original_filename": inv.original_filename,
                    "fecha_emision": fecha_emision,
                    "proveedor": proveedor,
                    "numero_documento": numero_documento,
                    "cufe": inv.cufe,
                    "cufe_source": inv.cufe_source,
                    "status": inv.status.value,
                    "total": total,
                    "extraction_quality": inv.extraction_quality or 0.0,
                    "uploaded_at": inv.uploaded_at.isoformat() if inv.uploaded_at else None,
                    "processed_invoice_id": inv.processed_invoice_id,
                })
            except Exception as e:
                logger.error(f"Error procesando invoice {inv.id}: {e}", exc_info=True)
                # Agregar con datos mínimos para no perder la factura
                result.append({
                    "id": inv.id,
                    "original_filename": inv.original_filename,
                    "fecha_emision": None,
                    "proveedor": "Error al cargar",
                    "numero_documento": "N/A",
                    "cufe": inv.cufe,
                    "cufe_source": inv.cufe_source,
                    "status": inv.status.value if hasattr(inv, 'status') else "error",
                    "total": 0,
                    "extraction_quality": 0.0,
                    "uploaded_at": None,
                    "processed_invoice_id": None,
                })
                continue
        
        return JSONResponse(content={"invoices": result})
    except Exception as e:
        logger.error(f"Error obteniendo lista de supplier invoices: {e}", exc_info=True)
        return JSONResponse(content={"invoices": []})


@router.get("/api/cufe/stats")
async def get_cufe_stats(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene estadísticas de CUFEs para el dashboard"""
    # Por ahora retornar datos de ejemplo ya que CUFE está en desarrollo
    return JSONResponse(content={
        "total": 0,
        "downloaded": 0,
        "associated": 0,
        "pending": 0
    })


@router.get("/api/cufe/list")
async def get_cufe_list(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    limit: int = 10,
):
    """Obtiene lista de CUFEs para el dashboard"""
    # Por ahora retornar lista vacía ya que CUFE está en desarrollo
    return JSONResponse(content={"cufes": []})


@router.get("/api/products/stats")
async def get_products_stats(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene estadísticas de productos para el dashboard"""
    from app.models.invoice_item import InvoiceItem
    from sqlalchemy import func, case
    
    # Total de productos únicos (por código)
    total = db.query(func.count(func.distinct(InvoiceItem.codigo))).scalar() or 0
    
    # Productos con match (tienen product_id)
    matched = db.query(func.count(func.distinct(InvoiceItem.codigo))).filter(
        InvoiceItem.product_id.isnot(None)
    ).scalar() or 0
    
    unmatched = total - matched
    
    # Calcular margen promedio (simplificado)
    avg_margin = 0.0
    
    return JSONResponse(content={
        "total": total,
        "matched": matched,
        "unmatched": unmatched,
        "avg_margin": avg_margin
    })


@router.get("/api/products/list")
async def get_products_list(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    limit: int = 10,
):
    """Obtiene lista de productos para el dashboard"""
    from app.models.invoice_item import InvoiceItem
    from sqlalchemy import func
    
    # Obtener productos únicos con sus datos agregados
    products_query = db.query(
        InvoiceItem.codigo,
        func.max(InvoiceItem.descripcion).label('descripcion'),
        func.avg(InvoiceItem.precio_unitario).label('precio_compra'),
        func.max(InvoiceItem.product_id).label('product_id'),
    ).group_by(InvoiceItem.codigo).limit(limit).all()
    
    result = []
    for prod in products_query:
        result.append({
            "codigo": prod.codigo,
            "descripcion": prod.descripcion,
            "precio_compra": int(prod.precio_compra) if prod.precio_compra else 0,
            "precio_venta": 0,  # Por ahora no tenemos precio de venta
            "margen": 0.0,
            "matched": prod.product_id is not None,
        })
    
    return JSONResponse(content={"products": result})


# ========================================
# API ENDPOINTS - SUPPLIER INVOICES MEJORADOS
# ========================================

@router.get("/api/supplier-invoices/{invoice_id}/detail")
async def get_supplier_invoice_detail(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene detalle completo de una factura de proveedor con calidad de extracción"""
    service = SupplierInvoiceService(db)
    invoice = service.get_by_id(invoice_id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Calcular badge de calidad
    quality = invoice.extraction_quality or 0.0
    if quality >= 0.80:
        quality_badge = {"label": "Alta", "color": "green", "value": quality}
    elif quality >= 0.50:
        quality_badge = {"label": "Media", "color": "yellow", "value": quality}
    else:
        quality_badge = {"label": "Baja", "color": "red", "value": quality}
    
    # Verificar si está vinculada a una factura procesada
    processed_invoice = None
    if invoice.processed_invoice_id:
        processed_invoice = db.query(Invoice).filter(
            Invoice.id == invoice.processed_invoice_id
        ).first()
    
    return JSONResponse(content={
        "id": invoice.id,
        "original_filename": invoice.original_filename,
        "supplier_name": invoice.supplier_name,
        "supplier_nit": invoice.supplier_nit,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
        "total_amount": invoice.total_amount,
        "cufe": invoice.cufe,
        "cufe_short": invoice.cufe_short,
        "cufe_source": invoice.cufe_source,
        "status": invoice.status.value,
        "status_message": invoice.status_message,
        "extraction_quality": quality,
        "quality_badge": quality_badge,
        "uploaded_at": invoice.uploaded_at.isoformat() if invoice.uploaded_at else None,
        "notes": invoice.notes,
        "dian_url": invoice.dian_url,
        "processed_invoice": {
            "id": processed_invoice.id,
            "numero_documento": processed_invoice.numero_documento,
            "total_neto": processed_invoice.total_neto,
        } if processed_invoice else None,
    })


@router.put("/api/supplier-invoices/{invoice_id}")
async def update_supplier_invoice(
    invoice_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Actualiza datos de una factura de proveedor manualmente"""
    try:
        data = await request.json()
        
        service = SupplierInvoiceService(db)
        invoice = service.get_by_id(invoice_id)
        
        if not invoice:
            return JSONResponse(content={"success": False, "message": "Factura no encontrada"})
        
        # Actualizar campos permitidos
        if 'supplier_name' in data:
            invoice.supplier_name = data['supplier_name']
        if 'supplier_nit' in data:
            invoice.supplier_nit = data['supplier_nit']
        if 'invoice_number' in data:
            invoice.invoice_number = data['invoice_number']
        if 'invoice_date' in data and data['invoice_date']:
            try:
                invoice.invoice_date = datetime.fromisoformat(data['invoice_date'].replace('Z', '+00:00'))
            except:
                pass
        if 'total_amount' in data:
            invoice.total_amount = data['total_amount']
        if 'notes' in data:
            invoice.notes = data['notes']
        
        db.commit()
        db.refresh(invoice)
        
        return JSONResponse(content={
            "success": True,
            "message": "Factura actualizada correctamente",
            "invoice": {
                "id": invoice.id,
                "supplier_name": invoice.supplier_name,
                "supplier_nit": invoice.supplier_nit,
                "invoice_number": invoice.invoice_number,
                "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                "total_amount": invoice.total_amount,
            }
        })
    except Exception as e:
        logger.error(f"Error actualizando factura: {e}", exc_info=True)
        return JSONResponse(content={"success": False, "message": str(e)})


@router.post("/api/supplier-invoices/{invoice_id}/reextract")
async def reextract_supplier_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Re-extrae datos de una factura de proveedor usando el extractor mejorado"""
    from app.services.s3_storage_service import S3StorageService
    
    try:
        service = SupplierInvoiceService(db)
        invoice = service.get_by_id(invoice_id)
        
        if not invoice:
            return JSONResponse(content={"success": False, "message": "Factura no encontrada"})
        
        # Obtener PDF
        s3_service = S3StorageService()
        pdf_content = None
        
        if s3_service.is_enabled() and invoice.original_file_path:
            try:
                pdf_content = s3_service.download_pdf(invoice.original_file_hash, prefix="supplier-invoices")
            except Exception as e:
                logger.error(f"Error descargando PDF desde S3: {e}")
        
        # Fallback a local
        if not pdf_content:
            local_path = f"/app/src/uploads/supplier-invoices/{invoice.original_file_hash}.pdf"
            if os.path.exists(local_path):
                with open(local_path, 'rb') as f:
                    pdf_content = f.read()
        
        if not pdf_content:
            return JSONResponse(content={"success": False, "message": "PDF no encontrado"})
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_content)
            tmp_path = tmp.name
        
        try:
            # Re-extraer con extractor mejorado
            enhanced_data = service.enhanced_extractor.extract_from_pdf(tmp_path)
            
            # Actualizar datos
            if enhanced_data.supplier_name.value:
                invoice.supplier_name = enhanced_data.supplier_name.value
            if enhanced_data.supplier_nit.value:
                invoice.supplier_nit = enhanced_data.supplier_nit.value
            if enhanced_data.invoice_number.value:
                invoice.invoice_number = enhanced_data.invoice_number.value
            if enhanced_data.invoice_date.value:
                invoice.invoice_date = enhanced_data.invoice_date.value
            if enhanced_data.total_amount.value:
                invoice.total_amount = enhanced_data.total_amount.value
            if enhanced_data.cufe.value and not invoice.cufe:
                invoice.cufe = enhanced_data.cufe.value
                invoice.cufe_source = 'reextraction'
                invoice.status = SupplierInvoiceStatus.CUFE_EXTRACTED
            
            invoice.extraction_quality = enhanced_data.overall_quality
            
            db.commit()
            db.refresh(invoice)
            
            return JSONResponse(content={
                "success": True,
                "message": "Datos re-extraídos correctamente",
                "extraction_quality": enhanced_data.overall_quality,
                "field_confidences": {
                    "supplier_name": enhanced_data.supplier_name.confidence,
                    "supplier_nit": enhanced_data.supplier_nit.confidence,
                    "invoice_number": enhanced_data.invoice_number.confidence,
                    "invoice_date": enhanced_data.invoice_date.confidence,
                    "total_amount": enhanced_data.total_amount.confidence,
                    "cufe": enhanced_data.cufe.confidence,
                },
                "invoice": {
                    "id": invoice.id,
                    "supplier_name": invoice.supplier_name,
                    "supplier_nit": invoice.supplier_nit,
                    "invoice_number": invoice.invoice_number,
                    "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                    "total_amount": invoice.total_amount,
                    "cufe": invoice.cufe,
                }
            })
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error re-extrayendo datos: {e}", exc_info=True)
        return JSONResponse(content={"success": False, "message": str(e)})


@router.delete("/api/supplier-invoices/{invoice_id}")
async def delete_supplier_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Elimina una factura de proveedor"""
    service = SupplierInvoiceService(db)
    success = service.delete(invoice_id)
    
    if not success:
        return JSONResponse(content={"success": False, "message": "Factura no encontrada"})
    
    return JSONResponse(content={"success": True, "message": "Factura eliminada correctamente"})


# ========================================
# CUFE MANAGEMENT - Gestión de CUFEs
# ========================================

from app.models.cufe import CufeRecord, CufeStatus as CufeStatusEnum
from sqlalchemy import func

@router.get("/api/cufe/stats")
async def get_cufe_stats(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Obtiene estadísticas de CUFEs"""
    try:
        total = db.query(func.count(CufeRecord.id)).scalar() or 0
        pending = db.query(func.count(CufeRecord.id)).filter(
            CufeRecord.status == CufeStatusEnum.PENDING
        ).scalar() or 0
        downloaded = db.query(func.count(CufeRecord.id)).filter(
            CufeRecord.status == CufeStatusEnum.DOWNLOADED
        ).scalar() or 0
        processed = db.query(func.count(CufeRecord.id)).filter(
            CufeRecord.status == CufeStatusEnum.PROCESSED
        ).scalar() or 0
        
        return JSONResponse(content={
            "total": total,
            "pending": pending,
            "downloaded": downloaded,
            "processed": processed
        })
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de CUFE: {e}", exc_info=True)
        return JSONResponse(content={
            "total": 0,
            "pending": 0,
            "downloaded": 0,
            "processed": 0
        })


@router.get("/api/cufe/list")
async def get_cufe_list(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
):
    """Lista de CUFEs registrados"""
    try:
        query = db.query(CufeRecord).order_by(CufeRecord.created_at.desc())
        
        if status:
            try:
                status_enum = CufeStatusEnum(status)
                query = query.filter(CufeRecord.status == status_enum)
            except ValueError:
                pass
        
        cufes = query.limit(limit).all()
        
        return JSONResponse(content={
            "success": True,
            "cufes": [
                {
                    "id": cufe.id,
                    "cufe": cufe.cufe,
                    "status": cufe.status.value if cufe.status else "pending",
                    "supplier_name": cufe.supplier_name,
                    "invoice_number": cufe.invoice_number,
                    "invoice_id": cufe.invoice_id,
                    "created_at": cufe.created_at.isoformat() if cufe.created_at else None,
                    "error_message": cufe.error_message
                }
                for cufe in cufes
            ]
        })
    except Exception as e:
        logger.error(f"Error listando CUFEs: {e}", exc_info=True)
        return JSONResponse(content={"success": False, "message": str(e), "cufes": []})


@router.post("/api/cufe/register")
async def register_cufe(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Registra un nuevo CUFE en el sistema"""
    try:
        data = await request.json()
        cufe = data.get('cufe', '').strip()
        
        if not cufe:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "CUFE es requerido"}
            )
        
        if len(cufe) != 96:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "CUFE debe tener 96 caracteres"}
            )
        
        # Verificar si ya existe
        existing = db.query(CufeRecord).filter(CufeRecord.cufe == cufe).first()
        if existing:
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "message": "Este CUFE ya está registrado",
                    "cufe_id": existing.id
                }
            )
        
        # Crear registro
        cufe_record = CufeRecord(
            cufe=cufe,
            status=CufeStatusEnum.PENDING,
            created_by=current_user.id
        )
        db.add(cufe_record)
        db.commit()
        db.refresh(cufe_record)
        
        return JSONResponse(content={
            "success": True,
            "message": "CUFE registrado exitosamente",
            "cufe_id": cufe_record.id,
            "dian_url": f"https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={cufe}"
        })
        
    except Exception as e:
        logger.error(f"Error registrando CUFE: {e}", exc_info=True)
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )


@router.post("/api/cufe/process-dian-pdf")
async def process_dian_pdf(
    file: UploadFile = File(...),
    cufe_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Procesa el PDF descargado desde la DIAN"""
    try:
        # Validar archivo
        if not file.filename.lower().endswith('.pdf'):
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Solo se permiten archivos PDF"}
            )
        
        # Leer contenido
        content = await file.read()
        
        # Extraer datos del PDF
        extractor = PDFExtractorService()
        extracted = extractor.extract_from_bytes(content, file.filename)
        
        if not extracted.success:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "No se pudieron extraer datos del PDF",
                    "errors": extracted.errors
                }
            )
        
        # Actualizar registro de CUFE si existe
        if cufe_id:
            cufe_record = db.query(CufeRecord).filter(CufeRecord.id == cufe_id).first()
            if cufe_record:
                cufe_record.status = CufeStatusEnum.PROCESSING
                cufe_record.supplier_name = extracted.proveedor
                cufe_record.invoice_number = extracted.numero_documento
                db.commit()
        
        # Guardar factura en el sistema
        service = InvoiceService(db)
        
        # Guardar PDF
        import hashlib
        file_hash = hashlib.sha256(content).hexdigest()
        metadata = {
            'filename': file.filename,
            'cufe_cude': extracted.cufe_cude if extracted.cufe_cude else 'unknown',
            'document_type': extracted.document_type if extracted.document_type else 'unknown'
        }
        service.save_pdf(content, file_hash, metadata)
        
        # Guardar factura
        invoice = service.save_invoice(extracted, file_hash)
        
        # Actualizar CUFE como procesado
        if cufe_id and cufe_record:
            cufe_record.status = CufeStatusEnum.PROCESSED
            cufe_record.invoice_id = invoice.id
            db.commit()
        
        return JSONResponse(content={
            "success": True,
            "message": "PDF procesado e importado exitosamente",
            "invoice_id": invoice.id,
            "invoice_number": invoice.numero_documento
        })
        
    except Exception as e:
        logger.error(f"Error procesando PDF de DIAN: {e}", exc_info=True)
        
        # Marcar CUFE como error
        if cufe_id:
            try:
                cufe_record = db.query(CufeRecord).filter(CufeRecord.id == cufe_id).first()
                if cufe_record:
                    cufe_record.status = CufeStatusEnum.ERROR
                    cufe_record.error_message = str(e)
                    db.commit()
            except:
                pass
        
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )


@router.delete("/api/cufe/{cufe_id}")
async def delete_cufe(
    cufe_id: int,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db),
):
    """Elimina un registro de CUFE"""
    try:
        cufe_record = db.query(CufeRecord).filter(CufeRecord.id == cufe_id).first()
        
        if not cufe_record:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": "CUFE no encontrado"}
            )
        
        db.delete(cufe_record)
        db.commit()
        
        return JSONResponse(content={
            "success": True,
            "message": "CUFE eliminado correctamente"
        })
        
    except Exception as e:
        logger.error(f"Error eliminando CUFE: {e}", exc_info=True)
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )
