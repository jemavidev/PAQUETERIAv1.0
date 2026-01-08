# ========================================
# PAQUETES EL CLUB - Servicio de Facturas
# ========================================
"""
Servicio para gestión de facturas importadas.
Incluye: persistencia, búsqueda, análisis y exportación.
"""

import csv
import io
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from app.models.invoice import Invoice, InvoiceItem, Supplier, DocumentType
from app.schemas.invoice import (
    ExtractedInvoiceData,
    InvoiceItemCreate,
    ExportableColumn,
    COLUMN_DISPLAY_NAMES,
    DEFAULT_EXPORT_COLUMNS,
    ProductPriceHistory,
    SupplierSummary,
    ProductSummary,
)
from app.services.pdf_extractor_service import PDFExtractorService

logger = logging.getLogger(__name__)


class InvoiceService:
    """Servicio para gestión de facturas"""
    
    def __init__(self, db: Session):
        self.db = db
        self.extractor = PDFExtractorService()
    
    # ========================================
    # Gestión de Proveedores
    # ========================================
    
    def get_or_create_supplier(self, nit: str, razon_social: str, **kwargs) -> Supplier:
        """Obtiene o crea un proveedor por NIT"""
        supplier = self.db.query(Supplier).filter(Supplier.nit == nit).first()
        
        if not supplier:
            supplier = Supplier(
                nit=nit,
                razon_social=razon_social,
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
            if updated:
                self.db.commit()
        
        return supplier
    
    def get_all_suppliers(self) -> List[Supplier]:
        """Obtiene todos los proveedores"""
        return self.db.query(Supplier).order_by(Supplier.razon_social).all()
    
    # ========================================
    # Gestión de Facturas
    # ========================================
    
    def check_duplicate(self, cufe_cude: str) -> bool:
        """Verifica si ya existe una factura con el mismo CUFE/CUDE"""
        return self.db.query(Invoice).filter(Invoice.cufe_cude == cufe_cude).first() is not None
    
    def save_invoice(self, data: ExtractedInvoiceData, user_id: int = None) -> Invoice:
        """Guarda una factura extraída en la base de datos"""
        
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
            subtotal=data.subtotal,
            descuento=data.descuento,
            total_bruto=data.total_bruto,
            total_iva=data.total_iva,
            total_neto=data.total_neto,
            archivo_nombre=data.archivo_nombre,
            imported_by=user_id,
            is_validated=data.is_valid,
        )
        
        self.db.add(invoice)
        self.db.flush()  # Para obtener el ID
        
        # Crear items
        for item_data in data.items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                numero_item=item_data.numero_item,
                codigo=item_data.codigo,
                descripcion=item_data.descripcion,
                unidad_medida=item_data.unidad_medida,
                cantidad=item_data.cantidad,
                precio_unitario=item_data.precio_unitario,
                descuento=item_data.descuento,
                recargo=item_data.recargo,
                iva_porcentaje=item_data.iva_porcentaje,
                iva_valor=item_data.iva_valor,
                inc_porcentaje=item_data.inc_porcentaje,
                inc_valor=item_data.inc_valor,
                valor_total=item_data.valor_total,
            )
            self.db.add(item)
        
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """Obtiene una factura por ID"""
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    def get_invoices(
        self,
        page: int = 1,
        per_page: int = 20,
        supplier_nit: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        search: str = None,
    ) -> Tuple[List[Invoice], int]:
        """Obtiene facturas con filtros y paginación"""
        query = self.db.query(Invoice)
        
        if supplier_nit:
            query = query.join(Supplier).filter(Supplier.nit == supplier_nit)
        
        if date_from:
            query = query.filter(Invoice.fecha_emision >= date_from)
        
        if date_to:
            query = query.filter(Invoice.fecha_emision <= date_to)
        
        if search:
            query = query.filter(
                Invoice.numero_documento.ilike(f'%{search}%')
            )
        
        total = query.count()
        invoices = query.order_by(desc(Invoice.fecha_emision))\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        return invoices, total
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Elimina una factura"""
        invoice = self.get_invoice(invoice_id)
        if invoice:
            self.db.delete(invoice)
            self.db.commit()
            return True
        return False

    # ========================================
    # Exportación de Datos
    # ========================================
    
    def export_to_csv(
        self,
        columns: List[ExportableColumn] = None,
        invoice_ids: List[int] = None,
        supplier_nit: str = None,
        date_from: datetime = None,
        date_to: datetime = None,
        include_headers: bool = True,
    ) -> Tuple[str, int]:
        """
        Exporta datos a CSV con columnas seleccionables.
        Returns: (contenido CSV, número de filas)
        """
        if columns is None:
            columns = DEFAULT_EXPORT_COLUMNS
        
        # Construir query
        query = self.db.query(InvoiceItem).join(Invoice).join(Supplier)
        
        if invoice_ids:
            query = query.filter(Invoice.id.in_(invoice_ids))
        if supplier_nit:
            query = query.filter(Supplier.nit == supplier_nit)
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
        mapping = {
            ExportableColumn.CODIGO: item.codigo or '',
            ExportableColumn.DESCRIPCION: item.descripcion,
            ExportableColumn.CANTIDAD: item.cantidad,
            ExportableColumn.UNIDAD_MEDIDA: item.unidad_medida or '',
            ExportableColumn.PRECIO_UNITARIO: item.precio_unitario,
            ExportableColumn.DESCUENTO_ITEM: item.descuento,
            ExportableColumn.IVA_PORCENTAJE: item.iva_porcentaje,
            ExportableColumn.IVA_VALOR: item.iva_valor,
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
    # Análisis de Datos
    # ========================================
    
    def get_product_price_history(self, codigo: str) -> Optional[ProductPriceHistory]:
        """Obtiene historial de precios de un producto"""
        items = self.db.query(InvoiceItem)\
            .join(Invoice)\
            .join(Supplier)\
            .filter(InvoiceItem.codigo == codigo)\
            .order_by(Invoice.fecha_emision)\
            .all()
        
        if not items:
            return None
        
        precios = []
        for item in items:
            precios.append({
                'fecha': item.invoice.fecha_emision.strftime('%d/%m/%Y'),
                'precio': item.precio_unitario,
                'proveedor': item.invoice.supplier.razon_social,
                'factura': item.invoice.numero_documento,
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
    
    def get_supplier_summary(self, nit: str) -> Optional[SupplierSummary]:
        """Obtiene resumen de compras a un proveedor"""
        supplier = self.db.query(Supplier).filter(Supplier.nit == nit).first()
        if not supplier:
            return None
        
        invoices = self.db.query(Invoice).filter(Invoice.supplier_id == supplier.id).all()
        if not invoices:
            return None
        
        productos_unicos = self.db.query(func.count(func.distinct(InvoiceItem.codigo)))\
            .join(Invoice)\
            .filter(Invoice.supplier_id == supplier.id)\
            .scalar()
        
        return SupplierSummary(
            nit=supplier.nit,
            razon_social=supplier.razon_social,
            total_facturas=len(invoices),
            total_compras=sum(i.total_neto for i in invoices),
            primera_compra=min(i.fecha_emision for i in invoices),
            ultima_compra=max(i.fecha_emision for i in invoices),
            productos_unicos=productos_unicos or 0,
        )
    
    def get_product_summary(self, codigo: str) -> Optional[ProductSummary]:
        """Obtiene resumen de un producto"""
        items = self.db.query(InvoiceItem)\
            .join(Invoice)\
            .join(Supplier)\
            .filter(InvoiceItem.codigo == codigo)\
            .order_by(desc(Invoice.fecha_emision))\
            .all()
        
        if not items:
            return None
        
        proveedores = list(set(item.invoice.supplier.nit for item in items))
        
        return ProductSummary(
            codigo=codigo,
            descripcion=items[0].descripcion,
            total_comprado=sum(item.cantidad for item in items),
            total_gastado=sum(item.valor_total for item in items),
            proveedores=proveedores,
            ultimo_precio=items[0].precio_unitario,
            ultima_compra=items[0].invoice.fecha_emision,
        )
    
    def search_products(self, query: str, limit: int = 50) -> List[Dict]:
        """Busca productos por código o descripción"""
        items = self.db.query(
            InvoiceItem.codigo,
            InvoiceItem.descripcion,
            func.count(InvoiceItem.id).label('compras'),
            func.sum(InvoiceItem.cantidad).label('total_cantidad'),
            func.max(InvoiceItem.precio_unitario).label('ultimo_precio'),
        ).filter(
            (InvoiceItem.codigo.ilike(f'%{query}%')) |
            (InvoiceItem.descripcion.ilike(f'%{query}%'))
        ).group_by(
            InvoiceItem.codigo, InvoiceItem.descripcion
        ).limit(limit).all()
        
        return [
            {
                'codigo': item.codigo,
                'descripcion': item.descripcion,
                'compras': item.compras,
                'total_cantidad': item.total_cantidad,
                'ultimo_precio': item.ultimo_precio,
            }
            for item in items
        ]
    
    def get_dashboard_stats(self) -> Dict:
        """Obtiene estadísticas para el dashboard"""
        total_invoices = self.db.query(func.count(Invoice.id)).scalar() or 0
        total_suppliers = self.db.query(func.count(Supplier.id)).scalar() or 0
        total_items = self.db.query(func.count(InvoiceItem.id)).scalar() or 0
        total_spent = self.db.query(func.sum(Invoice.total_neto)).scalar() or 0
        
        # Últimas 5 facturas
        recent_invoices = self.db.query(Invoice)\
            .order_by(desc(Invoice.imported_at))\
            .limit(5)\
            .all()
        
        # Top 5 proveedores por monto
        top_suppliers = self.db.query(
            Supplier.razon_social,
            func.sum(Invoice.total_neto).label('total')
        ).join(Invoice)\
            .group_by(Supplier.id)\
            .order_by(desc('total'))\
            .limit(5)\
            .all()
        
        return {
            'total_invoices': total_invoices,
            'total_suppliers': total_suppliers,
            'total_items': total_items,
            'total_spent': total_spent,
            'recent_invoices': recent_invoices,
            'top_suppliers': [{'nombre': s[0], 'total': s[1]} for s in top_suppliers],
        }
