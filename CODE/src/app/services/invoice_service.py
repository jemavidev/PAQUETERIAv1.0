# ========================================
# PAQUETES EL CLUB - Servicio de Facturas
# ========================================
"""
Servicio para gestión de facturas importadas.
Incluye: persistencia, búsqueda avanzada, validación, 
análisis de IVA, gestión de irregularidades y exportación.
"""

import csv
import io
import hashlib
import logging
import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, and_, or_

from app.models.invoice import (
    Invoice, InvoiceItem, Supplier, DocumentType,
    InvoiceIrregularity, InvoiceRejectedFile,
    IrregularityType, IrregularitySeverity
)
from app.schemas.invoice import (
    ExtractedInvoiceData,
    InvoiceItemCreate,
    ExportableColumn,
    COLUMN_DISPLAY_NAMES,
    DEFAULT_EXPORT_COLUMNS,
    ProductPriceHistory,
    SupplierSummary,
    ProductSummary,
    InvoiceSearchFilters,
    InvoiceDashboardStats,
)
from app.services.pdf_extractor_service import PDFExtractorService

logger = logging.getLogger(__name__)


class InvoiceService:
    """Servicio para gestión de facturas"""
    
    def __init__(self, db: Session):
        self.db = db
        self.extractor = PDFExtractorService()
    
    # ========================================
    # UTILIDADES DE NORMALIZACIÓN
    # ========================================
    
    @staticmethod
    def normalize_price(value: Any) -> int:
        """Normaliza un precio a entero en COP"""
        if value is None:
            return 0
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(round(value))
        if isinstance(value, str):
            # Remover caracteres no numéricos excepto punto y coma
            cleaned = re.sub(r'[^\d.,\-]', '', value)
            # Reemplazar coma por punto si es separador decimal
            if ',' in cleaned and '.' not in cleaned:
                cleaned = cleaned.replace(',', '.')
            elif ',' in cleaned and '.' in cleaned:
                # Formato europeo: 1.234,56 -> 1234.56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            try:
                return int(round(float(cleaned)))
            except ValueError:
                return 0
        return 0
    
    @staticmethod
    def normalize_nit(nit: str) -> str:
        """Normaliza un NIT removiendo caracteres especiales"""
        if not nit:
            return ""
        return re.sub(r'[^\d]', '', nit)
    
    @staticmethod
    def calculate_file_hash(content: bytes) -> str:
        """Calcula el hash SHA256 de un archivo"""
        return hashlib.sha256(content).hexdigest()
    
    # ========================================
    # GESTIÓN DE PROVEEDORES
    # ========================================
    
    def get_or_create_supplier(self, nit: str, razon_social: str, **kwargs) -> Supplier:
        """Obtiene o crea un proveedor por NIT"""
        nit_normalized = self.normalize_nit(nit)
        supplier = self.db.query(Supplier).filter(Supplier.nit == nit_normalized).first()
        
        if not supplier:
            supplier = Supplier(
                nit=nit_normalized,
                razon_social=razon_social.strip().upper(),
                nombre_comercial=kwargs.get('nombre_comercial'),
                direccion=kwargs.get('direccion'),
                telefono=kwargs.get('telefono'),
                correo=kwargs.get('correo'),
                departamento=kwargs.get('departamento'),
                ciudad=kwargs.get('ciudad'),
            )
            self.db.add(supplier)
            self.db.commit()
            self.db.refresh(supplier)
        else:
            # Actualizar datos si vienen más completos
            updated = False
            if kwargs.get('direccion') and not supplier.direccion:
                supplier.direccion = kwargs['direccion']
                updated = True
            if kwargs.get('telefono') and not supplier.telefono:
                supplier.telefono = kwargs['telefono']
                updated = True
            if kwargs.get('correo') and not supplier.correo:
                supplier.correo = kwargs['correo']
                updated = True
            if kwargs.get('ciudad') and not supplier.ciudad:
                supplier.ciudad = kwargs['ciudad']
                updated = True
            if updated:
                self.db.commit()
        
        return supplier
    
    def get_all_suppliers(self) -> List[Supplier]:
        """Obtiene todos los proveedores"""
        return self.db.query(Supplier).order_by(Supplier.razon_social).all()
    
    def get_supplier_by_nit(self, nit: str) -> Optional[Supplier]:
        """Obtiene un proveedor por NIT"""
        return self.db.query(Supplier).filter(Supplier.nit == self.normalize_nit(nit)).first()

    # ========================================
    # VALIDACIÓN Y DETECCIÓN DE IRREGULARIDADES
    # ========================================
    
    def validate_invoice_data(self, data: ExtractedInvoiceData) -> Tuple[bool, List[Dict]]:
        """
        Valida los datos de una factura y detecta irregularidades.
        Returns: (is_valid, list of irregularities)
        """
        irregularities = []
        
        # Validar CUFE/CUDE
        if not data.cufe_cude or len(data.cufe_cude) < 10:
            irregularities.append({
                'tipo': IrregularityType.CUFE_INVALIDO.value,
                'severidad': IrregularitySeverity.ERROR.value,
                'descripcion': 'CUFE/CUDE inválido o muy corto',
                'valor_original': data.cufe_cude,
            })
        
        # Validar NIT
        nit_normalized = self.normalize_nit(data.supplier_nit)
        if not nit_normalized or len(nit_normalized) < 5:
            irregularities.append({
                'tipo': IrregularityType.NIT_INVALIDO.value,
                'severidad': IrregularitySeverity.ERROR.value,
                'descripcion': 'NIT del proveedor inválido',
                'valor_original': data.supplier_nit,
            })
        
        # Validar fecha
        try:
            PDFExtractorService.parse_date(data.fecha_emision)
        except:
            irregularities.append({
                'tipo': IrregularityType.FECHA_INVALIDA.value,
                'severidad': IrregularitySeverity.WARNING.value,
                'descripcion': 'Fecha de emisión no reconocida',
                'valor_original': data.fecha_emision,
            })
        
        # Validar totales
        items_total = sum(item.valor_total for item in data.items)
        if abs(items_total - data.total_neto) > 100:  # Tolerancia de $100
            irregularities.append({
                'tipo': IrregularityType.TOTAL_NO_COINCIDE.value,
                'severidad': IrregularitySeverity.WARNING.value,
                'descripcion': f'Suma de items ({items_total}) no coincide con total ({data.total_neto})',
                'valor_original': str(data.total_neto),
                'valor_sugerido': str(items_total),
            })
        
        # Validar items
        for idx, item in enumerate(data.items):
            item_irregularities = self._validate_item(item, idx + 1)
            irregularities.extend(item_irregularities)
        
        # Determinar si es válido (sin errores críticos)
        has_errors = any(i['severidad'] == IrregularitySeverity.ERROR.value for i in irregularities)
        
        return not has_errors, irregularities
    
    def _validate_item(self, item, item_number: int) -> List[Dict]:
        """Valida un item individual"""
        irregularities = []
        
        # Código faltante
        if not item.codigo:
            irregularities.append({
                'tipo': IrregularityType.CODIGO_FALTANTE.value,
                'severidad': IrregularitySeverity.INFO.value,
                'descripcion': f'Item #{item_number}: Sin código de producto',
                'item_numero': item_number,
            })
        
        # Descripción vacía
        if not item.descripcion or len(item.descripcion.strip()) < 3:
            irregularities.append({
                'tipo': IrregularityType.DESCRIPCION_VACIA.value,
                'severidad': IrregularitySeverity.WARNING.value,
                'descripcion': f'Item #{item_number}: Descripción vacía o muy corta',
                'item_numero': item_number,
            })
        
        # Cantidad inválida
        if item.cantidad <= 0:
            irregularities.append({
                'tipo': IrregularityType.CANTIDAD_INVALIDA.value,
                'severidad': IrregularitySeverity.WARNING.value,
                'descripcion': f'Item #{item_number}: Cantidad inválida ({item.cantidad})',
                'valor_original': str(item.cantidad),
                'valor_sugerido': '1',
                'item_numero': item_number,
            })
        
        # Precio anómalo (muy bajo o muy alto)
        if item.precio_unitario < 0:
            irregularities.append({
                'tipo': IrregularityType.PRECIO_ANOMALO.value,
                'severidad': IrregularitySeverity.ERROR.value,
                'descripcion': f'Item #{item_number}: Precio negativo',
                'valor_original': str(item.precio_unitario),
                'item_numero': item_number,
            })
        elif item.precio_unitario > 100000000:  # > 100 millones
            irregularities.append({
                'tipo': IrregularityType.PRECIO_ANOMALO.value,
                'severidad': IrregularitySeverity.WARNING.value,
                'descripcion': f'Item #{item_number}: Precio inusualmente alto',
                'valor_original': str(item.precio_unitario),
                'item_numero': item_number,
            })
        
        # IVA inconsistente
        if item.iva_porcentaje not in [0, 5, 19]:
            irregularities.append({
                'tipo': IrregularityType.IVA_INCONSISTENTE.value,
                'severidad': IrregularitySeverity.INFO.value,
                'descripcion': f'Item #{item_number}: Porcentaje de IVA no estándar ({item.iva_porcentaje}%)',
                'valor_original': str(item.iva_porcentaje),
                'item_numero': item_number,
            })
        
        return irregularities

    # ========================================
    # GESTIÓN DE FACTURAS - CRUD
    # ========================================
    
    def check_duplicate(self, cufe_cude: str) -> Optional[Invoice]:
        """Verifica si ya existe una factura con el mismo CUFE/CUDE"""
        return self.db.query(Invoice).filter(
            Invoice.cufe_cude == cufe_cude,
            Invoice.is_active == True
        ).first()
    
    def check_file_hash(self, file_hash: str) -> Optional[Invoice]:
        """Verifica si ya existe una factura con el mismo hash de archivo"""
        return self.db.query(Invoice).filter(
            Invoice.file_hash == file_hash,
            Invoice.is_active == True
        ).first()
    
    def save_invoice(
        self, 
        data: ExtractedInvoiceData, 
        user_id: int = None,
        file_content: bytes = None,
        replace_existing: bool = False
    ) -> Invoice:
        """Guarda una factura extraída en la base de datos"""
        
        # Calcular hash del archivo si se proporciona
        file_hash = self.calculate_file_hash(file_content) if file_content else None
        
        # Verificar duplicado por CUFE
        existing = self.check_duplicate(data.cufe_cude)
        if existing:
            if replace_existing:
                # Marcar el existente como reemplazado
                existing.is_active = False
                existing.import_status = 'replaced'
                self.db.commit()
            else:
                raise ValueError(f"Ya existe una factura con CUFE: {data.cufe_cude}")
        
        # Validar datos
        is_valid, irregularities = self.validate_invoice_data(data)
        
        # Obtener o crear proveedor
        supplier = self.get_or_create_supplier(
            nit=data.supplier_nit,
            razon_social=data.supplier_razon_social,
            direccion=data.supplier_direccion,
            telefono=data.supplier_telefono,
            correo=data.supplier_correo,
            departamento=data.supplier_departamento,
            ciudad=data.supplier_ciudad,
        )
        
        # Parsear fecha
        fecha_emision = PDFExtractorService.parse_date(data.fecha_emision)
        fecha_vencimiento = PDFExtractorService.parse_date(data.fecha_vencimiento) if data.fecha_vencimiento else None
        
        # Determinar estado de importación
        error_count = sum(1 for i in irregularities if i['severidad'] == 'error')
        warning_count = sum(1 for i in irregularities if i['severidad'] == 'warning')
        
        if error_count > 0:
            import_status = 'error'
        elif warning_count > 0:
            import_status = 'warning'
        else:
            import_status = 'valid'
        
        # Crear factura
        invoice = Invoice(
            cufe_cude=data.cufe_cude,
            document_type=DocumentType(data.document_type.value),
            numero_documento=data.numero_documento,
            fecha_emision=fecha_emision or datetime.now(),
            fecha_vencimiento=fecha_vencimiento,
            forma_pago=data.forma_pago,
            medio_pago=data.medio_pago,
            supplier_id=supplier.id,
            subtotal=self.normalize_price(data.subtotal),
            descuento=self.normalize_price(data.descuento),
            total_bruto=self.normalize_price(data.total_bruto),
            total_iva=self.normalize_price(data.total_iva),
            total_neto=self.normalize_price(data.total_neto),
            archivo_nombre=data.archivo_nombre,
            file_hash=file_hash,
            imported_by=user_id,
            is_validated=is_valid,
            import_status=import_status,
            import_warnings=[i for i in irregularities if i['severidad'] == 'warning'],
            import_errors=[i for i in irregularities if i['severidad'] == 'error'],
            replaces_id=existing.id if existing and replace_existing else None,
        )
        
        self.db.add(invoice)
        self.db.flush()  # Para obtener el ID
        
        # Actualizar referencia en factura reemplazada
        if existing and replace_existing:
            existing.replaced_by_id = invoice.id
        
        # Crear items
        for item_data in data.items:
            # Detectar IVA incluido basado en el porcentaje y valor
            iva_incluido = self._detect_iva_incluido(item_data)
            
            # Calcular precio base
            precio_base = self._calculate_precio_base(
                item_data.precio_unitario, 
                item_data.iva_porcentaje, 
                iva_incluido
            )
            
            item = InvoiceItem(
                invoice_id=invoice.id,
                numero_item=item_data.numero_item,
                codigo=item_data.codigo,
                descripcion=item_data.descripcion,
                unidad_medida=item_data.unidad_medida,
                cantidad=item_data.cantidad or 1,
                precio_unitario=self.normalize_price(item_data.precio_unitario),
                precio_base=precio_base,
                descuento=self.normalize_price(item_data.descuento),
                recargo=self.normalize_price(item_data.recargo),
                iva_porcentaje=item_data.iva_porcentaje,
                iva_valor=self.normalize_price(item_data.iva_valor),
                iva_incluido=iva_incluido,
                inc_porcentaje=item_data.inc_porcentaje,
                inc_valor=self.normalize_price(item_data.inc_valor),
                valor_total=self.normalize_price(item_data.valor_total),
            )
            self.db.add(item)
        
        # Crear irregularidades
        for irr in irregularities:
            item_id = None
            if 'item_numero' in irr:
                # Buscar el item correspondiente
                item_num = irr['item_numero']
                if item_num <= len(data.items):
                    # Se asignará después del commit
                    pass
            
            irregularity = InvoiceIrregularity(
                invoice_id=invoice.id,
                tipo=irr['tipo'],
                severidad=irr['severidad'],
                descripcion=irr['descripcion'],
                valor_original=irr.get('valor_original'),
                valor_sugerido=irr.get('valor_sugerido'),
            )
            self.db.add(irregularity)
        
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def _detect_iva_incluido(self, item) -> Optional[bool]:
        """Detecta si el IVA está incluido en el precio"""
        if item.iva_porcentaje == 0:
            return None  # No aplica IVA
        
        if item.iva_valor > 0 and item.precio_unitario > 0:
            # Calcular IVA esperado si NO está incluido
            iva_esperado = int(item.precio_unitario * item.cantidad * item.iva_porcentaje / 100)
            
            # Si el IVA reportado es similar al esperado, NO está incluido
            if abs(iva_esperado - item.iva_valor) < 10:  # Tolerancia de $10
                return False
            
            # Calcular IVA esperado si ESTÁ incluido
            precio_base = int(item.precio_unitario / (1 + item.iva_porcentaje / 100))
            iva_incluido_esperado = int(precio_base * item.cantidad * item.iva_porcentaje / 100)
            
            if abs(iva_incluido_esperado - item.iva_valor) < 10:
                return True
        
        return None  # No se puede determinar
    
    def _calculate_precio_base(self, precio_unitario: int, iva_porcentaje: float, iva_incluido: Optional[bool]) -> int:
        """Calcula el precio base sin IVA"""
        if iva_incluido and iva_porcentaje > 0:
            return int(precio_unitario / (1 + iva_porcentaje / 100))
        return precio_unitario

    def get_invoice(self, invoice_id: int, include_inactive: bool = False) -> Optional[Invoice]:
        """Obtiene una factura por ID"""
        query = self.db.query(Invoice).filter(Invoice.id == invoice_id)
        if not include_inactive:
            query = query.filter(Invoice.is_active == True)
        return query.first()
    
    def delete_invoice(self, invoice_id: int, hard_delete: bool = False) -> bool:
        """
        Elimina una factura.
        hard_delete=False: Solo marca como inactiva (soft delete)
        hard_delete=True: Elimina permanentemente
        """
        invoice = self.get_invoice(invoice_id, include_inactive=True)
        if not invoice:
            return False
        
        if hard_delete:
            self.db.delete(invoice)
        else:
            invoice.is_active = False
            invoice.import_status = 'replaced'
        
        self.db.commit()
        return True
    
    def restore_invoice(self, invoice_id: int) -> bool:
        """Restaura una factura eliminada (soft delete)"""
        invoice = self.get_invoice(invoice_id, include_inactive=True)
        if not invoice:
            return False
        
        invoice.is_active = True
        if invoice.import_status == 'replaced':
            # Recalcular estado basado en irregularidades
            error_count = sum(1 for i in (invoice.import_errors or []))
            warning_count = sum(1 for i in (invoice.import_warnings or []))
            
            if error_count > 0:
                invoice.import_status = 'error'
            elif warning_count > 0:
                invoice.import_status = 'warning'
            else:
                invoice.import_status = 'valid'
        
        self.db.commit()
        return True
    
    # ========================================
    # BÚSQUEDA AVANZADA
    # ========================================
    
    def search_invoices(self, filters: InvoiceSearchFilters) -> Tuple[List[Invoice], int]:
        """Búsqueda avanzada de facturas con todos los filtros"""
        query = self.db.query(Invoice).join(Supplier)
        
        # Filtro de activos
        if filters.is_active is not None:
            query = query.filter(Invoice.is_active == filters.is_active)
        
        # Búsqueda general (en múltiples campos)
        if filters.query:
            search_term = f'%{filters.query}%'
            query = query.filter(or_(
                Invoice.numero_documento.ilike(search_term),
                Invoice.cufe_cude.ilike(search_term),
                Supplier.razon_social.ilike(search_term),
                Supplier.nit.ilike(search_term),
            ))
        
        # Filtros específicos de factura
        if filters.numero_documento:
            query = query.filter(Invoice.numero_documento.ilike(f'%{filters.numero_documento}%'))
        
        if filters.cufe_cude:
            query = query.filter(Invoice.cufe_cude.ilike(f'%{filters.cufe_cude}%'))
        
        if filters.fecha_desde:
            query = query.filter(Invoice.fecha_emision >= filters.fecha_desde)
        
        if filters.fecha_hasta:
            query = query.filter(Invoice.fecha_emision <= filters.fecha_hasta)
        
        if filters.total_min is not None:
            query = query.filter(Invoice.total_neto >= filters.total_min)
        
        if filters.total_max is not None:
            query = query.filter(Invoice.total_neto <= filters.total_max)
        
        if filters.document_type:
            query = query.filter(Invoice.document_type == filters.document_type)
        
        if filters.import_status:
            query = query.filter(Invoice.import_status == filters.import_status.value)
        
        # Filtros de proveedor
        if filters.supplier_nit:
            query = query.filter(Supplier.nit == self.normalize_nit(filters.supplier_nit))
        
        if filters.supplier_nombre:
            query = query.filter(Supplier.razon_social.ilike(f'%{filters.supplier_nombre}%'))
        
        if filters.supplier_ciudad:
            query = query.filter(Supplier.ciudad.ilike(f'%{filters.supplier_ciudad}%'))
        
        # Filtros de validación
        if filters.is_validated is not None:
            query = query.filter(Invoice.is_validated == filters.is_validated)
        
        # Filtros de irregularidades
        if filters.has_irregularities is not None:
            if filters.has_irregularities:
                query = query.join(InvoiceIrregularity).filter(InvoiceIrregularity.resuelto == False)
            else:
                # Facturas sin irregularidades pendientes
                subquery = self.db.query(InvoiceIrregularity.invoice_id).filter(
                    InvoiceIrregularity.resuelto == False
                ).distinct()
                query = query.filter(~Invoice.id.in_(subquery))
        
        # Filtros de producto (requiere join con items)
        if filters.producto_codigo or filters.producto_descripcion or filters.iva_porcentaje is not None or filters.iva_incluido is not None or filters.iva_desconocido:
            query = query.join(InvoiceItem)
            
            if filters.producto_codigo:
                query = query.filter(InvoiceItem.codigo.ilike(f'%{filters.producto_codigo}%'))
            
            if filters.producto_descripcion:
                query = query.filter(InvoiceItem.descripcion.ilike(f'%{filters.producto_descripcion}%'))
            
            if filters.iva_porcentaje is not None:
                query = query.filter(InvoiceItem.iva_porcentaje == filters.iva_porcentaje)
            
            # Filtro de IVA: incluido, no incluido, o desconocido
            if filters.iva_desconocido:
                query = query.filter(InvoiceItem.iva_incluido.is_(None))
            elif filters.iva_incluido is not None:
                query = query.filter(InvoiceItem.iva_incluido == filters.iva_incluido)
            
            query = query.distinct()
        
        # Contar total
        total = query.count()
        
        # Ordenamiento
        order_column = getattr(Invoice, filters.order_by, Invoice.fecha_emision)
        if filters.order_dir == 'asc':
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))
        
        # Paginación
        invoices = query.offset((filters.page - 1) * filters.per_page).limit(filters.per_page).all()
        
        return invoices, total
    
    def get_invoices(
        self,
        page: int = 1,
        per_page: int = 20,
        supplier_nit: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        search: str = None,
        only_active: bool = True,
    ) -> Tuple[List[Invoice], int]:
        """Obtiene facturas con filtros básicos y paginación (compatibilidad)"""
        filters = InvoiceSearchFilters(
            query=search,
            supplier_nit=supplier_nit,
            fecha_desde=date_from,
            fecha_hasta=date_to,
            is_active=only_active if only_active else None,
            page=page,
            per_page=per_page,
        )
        return self.search_invoices(filters)

    # ========================================
    # GESTIÓN DE IRREGULARIDADES
    # ========================================
    
    def get_invoice_irregularities(self, invoice_id: int, only_unresolved: bool = False) -> List[InvoiceIrregularity]:
        """Obtiene las irregularidades de una factura"""
        query = self.db.query(InvoiceIrregularity).filter(InvoiceIrregularity.invoice_id == invoice_id)
        if only_unresolved:
            query = query.filter(InvoiceIrregularity.resuelto == False)
        return query.order_by(InvoiceIrregularity.created_at).all()
    
    def resolve_irregularity(
        self, 
        irregularity_id: int, 
        user_id: int,
        notas: str = None,
        accion: str = "ignorar"
    ) -> bool:
        """Resuelve una irregularidad"""
        irr = self.db.query(InvoiceIrregularity).filter(InvoiceIrregularity.id == irregularity_id).first()
        if not irr:
            return False
        
        irr.resuelto = True
        irr.resuelto_por = user_id
        irr.resuelto_at = datetime.now()
        irr.notas_resolucion = notas
        
        self.db.commit()
        return True
    
    def get_all_irregularities(
        self, 
        only_unresolved: bool = True,
        tipo: str = None,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[InvoiceIrregularity], int]:
        """Obtiene todas las irregularidades del sistema"""
        query = self.db.query(InvoiceIrregularity).join(Invoice).filter(Invoice.is_active == True)
        
        if only_unresolved:
            query = query.filter(InvoiceIrregularity.resuelto == False)
        
        if tipo:
            query = query.filter(InvoiceIrregularity.tipo == tipo)
        
        total = query.count()
        irregularities = query.order_by(desc(InvoiceIrregularity.created_at))\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        return irregularities, total
    
    # ========================================
    # ARCHIVOS RECHAZADOS
    # ========================================
    
    def save_rejected_file(
        self,
        archivo_nombre: str,
        razon_rechazo: str,
        detalles_error: Dict = None,
        file_content: bytes = None,
        user_id: int = None,
        puede_reintentar: bool = True
    ) -> InvoiceRejectedFile:
        """Guarda un registro de archivo rechazado"""
        rejected = InvoiceRejectedFile(
            archivo_nombre=archivo_nombre,
            archivo_hash=self.calculate_file_hash(file_content) if file_content else None,
            archivo_size=len(file_content) if file_content else None,
            razon_rechazo=razon_rechazo,
            detalles_error=detalles_error or {},
            uploaded_by=user_id,
            puede_reintentar=puede_reintentar,
        )
        self.db.add(rejected)
        self.db.commit()
        self.db.refresh(rejected)
        return rejected
    
    def get_rejected_files(self, page: int = 1, per_page: int = 20) -> Tuple[List[InvoiceRejectedFile], int]:
        """Obtiene archivos rechazados"""
        query = self.db.query(InvoiceRejectedFile)
        total = query.count()
        files = query.order_by(desc(InvoiceRejectedFile.uploaded_at))\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        return files, total
    
    def delete_rejected_file(self, file_id: int) -> bool:
        """Elimina un registro de archivo rechazado"""
        rejected = self.db.query(InvoiceRejectedFile).filter(InvoiceRejectedFile.id == file_id).first()
        if rejected:
            self.db.delete(rejected)
            self.db.commit()
            return True
        return False

    # ========================================
    # BÚSQUEDA DE PRODUCTOS
    # ========================================
    
    def search_products_global(self, query: str, limit: int = 50) -> List[Dict]:
        """Busca productos en todas las facturas (búsqueda global)"""
        items = self.db.query(
            InvoiceItem.codigo,
            InvoiceItem.descripcion,
            InvoiceItem.iva_porcentaje,
            InvoiceItem.iva_incluido,
            func.count(InvoiceItem.id).label('compras'),
            func.sum(InvoiceItem.cantidad).label('total_cantidad'),
            func.max(InvoiceItem.precio_unitario).label('ultimo_precio'),
            func.min(InvoiceItem.precio_unitario).label('precio_minimo'),
            func.max(InvoiceItem.precio_unitario).label('precio_maximo'),
        ).join(Invoice).filter(
            Invoice.is_active == True,
            or_(
                InvoiceItem.codigo.ilike(f'%{query}%'),
                InvoiceItem.descripcion.ilike(f'%{query}%')
            )
        ).group_by(
            InvoiceItem.codigo, 
            InvoiceItem.descripcion,
            InvoiceItem.iva_porcentaje,
            InvoiceItem.iva_incluido
        ).limit(limit).all()
        
        return [
            {
                'codigo': item.codigo,
                'descripcion': item.descripcion,
                'iva_porcentaje': item.iva_porcentaje,
                'iva_incluido': item.iva_incluido,
                'compras': item.compras,
                'total_cantidad': item.total_cantidad,
                'ultimo_precio': item.ultimo_precio,
                'precio_minimo': item.precio_minimo,
                'precio_maximo': item.precio_maximo,
            }
            for item in items
        ]
    
    def search_products_in_invoice(self, invoice_id: int, query: str) -> List[InvoiceItem]:
        """Busca productos dentro de una factura específica (búsqueda local)"""
        return self.db.query(InvoiceItem).filter(
            InvoiceItem.invoice_id == invoice_id,
            or_(
                InvoiceItem.codigo.ilike(f'%{query}%'),
                InvoiceItem.descripcion.ilike(f'%{query}%')
            )
        ).all()
    
    def get_products_by_iva_status(self, iva_incluido: Optional[bool] = None) -> List[Dict]:
        """Obtiene productos filtrados por estado de IVA"""
        query = self.db.query(
            InvoiceItem.codigo,
            InvoiceItem.descripcion,
            InvoiceItem.iva_porcentaje,
            InvoiceItem.iva_incluido,
            func.count(InvoiceItem.id).label('apariciones'),
        ).join(Invoice).filter(Invoice.is_active == True)
        
        if iva_incluido is not None:
            query = query.filter(InvoiceItem.iva_incluido == iva_incluido)
        else:
            query = query.filter(InvoiceItem.iva_incluido.is_(None))
        
        items = query.group_by(
            InvoiceItem.codigo,
            InvoiceItem.descripcion,
            InvoiceItem.iva_porcentaje,
            InvoiceItem.iva_incluido
        ).order_by(desc('apariciones')).limit(100).all()
        
        return [
            {
                'codigo': item.codigo,
                'descripcion': item.descripcion,
                'iva_porcentaje': item.iva_porcentaje,
                'iva_incluido': item.iva_incluido,
                'apariciones': item.apariciones,
            }
            for item in items
        ]
    
    def search_products(self, query: str, limit: int = 50) -> List[Dict]:
        """Alias para compatibilidad"""
        return self.search_products_global(query, limit)
    
    def get_product_summary(self, codigo: str) -> Optional[ProductSummary]:
        """Obtiene resumen de un producto"""
        items = self.db.query(InvoiceItem)\
            .join(Invoice)\
            .join(Supplier)\
            .filter(
                InvoiceItem.codigo == codigo,
                Invoice.is_active == True
            )\
            .order_by(desc(Invoice.fecha_emision))\
            .all()
        
        if not items:
            return None
        
        proveedores = list(set(item.invoice.supplier.nit for item in items))
        
        # Determinar IVA incluido más común
        iva_incluido_counts = {}
        for item in items:
            key = item.iva_incluido
            iva_incluido_counts[key] = iva_incluido_counts.get(key, 0) + 1
        most_common_iva = max(iva_incluido_counts, key=iva_incluido_counts.get) if iva_incluido_counts else None
        
        return ProductSummary(
            codigo=codigo,
            descripcion=items[0].descripcion,
            total_comprado=sum(item.cantidad for item in items),
            total_gastado=sum(item.valor_total for item in items),
            proveedores=proveedores,
            ultimo_precio=items[0].precio_unitario,
            ultima_compra=items[0].invoice.fecha_emision,
            iva_incluido=most_common_iva,
        )
    
    def get_product_price_history(self, codigo: str) -> Optional[ProductPriceHistory]:
        """Obtiene historial de precios de un producto"""
        items = self.db.query(InvoiceItem)\
            .join(Invoice)\
            .join(Supplier)\
            .filter(
                InvoiceItem.codigo == codigo,
                Invoice.is_active == True
            )\
            .order_by(Invoice.fecha_emision)\
            .all()
        
        if not items:
            return None
        
        precios = []
        for item in items:
            precios.append({
                'fecha': item.invoice.fecha_emision.strftime('%d/%m/%Y'),
                'precio': item.precio_unitario,
                'precio_base': item.precio_base,
                'proveedor': item.invoice.supplier.razon_social,
                'factura': item.invoice.numero_documento,
                'iva_incluido': item.iva_incluido,
            })
        
        precios_valores = [p['precio'] for p in precios]
        
        return ProductPriceHistory(
            codigo=codigo,
            descripcion=items[0].descripcion,
            precios=precios,
            precio_minimo=min(precios_valores),
            precio_maximo=max(precios_valores),
            precio_promedio=int(sum(precios_valores) / len(precios_valores)),
            variacion_porcentaje=round(
                ((precios_valores[-1] - precios_valores[0]) / precios_valores[0] * 100)
                if precios_valores[0] > 0 else 0, 2
            )
        )

    # ========================================
    # ANÁLISIS Y ESTADÍSTICAS
    # ========================================
    
    def get_supplier_summary(self, nit: str) -> Optional[SupplierSummary]:
        """Obtiene resumen de compras a un proveedor"""
        supplier = self.db.query(Supplier).filter(Supplier.nit == self.normalize_nit(nit)).first()
        if not supplier:
            return None
        
        invoices = self.db.query(Invoice).filter(
            Invoice.supplier_id == supplier.id,
            Invoice.is_active == True
        ).all()
        
        if not invoices:
            return None
        
        productos_unicos = self.db.query(func.count(func.distinct(InvoiceItem.codigo)))\
            .join(Invoice)\
            .filter(
                Invoice.supplier_id == supplier.id,
                Invoice.is_active == True
            )\
            .scalar()
        
        return SupplierSummary(
            nit=supplier.nit,
            razon_social=supplier.razon_social,
            total_facturas=len(invoices),
            total_compras=sum(i.total_neto for i in invoices),
            total_iva=sum(i.total_iva for i in invoices),
            primera_compra=min(i.fecha_emision for i in invoices),
            ultima_compra=max(i.fecha_emision for i in invoices),
            productos_unicos=productos_unicos or 0,
        )
    
    def get_dashboard_stats(self) -> Dict:
        """Obtiene estadísticas para el dashboard"""
        # Totales básicos
        total_invoices = self.db.query(func.count(Invoice.id)).scalar() or 0
        total_active = self.db.query(func.count(Invoice.id)).filter(Invoice.is_active == True).scalar() or 0
        total_suppliers = self.db.query(func.count(Supplier.id)).scalar() or 0
        total_items = self.db.query(func.count(InvoiceItem.id)).join(Invoice).filter(Invoice.is_active == True).scalar() or 0
        total_spent = self.db.query(func.sum(Invoice.total_neto)).filter(Invoice.is_active == True).scalar() or 0
        total_iva = self.db.query(func.sum(Invoice.total_iva)).filter(Invoice.is_active == True).scalar() or 0
        
        # Por estado de importación
        valid_count = self.db.query(func.count(Invoice.id)).filter(
            Invoice.is_active == True, Invoice.import_status == 'valid'
        ).scalar() or 0
        warning_count = self.db.query(func.count(Invoice.id)).filter(
            Invoice.is_active == True, Invoice.import_status == 'warning'
        ).scalar() or 0
        error_count = self.db.query(func.count(Invoice.id)).filter(
            Invoice.is_active == True, Invoice.import_status == 'error'
        ).scalar() or 0
        
        # Irregularidades
        total_irregularities = self.db.query(func.count(InvoiceIrregularity.id)).join(Invoice).filter(
            Invoice.is_active == True
        ).scalar() or 0
        unresolved_irregularities = self.db.query(func.count(InvoiceIrregularity.id)).join(Invoice).filter(
            Invoice.is_active == True, InvoiceIrregularity.resuelto == False
        ).scalar() or 0
        
        # Productos por estado de IVA
        items_con_iva_incluido = self.db.query(func.count(InvoiceItem.id)).join(Invoice).filter(
            Invoice.is_active == True, InvoiceItem.iva_incluido == True
        ).scalar() or 0
        items_sin_iva_incluido = self.db.query(func.count(InvoiceItem.id)).join(Invoice).filter(
            Invoice.is_active == True, InvoiceItem.iva_incluido == False
        ).scalar() or 0
        items_iva_desconocido = self.db.query(func.count(InvoiceItem.id)).join(Invoice).filter(
            Invoice.is_active == True, InvoiceItem.iva_incluido.is_(None)
        ).scalar() or 0
        
        # Últimas 5 facturas
        recent_invoices = self.db.query(Invoice)\
            .filter(Invoice.is_active == True)\
            .order_by(desc(Invoice.imported_at))\
            .limit(5)\
            .all()
        
        # Top 5 proveedores por monto
        top_suppliers = self.db.query(
            Supplier.razon_social,
            func.sum(Invoice.total_neto).label('total')
        ).join(Invoice).filter(Invoice.is_active == True)\
            .group_by(Supplier.id)\
            .order_by(desc('total'))\
            .limit(5)\
            .all()
        
        return {
            'total_invoices': total_invoices,
            'total_active': total_active,
            'total_suppliers': total_suppliers,
            'total_items': total_items,
            'total_spent': total_spent,
            'total_iva': total_iva,
            'valid_count': valid_count,
            'warning_count': warning_count,
            'error_count': error_count,
            'total_irregularities': total_irregularities,
            'unresolved_irregularities': unresolved_irregularities,
            'items_con_iva_incluido': items_con_iva_incluido,
            'items_sin_iva_incluido': items_sin_iva_incluido,
            'items_iva_desconocido': items_iva_desconocido,
            'recent_invoices': recent_invoices,
            'top_suppliers': [{'nombre': s[0], 'total': s[1]} for s in top_suppliers],
        }

    # ========================================
    # EXPORTACIÓN DE DATOS
    # ========================================
    
    def export_to_csv(
        self,
        columns: List[ExportableColumn] = None,
        invoice_ids: List[int] = None,
        supplier_nit: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        include_headers: bool = True,
        only_active: bool = True,
    ) -> Tuple[str, int]:
        """
        Exporta datos a CSV con columnas seleccionables.
        Returns: (contenido CSV, número de filas)
        """
        if columns is None:
            columns = DEFAULT_EXPORT_COLUMNS
        
        # Construir query
        query = self.db.query(InvoiceItem).join(Invoice).join(Supplier)
        
        if only_active:
            query = query.filter(Invoice.is_active == True)
        if invoice_ids:
            query = query.filter(Invoice.id.in_(invoice_ids))
        if supplier_nit:
            query = query.filter(Supplier.nit == self.normalize_nit(supplier_nit))
        if date_from:
            query = query.filter(Invoice.fecha_emision >= date_from)
        if date_to:
            query = query.filter(Invoice.fecha_emision <= date_to)
        
        items = query.order_by(Invoice.fecha_emision, InvoiceItem.numero_item).all()
        
        # Generar CSV
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        
        # Headers
        if include_headers:
            headers = [COLUMN_DISPLAY_NAMES.get(col, col.value) for col in columns]
            writer.writerow(headers)
        
        # Datos
        for item in items:
            invoice = item.invoice
            supplier = invoice.supplier
            
            row = []
            for col in columns:
                value = self._get_export_value(col, item, invoice, supplier)
                row.append(value)
            writer.writerow(row)
        
        return output.getvalue(), len(items)
    
    def _get_export_value(
        self,
        column: ExportableColumn,
        item: InvoiceItem,
        invoice: Invoice,
        supplier: Supplier
    ) -> Any:
        """Obtiene el valor de una columna para exportación"""
        # Formatear IVA incluido
        iva_incluido_str = "Sí" if item.iva_incluido == True else ("No" if item.iva_incluido == False else "N/D")
        
        mapping = {
            ExportableColumn.CODIGO: item.codigo or '',
            ExportableColumn.DESCRIPCION: item.descripcion,
            ExportableColumn.CANTIDAD: item.cantidad,
            ExportableColumn.UNIDAD_MEDIDA: item.unidad_medida or '',
            ExportableColumn.PRECIO_UNITARIO: item.precio_unitario,
            ExportableColumn.PRECIO_BASE: item.precio_base,
            ExportableColumn.DESCUENTO_ITEM: item.descuento,
            ExportableColumn.IVA_PORCENTAJE: item.iva_porcentaje,
            ExportableColumn.IVA_VALOR: item.iva_valor,
            ExportableColumn.IVA_INCLUIDO: iva_incluido_str,
            ExportableColumn.VALOR_TOTAL: item.valor_total,
            ExportableColumn.PROVEEDOR_NIT: supplier.nit,
            ExportableColumn.PROVEEDOR_NOMBRE: supplier.razon_social,
            ExportableColumn.PROVEEDOR_CIUDAD: supplier.ciudad or '',
            ExportableColumn.PROVEEDOR_TELEFONO: supplier.telefono or '',
            ExportableColumn.NUMERO_FACTURA: invoice.numero_documento,
            ExportableColumn.TIPO_DOCUMENTO: invoice.document_type.value,
            ExportableColumn.FECHA_FACTURA: invoice.fecha_emision.strftime('%d/%m/%Y') if invoice.fecha_emision else '',
            ExportableColumn.FORMA_PAGO: invoice.forma_pago or '',
            ExportableColumn.MEDIO_PAGO: invoice.medio_pago or '',
            ExportableColumn.CUFE_CUDE: invoice.cufe_cude,
            ExportableColumn.FACTURA_SUBTOTAL: invoice.subtotal,
            ExportableColumn.FACTURA_DESCUENTO: invoice.descuento,
            ExportableColumn.FACTURA_IVA: invoice.total_iva,
            ExportableColumn.FACTURA_TOTAL: invoice.total_neto,
        }
        return mapping.get(column, '')
    
    # ========================================
    # ACTUALIZACIÓN DE ITEMS (IVA)
    # ========================================
    
    def update_item_iva_status(self, item_id: int, iva_incluido: Optional[bool]) -> bool:
        """Actualiza el estado de IVA incluido de un item"""
        item = self.db.query(InvoiceItem).filter(InvoiceItem.id == item_id).first()
        if not item:
            return False
        
        item.iva_incluido = iva_incluido
        item.precio_base = self._calculate_precio_base(
            item.precio_unitario, 
            item.iva_porcentaje, 
            iva_incluido
        )
        
        self.db.commit()
        return True
    
    def bulk_update_iva_status(self, item_ids: List[int], iva_incluido: Optional[bool]) -> int:
        """Actualiza el estado de IVA de múltiples items"""
        count = 0
        for item_id in item_ids:
            if self.update_item_iva_status(item_id, iva_incluido):
                count += 1
        return count
