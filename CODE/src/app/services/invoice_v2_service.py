"""
Servicio de lógica de negocio para facturas V2
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime, date
from decimal import Decimal
import logging

from ..models.invoice_v2 import InvoiceV2, InvoiceProductV2
from .pdf_parser_service import PDFParserService

# Importar S3Service de forma opcional
try:
    from .s3_service import S3Service
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    logger.warning("S3Service no disponible - los archivos no se subirán a S3")

logger = logging.getLogger(__name__)


class InvoiceV2Service:
    """
    Servicio para gestionar facturas V2
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.pdf_parser = PDFParserService()
        self.s3_service = S3Service() if S3_AVAILABLE else None
    
    # ===== TAB FACTURAS =====
    
    def create_invoice_from_provider_pdf(self, pdf_path: str, file_obj=None, allow_without_cufe: bool = False, overwrite: bool = False) -> InvoiceV2:
        """
        Crea una factura desde el PDF del proveedor
        Extrae: CUFE (si es posible, sino genera temporal si allow_without_cufe=True)
        
        Args:
            pdf_path: Ruta al archivo PDF
            file_obj: Objeto de archivo para subir a S3
            allow_without_cufe: Si True, permite crear factura sin CUFE (genera temporal)
            overwrite: Si True, actualiza factura existente (solo si NO está en estado 'completo')
        """
        # Parsear PDF
        logger.info(f"📄 Parseando PDF: {pdf_path}")
        data = self.pdf_parser.parse_provider_invoice(pdf_path)
        
        if 'error' in data:
            logger.error(f"❌ Error parseando PDF: {data['error']}")
            raise ValueError(data['error'])
        
        # Log de datos extraídos
        logger.info(f"📊 Datos extraídos del PDF:")
        logger.info(f"   - CUFE: {data.get('cufe', 'NO ENCONTRADO')[:20] if data.get('cufe') else 'NO ENCONTRADO'}...")
        logger.info(f"   - Proveedor: {data.get('proveedor_nombre', 'NO ENCONTRADO')}")
        logger.info(f"   - NIT: {data.get('proveedor_nit', 'NO ENCONTRADO')}")
        logger.info(f"   - Número: {data.get('numero_factura', 'NO ENCONTRADO')}")
        logger.info(f"   - Fecha: {data.get('fecha_emision', 'NO ENCONTRADO')}")
        logger.info(f"   - Total: {data.get('total_factura', 'NO ENCONTRADO')}")
        
        # Generar CUFE temporal si no se pudo extraer
        cufe = data.get('cufe')
        if not cufe:
            if not allow_without_cufe:
                logger.error("❌ No se pudo extraer CUFE y allow_without_cufe=False")
                raise ValueError('No se pudo extraer el código CUFE del PDF')
            
            # Generar CUFE temporal único
            import uuid
            import hashlib
            temp_id = str(uuid.uuid4())
            cufe = f"TEMP_{hashlib.sha256(temp_id.encode()).hexdigest()[:120]}"
            logger.warning(f"⚠️ CUFE no encontrado, generando temporal: {cufe[:20]}...")
        else:
            logger.info(f"✅ CUFE extraído correctamente: {cufe[:20]}...")
        
        # Verificar si ya existe
        existing = self.db.query(InvoiceV2).filter_by(cufe=cufe).first()
        if existing:
            if not overwrite:
                raise ValueError(f'Ya existe una factura con el CUFE {cufe[:16]}... (usa overwrite=true para actualizar)')
            
            # Si overwrite=True, verificar que NO esté completa
            if existing.estado == 'completo':
                raise ValueError(f'No se puede actualizar: la factura {cufe[:16]}... está en estado COMPLETO (protegida)')
            
            # ACTUALIZAR: modificar el registro existente
            logger.info(f"🔄 Actualizando factura existente: {cufe[:16]}... (estado: {existing.estado})")
            
            # Eliminar archivo antiguo de S3 si existe
            if existing.archivo_proveedor_s3_key and self.s3_service:
                try:
                    self.s3_service.delete_file(existing.archivo_proveedor_s3_key)
                    logger.info(f"🗑️ Archivo antiguo eliminado de S3: {existing.archivo_proveedor_s3_key}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar archivo antiguo de S3: {e}")
            
            # Actualizar datos
            existing.proveedor_nombre = data.get('proveedor_nombre') or existing.proveedor_nombre
            existing.proveedor_nit = data.get('proveedor_nit') or existing.proveedor_nit
            existing.fecha_emision = data.get('fecha_emision') or existing.fecha_emision
            existing.numero_factura = data.get('numero_factura') or existing.numero_factura
            existing.total_factura = data.get('total_factura') or existing.total_factura
            existing.proveedor_datos_raw = {'raw_text': data.get('raw_text', '')[:5000]}
            existing.updated_at = datetime.now()
            
            # Subir nuevo archivo a S3
            if file_obj and self.s3_service:
                try:
                    file_content = file_obj.read()
                    file_obj.seek(0)
                    
                    s3_key = f"invoices/provider/{cufe}.pdf"
                    archivo_url = self.s3_service.upload_file(file_content, s3_key, content_type='application/pdf')
                    existing.archivo_proveedor_url = archivo_url
                    existing.archivo_proveedor_s3_key = s3_key
                    logger.info(f"✅ Nuevo archivo subido a S3: {s3_key}")
                except Exception as e:
                    logger.warning(f"No se pudo subir nuevo archivo a S3: {e}")
            
            self.db.commit()
            self.db.refresh(existing)
            
            logger.info(f"✅ Factura actualizada: {existing.cufe[:16]}... - {existing.proveedor_nombre}")
            
            return existing
        
        # Si NO existe, crear nueva factura
        # Subir archivo a S3 (opcional)
        archivo_url = None
        archivo_s3_key = None
        if file_obj and self.s3_service:
            try:
                logger.info(f"📤 Intentando subir archivo a S3...")
                # Leer el contenido del archivo como bytes
                file_content = file_obj.read()
                file_obj.seek(0)  # Resetear el puntero por si se necesita después
                
                logger.info(f"   Tamaño del archivo: {len(file_content)} bytes")
                
                s3_key = f"invoices/provider/{cufe}.pdf"
                logger.info(f"   S3 Key: {s3_key}")
                
                archivo_url = self.s3_service.upload_file(file_content, s3_key, content_type='application/pdf')
                archivo_s3_key = s3_key
                logger.info(f"✅ Archivo subido a S3: {s3_key}")
                logger.info(f"   URL: {archivo_url[:100]}...")
            except Exception as e:
                logger.error(f"❌ Error subiendo archivo a S3: {e}")
                import traceback
                logger.error(traceback.format_exc())
        elif not file_obj:
            logger.warning("⚠️ No se proporcionó file_obj, archivo no se subirá a S3")
        elif not self.s3_service:
            logger.warning("⚠️ S3Service no está disponible, archivo no se subirá a S3")
        
        # Crear factura nueva
        invoice = InvoiceV2(
            cufe=cufe,
            archivo_proveedor_url=archivo_url,
            archivo_proveedor_s3_key=archivo_s3_key,
            proveedor_nombre=data.get('proveedor_nombre'),
            proveedor_nit=data.get('proveedor_nit'),
            fecha_emision=data.get('fecha_emision'),
            numero_factura=data.get('numero_factura'),
            total_factura=data.get('total_factura'),
            proveedor_datos_raw={'raw_text': data.get('raw_text', '')[:5000]},  # Limitar tamaño
            estado='sin_cufe' if cufe.startswith('TEMP_') else 'pendiente_dian'
        )
        
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        
        logger.info(f"✅ Factura creada: {invoice.cufe[:16]}... - {invoice.proveedor_nombre} (estado: {invoice.estado})")
        
        return invoice
    
    def list_invoices(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[InvoiceV2]:
        """
        Lista facturas con filtros
        """
        query = self.db.query(InvoiceV2)
        
        # Filtro de búsqueda
        if search:
            query = query.filter(
                or_(
                    InvoiceV2.proveedor_nombre.ilike(f'%{search}%'),
                    InvoiceV2.numero_factura.ilike(f'%{search}%'),
                    InvoiceV2.cufe.ilike(f'%{search}%')
                )
            )
        
        # Filtro de estado
        if estado:
            query = query.filter(InvoiceV2.estado == estado)
        
        # Filtro de fechas
        if fecha_desde:
            query = query.filter(InvoiceV2.fecha_emision >= fecha_desde)
        if fecha_hasta:
            query = query.filter(InvoiceV2.fecha_emision <= fecha_hasta)
        
        # Ordenar por fecha descendente
        query = query.order_by(InvoiceV2.fecha_emision.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_invoice_by_cufe(self, cufe: str) -> Optional[InvoiceV2]:
        """
        Obtiene una factura por CUFE
        """
        return self.db.query(InvoiceV2).filter_by(cufe=cufe).first()
    
    def update_invoice(self, cufe: str, data: Dict[str, Any]) -> InvoiceV2:
        """
        Actualiza una factura (campos editables, excepto CUFE)
        """
        invoice = self.get_invoice_by_cufe(cufe)
        if not invoice:
            raise ValueError(f'Factura no encontrada: {cufe}')
        
        # Campos editables
        editable_fields = [
            'proveedor_nombre', 'proveedor_nit', 'fecha_emision',
            'numero_factura', 'total_factura', 'notas', 'estado'
        ]
        
        for field in editable_fields:
            if field in data:
                setattr(invoice, field, data[field])
        
        invoice.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def delete_invoice(self, cufe: str) -> bool:
        """
        Elimina una factura (cascada a productos)
        """
        invoice = self.get_invoice_by_cufe(cufe)
        if not invoice:
            return False
        
        # Eliminar archivos de S3 (opcional)
        if invoice.archivo_proveedor_s3_key and self.s3_service:
            try:
                self.s3_service.delete_file(invoice.archivo_proveedor_s3_key)
            except Exception as e:
                logger.warning(f"No se pudo eliminar archivo proveedor de S3: {e}")
        
        if invoice.archivo_dian_s3_key and self.s3_service:
            try:
                self.s3_service.delete_file(invoice.archivo_dian_s3_key)
            except Exception as e:
                logger.warning(f"No se pudo eliminar archivo DIAN de S3: {e}")
        
        self.db.delete(invoice)
        self.db.commit()
        
        logger.info(f"Factura eliminada: {cufe[:16]}...")
        
        return True
    
    # ===== TAB CUFE =====
    
    def process_dian_document(self, cufe: str, pdf_path: str, file_obj=None) -> InvoiceV2:
        """
        Procesa el archivo DIAN y actualiza la factura con TODOS los datos
        Esta es la fuente de verdad
        """
        # Verificar que la factura existe
        invoice = self.get_invoice_by_cufe(cufe)
        if not invoice:
            raise ValueError(f'Factura no encontrada: {cufe}')
        
        # Parsear documento DIAN
        data = self.pdf_parser.parse_dian_document(pdf_path)
        
        if 'error' in data:
            raise ValueError(data['error'])
        
        # Validar que el CUFE coincide
        if data.get('cufe') and data['cufe'] != cufe:
            raise ValueError(f'El CUFE del archivo DIAN no coincide con la factura')
        
        # Subir archivo a S3 (opcional)
        archivo_url = None
        archivo_s3_key = None
        if file_obj and self.s3_service:
            try:
                # Leer el contenido del archivo como bytes
                file_content = file_obj.read()
                file_obj.seek(0)  # Resetear el puntero por si se necesita después
                
                s3_key = f"invoices/dian/{cufe}.pdf"
                archivo_url = self.s3_service.upload_file(file_content, s3_key, content_type='application/pdf')
                archivo_s3_key = s3_key
                logger.info(f"✅ Archivo DIAN subido a S3: {s3_key}")
            except Exception as e:
                logger.warning(f"No se pudo subir archivo DIAN a S3: {e}")
        
        # Actualizar factura con datos DIAN
        invoice.archivo_dian_url = archivo_url
        invoice.archivo_dian_s3_key = archivo_s3_key
        invoice.dian_validado = True
        invoice.dian_fecha_validacion = datetime.now()
        invoice.dian_tipo_documento = data.get('tipo_documento')
        invoice.dian_numero_documento = data.get('numero_documento')
        
        # Emisor
        emisor = data.get('emisor', {})
        invoice.dian_emisor_razon_social = emisor.get('razon_social')
        invoice.dian_emisor_nit = emisor.get('nit')
        invoice.dian_emisor_regimen_fiscal = emisor.get('regimen_fiscal')
        invoice.dian_emisor_direccion = emisor.get('direccion')
        invoice.dian_emisor_telefono = emisor.get('telefono')
        invoice.dian_emisor_email = emisor.get('email')
        
        # Adquiriente
        adquiriente = data.get('adquiriente', {})
        invoice.dian_adquiriente_razon_social = adquiriente.get('razon_social')
        invoice.dian_adquiriente_nit = adquiriente.get('nit')
        
        # Condiciones comerciales
        invoice.dian_forma_pago = data.get('forma_pago')
        invoice.dian_medio_pago = data.get('medio_pago')
        invoice.dian_moneda = data.get('moneda', 'COP')
        
        # Totales
        totales = data.get('totales', {})
        invoice.dian_subtotal = totales.get('subtotal')
        invoice.dian_total_bruto = totales.get('total_bruto')
        invoice.dian_total_iva = totales.get('total_iva')
        invoice.dian_total_neto = totales.get('total_neto')
        
        # Información técnica
        invoice.dian_proveedor_tecnologico = data.get('proveedor_tecnologico')
        resolucion = data.get('resolucion', {})
        invoice.dian_resolucion_numero = resolucion.get('numero')
        invoice.dian_resolucion_rango_desde = resolucion.get('rango_desde')
        invoice.dian_resolucion_rango_hasta = resolucion.get('rango_hasta')
        
        # Guardar datos raw
        invoice.dian_datos_raw = {
            'raw_text': data.get('raw_text', '')[:5000],
            'fecha_procesamiento': datetime.now().isoformat()
        }
        
        # Actualizar estado
        invoice.estado = 'completo'
        invoice.updated_at = datetime.now()
        
        # Eliminar productos anteriores (si existen)
        self.db.query(InvoiceProductV2).filter_by(cufe=cufe).delete()
        
        # Insertar productos
        productos = data.get('productos', [])
        for i, prod_data in enumerate(productos):
            producto = InvoiceProductV2(
                cufe=cufe,
                linea_numero=i + 1,
                codigo_producto=prod_data.get('codigo_producto'),
                descripcion=prod_data.get('descripcion'),
                cantidad=prod_data.get('cantidad'),
                precio_unitario=prod_data.get('precio_unitario'),
                iva_porcentaje=prod_data.get('iva_porcentaje'),
                total_item=prod_data.get('total_item'),
                fecha_compra=invoice.fecha_emision.date() if invoice.fecha_emision else None,
                datos_raw=prod_data
            )
            self.db.add(producto)
        
        self.db.commit()
        self.db.refresh(invoice)
        
        logger.info(f"Documento DIAN procesado: {cufe[:16]}... - {len(productos)} productos")
        
        return invoice
    
    # ===== TAB PRODUCTOS =====
    
    def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        codigo_producto: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        proveedor: Optional[str] = None
    ) -> List[InvoiceProductV2]:
        """
        Lista productos con filtros avanzados
        """
        query = self.db.query(InvoiceProductV2).join(InvoiceV2)
        
        # Filtro de búsqueda en descripción
        if search:
            query = query.filter(
                or_(
                    InvoiceProductV2.descripcion.ilike(f'%{search}%'),
                    InvoiceProductV2.codigo_producto.ilike(f'%{search}%')
                )
            )
        
        # Filtro por código de producto
        if codigo_producto:
            query = query.filter(InvoiceProductV2.codigo_producto == codigo_producto)
        
        # Filtro por fechas
        if fecha_desde:
            query = query.filter(InvoiceProductV2.fecha_compra >= fecha_desde)
        if fecha_hasta:
            query = query.filter(InvoiceProductV2.fecha_compra <= fecha_hasta)
        
        # Filtro por proveedor
        if proveedor:
            query = query.filter(InvoiceV2.proveedor_nombre.ilike(f'%{proveedor}%'))
        
        # Ordenar por fecha descendente
        query = query.order_by(InvoiceProductV2.fecha_compra.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_product_history(self, codigo_producto: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de compras de un producto
        """
        productos = self.db.query(InvoiceProductV2).filter_by(
            codigo_producto=codigo_producto
        ).join(InvoiceV2).order_by(InvoiceProductV2.fecha_compra.desc()).all()
        
        history = []
        for prod in productos:
            history.append({
                'producto': prod.to_dict(),
                'factura': {
                    'cufe': prod.factura.cufe,
                    'proveedor': prod.factura.proveedor_nombre,
                    'numero_factura': prod.factura.numero_factura,
                    'fecha': prod.factura.fecha_emision.isoformat() if prod.factura.fecha_emision else None
                }
            })
        
        return history
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales
        """
        total_facturas = self.db.query(func.count(InvoiceV2.cufe)).scalar()
        facturas_completas = self.db.query(func.count(InvoiceV2.cufe)).filter_by(estado='completo').scalar()
        facturas_pendientes = self.db.query(func.count(InvoiceV2.cufe)).filter_by(estado='pendiente_dian').scalar()
        total_productos = self.db.query(func.count(InvoiceProductV2.id)).scalar()
        
        return {
            'total_facturas': total_facturas,
            'facturas_completas': facturas_completas,
            'facturas_pendientes': facturas_pendientes,
            'total_productos': total_productos,
        }
