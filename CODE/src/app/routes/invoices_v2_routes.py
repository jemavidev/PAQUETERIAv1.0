"""
Rutas API para el sistema de facturas V2
3 Tabs: FACTURAS, CUFE, PRODUCTOS
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field
import tempfile
import os
import logging

from ..database import get_db
from ..services.invoice_v2_service import InvoiceV2Service
from ..models.invoice_v2 import InvoiceV2, InvoiceProductV2

router = APIRouter(prefix="/api/v2/invoices", tags=["Invoices V2"])
logger = logging.getLogger(__name__)


# ===== SCHEMAS =====

class InvoiceResponse(BaseModel):
    cufe: str
    archivo_proveedor_url: Optional[str]
    archivo_proveedor_s3_key: Optional[str]  # ✅ AGREGADO para que el frontend sepa si hay archivo
    archivo_dian_url: Optional[str]
    archivo_dian_s3_key: Optional[str]  # ✅ AGREGADO para consistencia
    proveedor_nombre: Optional[str]
    proveedor_nit: Optional[str]
    fecha_emision: Optional[datetime]
    numero_factura: Optional[str]
    total_factura: Optional[float]
    dian_validado: bool
    dian_emisor_razon_social: Optional[str]
    dian_total_neto: Optional[float]
    estado: str
    tipo_factura: Optional[str] = 'reventa'  # ✅ NUEVO
    notas: Optional[str]
    created_at: datetime
    updated_at: datetime
    productos_count: Optional[int] = None  # ✅ Conteo de productos para estados completo/validado
    validation_warnings: Optional[dict] = None  # ✅ Advertencias de validación para PDFs
    
    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class InvoiceDetailResponse(InvoiceResponse):
    productos_count: int = 0


class InvoiceUpdateRequest(BaseModel):
    proveedor_nombre: Optional[str] = None
    proveedor_nit: Optional[str] = None
    fecha_emision: Optional[datetime] = None
    numero_factura: Optional[str] = None
    total_factura: Optional[float] = None
    tipo_factura: Optional[str] = None  # ✅ NUEVO
    notas: Optional[str] = None
    estado: Optional[str] = None


class InvoiceCorrectionRequest(BaseModel):
    """Request para corrección manual de campos problemáticos"""
    dian_total_neto: Optional[float] = None
    dian_subtotal: Optional[float] = None
    dian_total_iva: Optional[float] = None
    fecha_emision: Optional[datetime] = None
    numero_factura: Optional[str] = None
    dian_emisor_razon_social: Optional[str] = None
    dian_emisor_nit: Optional[str] = None


class ManualCufeEntryRequest(BaseModel):
    """Request para entrada manual de CUFE cuando la extracción automática falla"""
    cufe: str = Field(..., min_length=20, max_length=96, description="Código CUFE (96 hex chars) o CUDE corto")
    supplier_name: Optional[str] = None
    invoice_number: Optional[str] = None
    notes: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    cufe: str
    linea_numero: Optional[int]
    codigo_producto: Optional[str]
    codigo_interno: Optional[str]
    descripcion: Optional[str]
    cantidad: Optional[float]
    unidad_medida: Optional[str]
    precio_unitario: Optional[float]
    iva_porcentaje: Optional[float]
    iva_valor: Optional[float]
    subtotal: Optional[float]
    total_item: Optional[float]
    fecha_compra: Optional[date]
    
    # Datos de la factura
    proveedor_nombre: Optional[str] = None
    numero_factura: Optional[str] = None
    
    # Campos de trazabilidad
    precio_anterior: Optional[float] = None
    variacion_precio: Optional[float] = None
    variacion_tipo: Optional[str] = None
    precio_promedio: Optional[float] = None
    precio_minimo_historico: Optional[float] = None
    precio_maximo_historico: Optional[float] = None
    total_compras_producto: Optional[int] = None
    ultimo_proveedor: Optional[str] = None
    dias_desde_ultima_compra: Optional[int] = None
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatisticsResponse(BaseModel):
    total_facturas: int
    facturas_completas: int
    facturas_pendientes: int
    total_productos: int


# ===== TAB 1: FACTURAS =====

@router.post("/extract-cufe")
async def extract_cufe_from_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Extrae solo el CUFE de un PDF (útil para carga múltiple de archivos DIAN)
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = InvoiceV2Service(db)
        text = service.pdf_parser.extract_text_from_pdf(tmp_path)
        
        if not text:
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF")
        
        cufe = service.pdf_parser.extract_cufe(text)
        
        if not cufe:
            raise HTTPException(status_code=400, detail="No se encontró código CUFE en el PDF")
        
        return {"cufe": cufe}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extrayendo CUFE: {str(e)}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/manual-cufe", response_model=InvoiceResponse)
def enter_manual_cufe(
    temp_cufe: str = Query(..., description="CUFE temporal de la factura"),
    request: ManualCufeEntryRequest = None,
    db: Session = Depends(get_db)
):
    """
    Ingresa manualmente un CUFE cuando la extracción automática falló
    Modal/Form para usuario cuando extract_cufe no encuentra el código
    """
    if not request:
        raise HTTPException(status_code=400, detail="Request body requerido")

    import re
    from app.services.pdf_parser_service import PDFParserService

    # Validar que el CUFE tenga formato válido
    if not PDFParserService.validate_cufe_format(request.cufe):
        raise HTTPException(
            status_code=400,
            detail="CUFE debe ser 96 caracteres hexadecimales o código CUDE válido"
        )

    service = InvoiceV2Service(db)

    # Obtener la factura
    invoice = service.get_invoice_by_cufe(temp_cufe)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    # Validar que no existe otro registro con este CUFE
    cleaned_cufe = request.cufe.lower().strip()
    existing = service.get_invoice_by_cufe(cleaned_cufe)
    if existing and existing.id != invoice.id:
        raise HTTPException(status_code=400, detail="Este CUFE ya existe en el sistema")

    # Actualizar la factura con el CUFE manual
    invoice.cufe = cleaned_cufe
    invoice.cufe_origen = 'manual'
    invoice.cufe_validado_usuario = True

    # Actualizar metadata si se proporciona
    if request.supplier_name:
        invoice.proveedor_nombre = request.supplier_name

    if request.invoice_number:
        invoice.numero_factura = request.invoice_number

    if request.notes:
        invoice.notas = request.notes

    # Cambiar estado a pendiente_dian para permitir validación
    invoice.estado = 'pendiente_dian'
    invoice.updated_at = datetime.now()

    # Guardar
    db.commit()
    db.refresh(invoice)

    logger.info(f"✅ CUFE manual ingresado: {cleaned_cufe[:20]}...")

    return InvoiceResponse.from_orm(invoice)


@router.post("/facturas/upload", response_model=InvoiceResponse)
async def upload_provider_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    TAB FACTURAS: Sube una factura de proveedor
    Extrae: CUFE (si es posible, sino genera temporal)
    SIEMPRE permite la carga aunque no tenga CUFE
    OPTIMIZADO: Timeout de 25 segundos
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    # Leer contenido del archivo
    content = await file.read()
    
    # Validar tamaño (máximo 5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 5MB)")
    
    # Guardar temporalmente para procesamiento
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        service = InvoiceV2Service(db)
        
        # Crear un objeto BytesIO para S3 (no depende del file.file que ya se leyó)
        from io import BytesIO
        file_for_s3 = BytesIO(content)
        file_for_s3.name = file.filename  # Agregar nombre para S3
        
        logger.info(f"📤 Subiendo factura: {file.filename} ({len(content)} bytes)")
        
        # SIEMPRE permitir carga sin CUFE (genera temporal)
        invoice = service.create_invoice_from_provider_pdf(
            tmp_path, 
            file_obj=file_for_s3,  # ✅ Usar BytesIO con contenido completo
            allow_without_cufe=True,
            overwrite=False
        )
        
        logger.info(f"✅ Factura creada: {invoice.cufe[:20]}... - S3 Key: {invoice.archivo_proveedor_s3_key or 'NO SUBIDO'}")
        
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error procesando PDF {file.filename}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error procesando PDF: {str(e)}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/facturas", response_model=InvoiceListResponse)
def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=500),
    search: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query('asc'),
    db: Session = Depends(get_db)
):
    """
    TAB FACTURAS: Lista todas las facturas con filtros, ordenamiento y paginación
    OPTIMIZADO: Usa una sola query para contar y obtener items
    INCLUYE: Conteo de productos para estados 'completo' y 'validado'
    ORDENAMIENTO: Soporta ordenar por proveedor, fecha, total, productos
    """
    # Convertir strings vacías a None y parsear fechas
    search = search if search and search.strip() else None
    estado = estado if estado and estado.strip() else None
    
    fecha_desde_parsed = None
    if fecha_desde and fecha_desde.strip():
        try:
            fecha_desde_parsed = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    fecha_hasta_parsed = None
    if fecha_hasta and fecha_hasta.strip():
        try:
            fecha_hasta_parsed = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Construir query base UNA SOLA VEZ
    from sqlalchemy import or_, func
    from ..models.invoice_v2 import InvoiceV2
    
    query = db.query(InvoiceV2)
    
    # Aplicar filtros
    if search:
        query = query.filter(
            or_(
                InvoiceV2.proveedor_nombre.ilike(f'%{search}%'),
                InvoiceV2.numero_factura.ilike(f'%{search}%'),
                InvoiceV2.cufe.ilike(f'%{search}%')
            )
        )
    
    if estado:
        query = query.filter(InvoiceV2.estado == estado)
    
    if fecha_desde_parsed:
        query = query.filter(InvoiceV2.fecha_emision >= fecha_desde_parsed)
    if fecha_hasta_parsed:
        query = query.filter(InvoiceV2.fecha_emision <= fecha_hasta_parsed)
    
    # Contar total (rápido con la misma query)
    total = query.count()
    
    # Aplicar ordenamiento
    if sort_by:
        sort_order_lower = sort_order.lower() if sort_order else 'asc'
        
        if sort_by == 'proveedor':
            # Ordenar por proveedor (usar dian_emisor_razon_social si está disponible, sino proveedor_nombre)
            order_col = func.coalesce(InvoiceV2.dian_emisor_razon_social, InvoiceV2.proveedor_nombre)
            query = query.order_by(order_col.desc() if sort_order_lower == 'desc' else order_col.asc())
        elif sort_by == 'fecha':
            # Ordenar por fecha de emisión
            query = query.order_by(InvoiceV2.fecha_emision.desc() if sort_order_lower == 'desc' else InvoiceV2.fecha_emision.asc())
        elif sort_by == 'total':
            # Ordenar por total (usar dian_total_neto si está disponible, sino total_factura)
            order_col = func.coalesce(InvoiceV2.dian_total_neto, InvoiceV2.total_factura)
            query = query.order_by(order_col.desc() if sort_order_lower == 'desc' else order_col.asc())
        elif sort_by == 'productos':
            # Para ordenar por productos, necesitamos hacer un join con la tabla de productos
            # Esto es más complejo, lo haremos en memoria después de obtener los resultados
            pass
        else:
            # Por defecto, ordenar por fecha de creación
            query = query.order_by(InvoiceV2.created_at.desc())
    else:
        # Sin ordenamiento especificado, usar fecha de creación descendente
        query = query.order_by(InvoiceV2.created_at.desc())
    
    # Obtener items paginados
    invoices = query.offset(skip).limit(limit).all()
    
    # Obtener conteo de productos para facturas con estado 'completo' o 'validado'
    # Solo para las facturas que se están mostrando en esta página
    cufes_to_count = [inv.cufe for inv in invoices if inv.estado in ['completo', 'validado']]
    
    productos_count = {}
    if cufes_to_count:
        from sqlalchemy import func
        counts = db.query(
            InvoiceProductV2.cufe,
            func.count(InvoiceProductV2.id).label('count')
        ).filter(
            InvoiceProductV2.cufe.in_(cufes_to_count)
        ).group_by(InvoiceProductV2.cufe).all()
        
        productos_count = {cufe: count for cufe, count in counts}
    
    # Agregar el conteo de productos a cada factura
    invoice_responses = []
    for invoice in invoices:
        invoice_dict = {
            'cufe': invoice.cufe,
            'archivo_proveedor_url': invoice.archivo_proveedor_url,
            'archivo_proveedor_s3_key': invoice.archivo_proveedor_s3_key,
            'archivo_dian_url': invoice.archivo_dian_url,
            'archivo_dian_s3_key': invoice.archivo_dian_s3_key,
            'proveedor_nombre': invoice.proveedor_nombre,
            'proveedor_nit': invoice.proveedor_nit,
            'fecha_emision': invoice.fecha_emision,
            'numero_factura': invoice.numero_factura,
            'total_factura': invoice.total_factura,
            'dian_validado': invoice.dian_validado,
            'dian_emisor_razon_social': invoice.dian_emisor_razon_social,
            'dian_total_neto': invoice.dian_total_neto,
            'estado': invoice.estado,
            'notas': invoice.notas,
            'created_at': invoice.created_at,
            'updated_at': invoice.updated_at,
            'productos_count': productos_count.get(invoice.cufe, 0) if invoice.estado in ['completo', 'validado'] else None,
            'validation_warnings': None  # Se calcula bajo demanda en el frontend
        }
        invoice_responses.append(invoice_dict)
    
    # Si se ordenó por productos, ordenar en memoria
    if sort_by == 'productos':
        sort_order_lower = sort_order.lower() if sort_order else 'asc'
        invoice_responses.sort(
            key=lambda x: x['productos_count'] if x['productos_count'] is not None else -1,
            reverse=(sort_order_lower == 'desc')
        )
    
    # NO generar URLs pre-firmadas aquí (se generan bajo demanda al descargar)
    # Esto ahorra MUCHO tiempo
    
    # Calcular páginas
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit  # Redondear hacia arriba
    
    return {
        'items': invoice_responses,
        'total': total,
        'page': page,
        'page_size': limit,
        'total_pages': total_pages
    }


@router.get("/facturas/{cufe}/download-url")
async def get_invoice_download_url(
    cufe: str, 
    file_type: str = "proveedor",  # "proveedor" o "dian"
    db: Session = Depends(get_db)
):
    """
    Genera URL de descarga temporal para el PDF de la factura
    
    Args:
        cufe: CUFE de la factura
        file_type: Tipo de archivo a descargar ("proveedor" o "dian")
    """
    service = InvoiceV2Service(db)
    invoice = service.get_invoice_by_cufe(cufe)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Determinar qué archivo descargar
    if file_type == "dian":
        s3_key = invoice.archivo_dian_s3_key
        file_prefix = "factura_dian"
        error_msg = "No hay archivo PDF DIAN disponible para esta factura"
    else:
        s3_key = invoice.archivo_proveedor_s3_key
        file_prefix = "factura_proveedor"
        error_msg = "No hay archivo PDF del proveedor disponible para esta factura"
    
    if not s3_key:
        raise HTTPException(status_code=404, detail=error_msg)
    
    if not service.s3_service:
        raise HTTPException(status_code=500, detail="Servicio S3 no disponible")
    
    try:
        # Generar URL pre-firmada válida por 1 hora
        url = service.s3_service.generate_presigned_url(
            s3_key,
            expiration=3600
        )
        filename = f"{file_prefix}_{invoice.numero_factura or cufe[:16]}.pdf"
        return {"download_url": url, "filename": filename}
    except Exception as e:
        logger.error(f"Error generando URL de descarga: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando URL de descarga: {str(e)}")


@router.get("/facturas/{cufe}", response_model=InvoiceDetailResponse)
def get_invoice(cufe: str, db: Session = Depends(get_db)):
    """
    TAB FACTURAS: Obtiene una factura por CUFE
    """
    service = InvoiceV2Service(db)
    invoice = service.get_invoice_by_cufe(cufe)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    response = InvoiceDetailResponse.from_orm(invoice)
    response.productos_count = len(invoice.productos)
    
    return response


@router.put("/facturas/{cufe}", response_model=InvoiceResponse)
def update_invoice(
    cufe: str,
    data: InvoiceUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    TAB FACTURAS: Actualiza una factura (campos editables, excepto CUFE)
    """
    service = InvoiceV2Service(db)
    
    try:
        invoice = service.update_invoice(cufe, data.dict(exclude_unset=True))
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/facturas/{cufe}")
def delete_invoice(cufe: str, db: Session = Depends(get_db)):
    """
    TAB FACTURAS: Elimina una factura (cascada a productos)
    """
    service = InvoiceV2Service(db)
    
    if not service.delete_invoice(cufe):
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return {"message": "Factura eliminada correctamente"}


