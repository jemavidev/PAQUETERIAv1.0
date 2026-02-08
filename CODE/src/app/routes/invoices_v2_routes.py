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
    notas: Optional[str]
    created_at: datetime
    updated_at: datetime
    
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
    notas: Optional[str] = None
    estado: Optional[str] = None


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
    db: Session = Depends(get_db)
):
    """
    TAB FACTURAS: Lista todas las facturas con filtros y paginación
    OPTIMIZADO: Usa una sola query para contar y obtener items
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
    from sqlalchemy import or_
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
    
    # Obtener items paginados con ordenamiento
    invoices = query.order_by(InvoiceV2.created_at.desc()).offset(skip).limit(limit).all()
    
    # NO generar URLs pre-firmadas aquí (se generan bajo demanda al descargar)
    # Esto ahorra MUCHO tiempo
    
    # Calcular páginas
    page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit  # Redondear hacia arriba
    
    return InvoiceListResponse(
        items=invoices,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


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
    TAB CUFE: Sube el archivo DIAN y actualiza TODOS los datos
    Esta es la fuente de verdad
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
        
        # Resetear el file object para S3
        await file.seek(0)
        
        invoice = service.process_dian_document(cufe, tmp_path, file_obj=file.file)
        
        return invoice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
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

@router.get("/productos", response_model=List[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Buscar en descripción o código"),
    codigo_producto: Optional[str] = Query(None),
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    proveedor: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    TAB PRODUCTOS: Lista todos los productos con filtros avanzados
    """
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
    
    service = InvoiceV2Service(db)
    productos = service.list_products(
        skip=skip,
        limit=limit,
        search=search,
        codigo_producto=codigo_producto,
        fecha_desde=fecha_desde_parsed,
        fecha_hasta=fecha_hasta_parsed,
        proveedor=proveedor
    )
    
    # Enriquecer con datos de la factura
    result = []
    for prod in productos:
        prod_dict = prod.to_dict()
        prod_dict['proveedor_nombre'] = prod.factura.proveedor_nombre
        prod_dict['numero_factura'] = prod.factura.numero_factura
        result.append(ProductResponse(**prod_dict))
    
    return result


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


# ===== ESTADÍSTICAS =====

@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales del sistema
    """
    service = InvoiceV2Service(db)
    stats = service.get_statistics()
    return stats


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
