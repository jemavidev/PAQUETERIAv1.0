# ========================================
# PAQUETES EL CLUB - Modelos de Facturas/CUFE
# ========================================

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base
from app.utils.datetime_utils import get_colombia_now


class DocumentType(enum.Enum):
    """Tipo de documento"""
    FACTURA = "FACTURA"
    POS = "POS"


class Supplier(Base):
    """Modelo de Proveedor"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    nit = Column(String(20), unique=True, index=True, nullable=False)
    razon_social = Column(String(255), nullable=False)
    nombre_comercial = Column(String(255), nullable=True)
    direccion = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)
    correo = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=get_colombia_now)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now)
    
    # Relaciones
    invoices = relationship("Invoice", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier {self.razon_social} ({self.nit})>"


class Invoice(Base):
    """Modelo de Factura/Documento"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificación única del documento
    cufe_cude = Column(String(100), unique=True, index=True, nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    numero_documento = Column(String(50), nullable=False)
    
    # Fechas
    fecha_emision = Column(DateTime, nullable=False)
    fecha_vencimiento = Column(DateTime, nullable=True)
    
    # Pago
    forma_pago = Column(String(50), nullable=True)
    medio_pago = Column(String(50), nullable=True)
    
    # Proveedor
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    supplier = relationship("Supplier", back_populates="invoices")
    
    # Totales (en pesos colombianos, sin decimales)
    subtotal = Column(Integer, default=0)
    descuento = Column(Integer, default=0)
    total_bruto = Column(Integer, default=0)
    total_iva = Column(Integer, default=0)
    total_otros_impuestos = Column(Integer, default=0)
    total_neto = Column(Integer, default=0)
    
    # Archivo original
    archivo_nombre = Column(String(255), nullable=True)
    archivo_path = Column(String(500), nullable=True)
    
    # Metadata de importación
    imported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    imported_at = Column(DateTime, default=get_colombia_now)
    
    # Estado
    is_validated = Column(Boolean, default=False)
    validation_notes = Column(Text, nullable=True)
    
    # Relaciones
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice {self.numero_documento} ({self.document_type.value})>"


class InvoiceItem(Base):
    """Modelo de Item/Producto de Factura"""
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    
    # Datos del producto
    numero_item = Column(Integer, nullable=False)
    codigo = Column(String(50), nullable=True)
    descripcion = Column(String(500), nullable=False)
    unidad_medida = Column(String(50), nullable=True)
    
    # Cantidades y precios (en pesos colombianos, sin decimales)
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Integer, default=0)
    descuento = Column(Integer, default=0)
    recargo = Column(Integer, default=0)
    
    # Impuestos
    iva_porcentaje = Column(Float, default=0)
    iva_valor = Column(Integer, default=0)
    inc_porcentaje = Column(Float, default=0)
    inc_valor = Column(Integer, default=0)
    
    # Total del item
    valor_total = Column(Integer, default=0)
    
    # Relación
    invoice = relationship("Invoice", back_populates="items")

    def __repr__(self):
        return f"<InvoiceItem {self.descripcion[:30]}... ({self.cantidad} x {self.precio_unitario})>"