# ===== TAB 2: CUFE =====

@router.post("/cufe/{cufe}/upload-dian", response_model=InvoiceResponse)
async def upload_dian_document(
    cufe: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    TAB CUFE: Sube el archivo DIAN (XML o PDF) y actualiza TODOS los datos
    Detecta automáticamente el tipo de archivo y lo procesa
    """
    # Validar extensión
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.xml')):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF o XML")
    
    # Determinar extensión para archivo temporal
    file_extension = '.xml' if filename_lower.endswith('.xml') else '.pdf'
    
    # Guardar temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Detectar tipo de archivo
        from app.services.file_detector_service import FileDetectorService
        file_type = FileDetectorService.detect_file_type(tmp_path)
        
        logger.info(f"📄 Archivo detectado como: {file_type}")
        
        service = InvoiceV2Service(db)
        
        # Resetear el file object para S3
        await file.seek(0)
        
        # Procesar según el tipo
        if file_type == 'XML':
            invoice = service.process_xml_document(cufe, tmp_path, file_obj=file.file)
        elif file_type == 'PDF':
            invoice = service.process_dian_document(cufe, tmp_path, file_obj=file.file)
        else:
            raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
        
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error procesando documento DIAN: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error procesando documento DIAN: {str(e)}")
    finally:
        # Limpiar archivo temporal
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/cufe", response_model=List[InvoiceResponse])
def list_cufe_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    dian_validado: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    TAB CUFE: Lista códigos CUFE con su estado de validación DIAN
    """
    service = InvoiceV2Service(db)
    
    # Usar el mismo método pero filtrar por validación DIAN
    estado = None
    if dian_validado is True:
        estado = 'completo'
    elif dian_validado is False:
        estado = 'pendiente_dian'
    
    invoices = service.list_invoices(
        skip=skip,
        limit=limit,
        search=search,
        estado=estado
    )
    return invoices


@router.get("/cufe/{cufe}/full", response_model=dict)
def get_cufe_full_data(cufe: str, db: Session = Depends(get_db)):
    """
    TAB CUFE: Obtiene TODOS los datos de una factura (incluyendo productos)
    """
    service = InvoiceV2Service(db)
    invoice = service.get_invoice_by_cufe(cufe)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return {
        'factura': invoice.to_dict(include_productos=False),
        'productos': [p.to_dict() for p in invoice.productos],
        'dian_datos_raw': invoice.dian_datos_raw,
        'proveedor_datos_raw': invoice.proveedor_datos_raw,
    }


# ===== TAB 3: PRODUCTOS =====

@router.get("/productos")
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Buscar en descripción o código"),
    codigo_producto: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    proveedor: Optional[str] = Query(None),
    tipo_factura: Optional[str] = Query('reventa', description="Filtrar por tipo de factura: reventa, consumo, servicio, otro, all"),  # ✅ NUEVO
    db: Session = Depends(get_db)
):
    """
    TAB PRODUCTOS: Lista todos los productos con filtros avanzados y paginación
    Por defecto muestra solo productos de facturas tipo 'reventa'
    """
    try:
        from sqlalchemy import or_
        from sqlalchemy.orm import joinedload
        from ..models.invoice_v2 import InvoiceProductV2, InvoiceV2
        from fastapi.responses import JSONResponse
        
        logger.info(f"📦 Listando productos: skip={skip}, limit={limit}, search={search}")
        
        # Convertir strings vacías a None y parsear fechas
        search = search if search and search.strip() else None
        codigo_producto = codigo_producto if codigo_producto and codigo_producto.strip() else None
        proveedor = proveedor if proveedor and proveedor.strip() else None
        
        fecha_desde_parsed = None
        if fecha_desde and fecha_desde.strip():
            try:
                fecha_desde_parsed = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        fecha_hasta_parsed = None
        if fecha_hasta and fecha_hasta.strip():
            try:
                fecha_hasta_parsed = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            except ValueError:
                pass
        fecha_hasta_parsed = None
        if fecha_hasta and fecha_hasta.strip():
            try:
                fecha_hasta_parsed = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Construir query base con eager loading de la relación factura
        query = db.query(InvoiceProductV2).join(InvoiceV2, InvoiceProductV2.cufe == InvoiceV2.cufe).options(joinedload(InvoiceProductV2.factura))
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    InvoiceProductV2.descripcion.ilike(f'%{search}%'),
                    InvoiceProductV2.codigo_producto.ilike(f'%{search}%'),
                    InvoiceProductV2.codigo_interno.ilike(f'%{search}%')
                )
            )
        
        if codigo_producto:
            query = query.filter(InvoiceProductV2.codigo_producto == codigo_producto)
        
        if fecha_desde_parsed:
            query = query.filter(InvoiceProductV2.fecha_compra >= fecha_desde_parsed)
        
        if fecha_hasta_parsed:
            query = query.filter(InvoiceProductV2.fecha_compra <= fecha_hasta_parsed)
        
        if proveedor:
            query = query.filter(InvoiceV2.proveedor_nombre.ilike(f'%{proveedor}%'))
        
        # ✅ NUEVO: Filtrar por tipo de factura
        if tipo_factura and tipo_factura != 'all':
            query = query.filter(InvoiceV2.tipo_factura == tipo_factura)
        
        # Contar total
        total = query.count()
        
        # Obtener items paginados
        productos = query.order_by(InvoiceProductV2.created_at.desc()).offset(skip).limit(limit).all()
        
        # Enriquecer con datos de la factura y análisis de variación de precio
        result = []
        for prod in productos:
            try:
                prod_dict = {
                    "id": prod.id,
                    "cufe": prod.cufe,
                    "linea_numero": prod.linea_numero,
                    "codigo_producto": prod.codigo_producto,
                    "codigo_interno": prod.codigo_interno,
                    "descripcion": prod.descripcion,
                    "cantidad": float(prod.cantidad) if prod.cantidad else None,
                    "unidad_medida": prod.unidad_medida,
                    "precio_unitario": float(prod.precio_unitario) if prod.precio_unitario else None,
                    "iva_porcentaje": float(prod.iva_porcentaje) if prod.iva_porcentaje else None,
                    "iva_valor": float(prod.iva_valor) if prod.iva_valor else None,
                    "descuento_valor": float(prod.descuento_valor) if prod.descuento_valor else None,
                    "recargo_valor": float(prod.recargo_valor) if prod.recargo_valor else None,
                    "subtotal": float(prod.subtotal) if prod.subtotal else None,
                    "total_item": float(prod.total_item) if prod.total_item else None,
                    "fecha_compra": prod.fecha_compra.isoformat() if prod.fecha_compra else None,
                    "proveedor_nombre": prod.factura.proveedor_nombre if prod.factura else None,
                    "numero_factura": prod.factura.numero_factura if prod.factura else None,
                }
                
                # ===== DETECTAR SI PRECIOS INCLUYEN IVA =====
                # Estrategia simplificada: Verificar si total_item coincide con el total mostrado en factura
                # Si total_item × (1 + IVA%) ≈ total_item + iva_valor, entonces total_item NO incluye IVA
                # Si total_item ≈ total_item + iva_valor, entonces total_item YA incluye IVA
                
                iva_incluido_en_precio = False
                if prod.precio_unitario and prod.cantidad and prod.total_item:
                    precio_unit = float(prod.precio_unitario)
                    cantidad = float(prod.cantidad)
                    total = float(prod.total_item)
                    iva_pct = float(prod.iva_porcentaje) if prod.iva_porcentaje else 0
                    iva_val = float(prod.iva_valor) if prod.iva_valor else 0
                    
                    # Tolerancia del 3% para errores de redondeo
                    tolerancia = 0.03
                    
                    # Verificar si iva_valor es significativo (mayor al 1% del total)
                    if iva_val > 0 and iva_val > (total * 0.01):
                        # Hay un iva_valor significativo registrado
                        # Verificar si total + iva_valor ≈ precio × cantidad × (1 + IVA%)
                        total_con_iva_sumado = total + iva_val
                        total_esperado_con_iva = precio_unit * cantidad * (1 + iva_pct / 100)
                        
                        diff = abs(total_con_iva_sumado - total_esperado_con_iva) / max(total_con_iva_sumado, 1)
                        
                        if diff < tolerancia:
                            # total_item NO incluye IVA (iva_valor está separado)
                            iva_incluido_en_precio = False
                        else:
                            # total_item YA incluye IVA (iva_valor es redundante o mal calculado)
                            iva_incluido_en_precio = True
                    else:
                        # No hay iva_valor significativo, verificar directamente
                        # Si total ≈ precio × cantidad × (1 + IVA%), entonces YA incluye IVA
                        total_esperado_con_iva = precio_unit * cantidad * (1 + iva_pct / 100)
                        total_esperado_sin_iva = precio_unit * cantidad
                        
                        diff_con_iva = abs(total - total_esperado_con_iva) / max(total, 1)
                        diff_sin_iva = abs(total - total_esperado_sin_iva) / max(total, 1)
                        
                        if diff_con_iva < diff_sin_iva and diff_con_iva < tolerancia:
                            # total se parece más a precio × cantidad × (1 + IVA%)
                            iva_incluido_en_precio = True
                        else:
                            # total se parece más a precio × cantidad
                            iva_incluido_en_precio = False
                    
                prod_dict["iva_incluido_en_precio"] = iva_incluido_en_precio
                
                # Calcular variación de precio en tiempo real (sin campos de trazabilidad en BD)
                if prod.codigo_producto and prod.precio_unitario:
                    try:
                        # Buscar compra anterior del mismo producto
                        compra_anterior = db.query(InvoiceProductV2).filter(
                            InvoiceProductV2.codigo_producto == prod.codigo_producto,
                            InvoiceProductV2.id != prod.id,
                            InvoiceProductV2.fecha_compra < prod.fecha_compra,
                            InvoiceProductV2.precio_unitario.isnot(None)
                        ).order_by(InvoiceProductV2.fecha_compra.desc()).first()
                        
                        if compra_anterior and compra_anterior.precio_unitario:
                            precio_actual = float(prod.precio_unitario)
                            precio_anterior = float(compra_anterior.precio_unitario)
                            
                            if precio_anterior > 0:
                                variacion_porcentaje = ((precio_actual - precio_anterior) / precio_anterior) * 100
                                
                                if variacion_porcentaje > 0.5:
                                    prod_dict["variacion_precio"] = round(variacion_porcentaje, 1)
                                    prod_dict["variacion_tipo"] = "subio"
                                elif variacion_porcentaje < -0.5:
                                    prod_dict["variacion_precio"] = round(variacion_porcentaje, 1)
                                    prod_dict["variacion_tipo"] = "bajo"
                                else:
                                    prod_dict["variacion_precio"] = 0.0
                                    prod_dict["variacion_tipo"] = "igual"
                            else:
                                prod_dict["variacion_tipo"] = "primera_compra"
                        else:
                            # No hay compra anterior
                            prod_dict["variacion_tipo"] = "primera_compra"
                    except Exception as e:
                        logger.warning(f"Error calculando variación para producto {prod.id}: {e}")
                        prod_dict["variacion_tipo"] = None
                
                result.append(prod_dict)
            except Exception as e:
                logger.error(f"❌ Error procesando producto {prod.id}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Continuar con el siguiente producto
                continue
        
        # Calcular páginas
        page = (skip // limit) + 1
        total_pages = (total + limit - 1) // limit
        
        # Retornar explícitamente como JSON
        response_data = {
            "items": result,
            "total": total,
            "page": page,
            "page_size": limit,
            "total_pages": total_pages
        }
        
        logger.info(f"✅ Retornando {len(result)} productos (total: {total}, página: {page}/{total_pages})")
        
        return JSONResponse(
            content=response_data,
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache, no-store, must-revalidate"
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Error en endpoint /productos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar productos: {str(e)}"
        )


@router.get("/productos/{codigo_producto}/history")
def get_product_history(codigo_producto: str, db: Session = Depends(get_db)):
    """
    TAB PRODUCTOS: Obtiene el historial de compras de un producto
    """
    service = InvoiceV2Service(db)
    history = service.get_product_history(codigo_producto)
    
    if not history:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return {
        'codigo_producto': codigo_producto,
        'total_compras': len(history),
        'historial': history
    }


@router.get("/productos/{product_id}/analisis")
def get_product_analysis(product_id: int, db: Session = Depends(get_db)):
    """
    TAB PRODUCTOS: Análisis detallado de un producto específico
    
    Calcula en tiempo real:
    - Variación de precio vs última compra
    - Descuentos aplicados
    - Recargos aplicados
    - Historial de precios
    """
    try:
        from sqlalchemy import func, desc
        from ..models.invoice_v2 import InvoiceProductV2, InvoiceV2
        from decimal import Decimal
        
        # Obtener el producto actual
        producto_actual = db.query(InvoiceProductV2).filter(
            InvoiceProductV2.id == product_id
        ).first()
        
        if not producto_actual:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        codigo_producto = producto_actual.codigo_producto
        precio_actual = float(producto_actual.precio_unitario) if producto_actual.precio_unitario else 0
        fecha_actual = producto_actual.fecha_compra
        
        # Buscar historial del mismo producto (excluyendo el actual)
        historial = db.query(InvoiceProductV2).join(
            InvoiceV2, InvoiceProductV2.cufe == InvoiceV2.cufe
        ).filter(
            InvoiceProductV2.codigo_producto == codigo_producto,
            InvoiceProductV2.id != product_id,
            InvoiceProductV2.precio_unitario.isnot(None)
        ).order_by(desc(InvoiceProductV2.fecha_compra)).all()
        
        # Análisis de variación de precio
        variacion_precio = None
        if historial:
            # Obtener la compra anterior más reciente
            compra_anterior = historial[0]
            precio_anterior = float(compra_anterior.precio_unitario) if compra_anterior.precio_unitario else 0
            
            if precio_anterior > 0:
                variacion_porcentaje = ((precio_actual - precio_anterior) / precio_anterior) * 100
                
                if variacion_porcentaje > 0.5:  # Subió más del 0.5%
                    tipo = "subio"
                elif variacion_porcentaje < -0.5:  # Bajó más del 0.5%
                    tipo = "bajo"
                else:
                    tipo = "igual"
                
                variacion_precio = {
                    "porcentaje": round(variacion_porcentaje, 1),
                    "tipo": tipo,
                    "precio_anterior": precio_anterior,
                    "precio_actual": precio_actual,
                    "fecha_anterior": compra_anterior.fecha_compra.isoformat() if compra_anterior.fecha_compra else None
                }
            else:
                variacion_precio = {
                    "tipo": "primera_compra",
                    "precio_actual": precio_actual
                }
        else:
            variacion_precio = {
                "tipo": "primera_compra",
                "precio_actual": precio_actual
            }
        
        # Análisis de descuentos
        descuento_valor = float(producto_actual.descuento_valor) if producto_actual.descuento_valor else 0
        descuentos = {
            "tiene_descuento": descuento_valor > 0,
            "valor": descuento_valor,
            "porcentaje": 0
        }
        
        # Calcular porcentaje de descuento si existe
        if descuento_valor > 0 and precio_actual > 0:
            precio_sin_descuento = precio_actual + descuento_valor
            descuentos["porcentaje"] = round((descuento_valor / precio_sin_descuento) * 100, 1)
        
        # Análisis de recargos
        recargo_valor = float(producto_actual.recargo_valor) if producto_actual.recargo_valor else 0
        recargos = {
            "tiene_recargo": recargo_valor > 0,
            "valor": recargo_valor,
            "porcentaje": 0
        }
        
        # Calcular porcentaje de recargo si existe
        if recargo_valor > 0 and precio_actual > 0:
            precio_sin_recargo = precio_actual - recargo_valor
            if precio_sin_recargo > 0:
                recargos["porcentaje"] = round((recargo_valor / precio_sin_recargo) * 100, 1)
        
        # Estadísticas adicionales
        precios_historicos = [float(p.precio_unitario) for p in historial if p.precio_unitario]
        estadisticas = {
            "total_compras": len(historial) + 1,  # +1 por la compra actual
            "precio_promedio": round(sum(precios_historicos) / len(precios_historicos), 2) if precios_historicos else precio_actual,
            "precio_minimo": min(precios_historicos) if precios_historicos else precio_actual,
            "precio_maximo": max(precios_historicos) if precios_historicos else precio_actual
        }
        
        return {
            "producto_id": product_id,
            "codigo_producto": codigo_producto,
            "descripcion": producto_actual.descripcion,
            "variacion_precio": variacion_precio,
            "descuentos": descuentos,
            "recargos": recargos,
            "estadisticas": estadisticas,
            "iva_porcentaje": float(producto_actual.iva_porcentaje) if producto_actual.iva_porcentaje else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en análisis de producto {product_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar producto: {str(e)}"
        )


# ===== ESTADÍSTICAS =====

@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales del sistema
    """
    service = InvoiceV2Service(db)
    stats = service.get_statistics()
    return stats


@router.get("/cufe/{cufe}/validate")
def validate_invoice(cufe: str, db: Session = Depends(get_db)):
    """
    Valida una factura y detecta inconsistencias en campos críticos
    Solo aplica para facturas procesadas desde PDF
    """
    from ..services.validation_service import ValidationService
    
    service = InvoiceV2Service(db)
    invoice = service.get_invoice_by_cufe(cufe)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Ejecutar validación
    validation_result = ValidationService.validate_invoice(invoice)
    
    return validation_result


@router.patch("/cufe/{cufe}/correct")
def correct_invoice_fields(
    cufe: str,
    corrections: InvoiceCorrectionRequest,
    db: Session = Depends(get_db)
):
    """
    Corrige manualmente campos problemáticos de una factura
    Solo permite corregir campos identificados como problemáticos en casos edge
    """
    service = InvoiceV2Service(db)
    invoice = service.get_invoice_by_cufe(cufe)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Aplicar correcciones
    corrections_applied = []
    corrections_dict = corrections.dict(exclude_unset=True)
    
    for field, value in corrections_dict.items():
        if value is not None:
            setattr(invoice, field, value)
            corrections_applied.append(field)
    
    # Guardar registro de correcciones manuales en dian_datos_raw
    if corrections_applied:
        if not invoice.dian_datos_raw:
            invoice.dian_datos_raw = {}
        
        if 'manual_corrections' not in invoice.dian_datos_raw:
            invoice.dian_datos_raw['manual_corrections'] = []
        
        from datetime import datetime
        invoice.dian_datos_raw['manual_corrections'].append({
            'timestamp': datetime.now().isoformat(),
            'fields': corrections_applied,
            'values': corrections_dict
        })
        
        # Marcar como modificado para que SQLAlchemy detecte el cambio en JSONB
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(invoice, 'dian_datos_raw')
        
        invoice.updated_at = datetime.now()
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"✅ Correcciones aplicadas a {cufe[:20]}...: {corrections_applied}")
    
    return {
        "message": "Correcciones aplicadas correctamente",
        "fields_corrected": corrections_applied,
        "invoice": InvoiceResponse.from_orm(invoice)
    }


@router.put("/facturas/{temp_cufe}/update-cufe")
async def update_invoice_cufe(
    temp_cufe: str,
    new_cufe: str = Query(..., min_length=96, max_length=96),
    db: Session = Depends(get_db)
):
    """
    Actualiza el CUFE de una factura (de temporal a real)
    """
    service = InvoiceV2Service(db)
    
    # Verificar que la factura existe
    invoice = service.get_invoice_by_cufe(temp_cufe)
    if not invoice:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # Verificar que el CUFE actual es temporal
    if not temp_cufe.startswith('TEMP_'):
        raise HTTPException(status_code=400, detail="Esta factura ya tiene un CUFE real")
    
    # Validar que el nuevo CUFE es hexadecimal
    import re
    if not re.match(r'^[0-9a-fA-F]{96}$', new_cufe):
        raise HTTPException(status_code=400, detail="El CUFE debe contener solo caracteres hexadecimales (0-9, a-f)")
    
    # Verificar que el nuevo CUFE no existe
    existing = service.get_invoice_by_cufe(new_cufe.lower())
    if existing:
        raise HTTPException(status_code=400, detail=f"⚠️ Este CUFE ya está asociado a otra factura en el sistema")
    
    # Actualizar el CUFE
    try:
        invoice.cufe = new_cufe.lower()
        invoice.estado = 'pendiente_dian'  # Cambiar estado de sin_cufe a pendiente_dian
        invoice.updated_at = datetime.now()
        
        # Si tiene archivo en S3, renombrar la clave
        if invoice.archivo_proveedor_s3_key and service.s3_service:
            try:
                old_key = invoice.archivo_proveedor_s3_key
                new_key = f"invoices/provider/{new_cufe.lower()}.pdf"
                
                # Copiar archivo con nueva clave
                service.s3_service.copy_file(old_key, new_key)
                
                # Eliminar archivo antiguo
                service.s3_service.delete_file(old_key)
                
                # Actualizar clave en BD
                invoice.archivo_proveedor_s3_key = new_key
                invoice.archivo_proveedor_url = service.s3_service.generate_presigned_url(new_key, expiration=3600)
                
                logger.info(f"✅ Archivo S3 renombrado: {old_key} -> {new_key}")
            except Exception as e:
                logger.warning(f"No se pudo renombrar archivo en S3: {e}")
        
        db.commit()
        db.refresh(invoice)
        
        logger.info(f"✅ CUFE actualizado: {temp_cufe[:20]}... -> {new_cufe[:20]}...")
        
        return invoice
    except Exception as e:
        db.rollback()
        logger.error(f"Error actualizando CUFE: {e}")
        raise HTTPException(status_code=500, detail=f"Error actualizando CUFE: {str(e)}")
