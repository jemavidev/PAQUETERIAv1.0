# ========================================
# PAQUETES EL CLUB - Modelos de Facturas/CUFE
# ========================================

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base
from app.utils.datetime_utils import get_colombia_now


class DocumentType(enum.Enum):
    """Tipo de documento"""
    FACTURA = "FACTURA"
    POS = "POS"


class ImportStatus(enum.Enum):
    """Estado de importación del documento"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    REPLACED = "replaced"


class IrregularityType(enum.Enum):
    """Tipos de irregularidades detectadas"""
    PRECIO_ANOMALO = "precio_anomalo"
    IVA_INCONSISTENTE = "iva_inconsistente"
    CANTIDAD_INVALIDA = "cantidad_invalida"
    CODIGO_FALTANTE = "codigo_faltante"
    DESCRIPCION_VACIA = "descripcion_vacia"
    TOTAL_NO_COINCIDE = "total_no_coincide"
    FECHA_INVALIDA = "fecha_invalida"
    NIT_INVALIDO = "nit_invalido"
    CUFE_INVALIDO = "cufe_invalido"
    ARCHIVO_CORRUPTO = "archivo_corrupto"
    FORMATO_NO_SOPORTADO = "formato_no_soportado"


class IrregularitySeverity(enum.Enum):
    """Severidad de la irregularidad"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Supplier(Base):
    """Modelo de Proveedor"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    nit = Column(String(20), unique=True, index=True, nullable=False)
    razon_social = Column(String(255), nullable=False, index=True)
    nombre_comercial = Column(String(255), nullable=True)
    direccion = Column(String(255), nullable=True)
    telefono = Column(String(50), nullable=True)
    correo = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)
    ciudad = Column(String(100), nullable=True, index=True)
    
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
    document_type = Column(SQLEnum(DocumentType), nullable=False, index=True)
    numero_documento = Column(String(50), nullable=False, index=True)
    
    # Fechas
    fecha_emision = Column(DateTime, nullable=False, index=True)
    fecha_vencimiento = Column(DateTime, nullable=True)
    
    # Pago
    forma_pago = Column(String(50), nullable=True)
    medio_pago = Column(String(50), nullable=True)
    
    # Proveedor
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    supplier = relationship("Supplier", back_populates="invoices")
    
    # Totales (en pesos colombianos, sin decimales)
    subtotal = Column(Integer, default=0)
    descuento = Column(Integer, default=0)
    total_bruto = Column(Integer, default=0)
    total_iva = Column(Integer, default=0, index=True)
    total_otros_impuestos = Column(Integer, default=0)
    total_neto = Column(Integer, default=0, index=True)
    
    # Archivo original
    archivo_nombre = Column(String(255), nullable=True)
    archivo_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=True)  # Hash SHA256 del archivo
    
    # Metadata de importación
    imported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    imported_at = Column(DateTime, default=get_colombia_now, index=True)
    
    # Estado de validación
    is_validated = Column(Boolean, default=False)
    validation_notes = Column(Text, nullable=True)
    
    # Estado de importación y errores
    import_status = Column(String(20), default='valid')
    import_errors = Column(JSON, default=list)
    import_warnings = Column(JSON, default=list)
    
    # Sistema de reemplazo de documentos
    is_active = Column(Boolean, default=True, index=True)
    replaced_by_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    replaces_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    
    # Relaciones
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    irregularities = relationship("InvoiceIrregularity", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice {self.numero_documento} ({self.document_type.value})>"
    
    @property
    def has_irregularities(self) -> bool:
        """Verifica si tiene irregularidades sin resolver"""
        return any(not irr.resuelto for irr in self.irregularities)
    
    @property
    def unresolved_irregularities_count(self) -> int:
        """Cuenta irregularidades sin resolver"""
        return sum(1 for irr in self.irregularities if not irr.resuelto)


class InvoiceItem(Base):
    """Modelo de Item/Producto de Factura"""
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    
    # Datos del producto
    numero_item = Column(Integer, nullable=False)
    codigo = Column(String(50), nullable=True, index=True)
    descripcion = Column(String(500), nullable=False)
    unidad_medida = Column(String(50), nullable=True)
    
    # Cantidades y precios (en pesos colombianos, sin decimales)
    cantidad = Column(Integer, default=1)
    precio_unitario = Column(Integer, default=0, index=True)
    precio_base = Column(Integer, default=0)  # Precio sin IVA (calculado)
    descuento = Column(Integer, default=0)
    recargo = Column(Integer, default=0)
    
    # Impuestos - IVA INFORMATIVO
    iva_porcentaje = Column(Float, default=0, index=True)
    iva_valor = Column(Integer, default=0)
    iva_incluido = Column(Boolean, nullable=True)  # True=incluido, False=no incluido, None=desconocido
    inc_porcentaje = Column(Float, default=0)
    inc_valor = Column(Integer, default=0)
    
    # Total del item
    valor_total = Column(Integer, default=0)
    
    # Irregularidades y notas
    tiene_irregularidad = Column(Boolean, default=False)
    tipo_irregularidad = Column(String(50), nullable=True)
    notas = Column(Text, nullable=True)
    
    # Relación
    invoice = relationship("Invoice", back_populates="items")
    irregularities = relationship("InvoiceIrregularity", back_populates="item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InvoiceItem {self.descripcion[:30]}... ({self.cantidad} x {self.precio_unitario})>"
    
    def calculate_precio_base(self):
        """Calcula el precio base sin IVA"""
        if self.iva_incluido and self.iva_porcentaje > 0:
            # Si el IVA está incluido, calculamos el precio base
            self.precio_base = int(self.precio_unitario / (1 + self.iva_porcentaje / 100))
        else:
            # Si no está incluido o es desconocido, el precio base es el unitario
            self.precio_base = self.precio_unitario


class InvoiceIrregularity(Base):
    """Modelo de Irregularidades detectadas en facturas"""
    __tablename__ = "invoice_irregularities"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=True, index=True)
    item_id = Column(Integer, ForeignKey("invoice_items.id", ondelete="CASCADE"), nullable=True)
    
    # Tipo y severidad
    tipo = Column(String(50), nullable=False, index=True)
    severidad = Column(String(20), default='warning')
    descripcion = Column(Text, nullable=False)
    
    # Valores para corrección
    valor_original = Column(Text, nullable=True)
    valor_sugerido = Column(Text, nullable=True)
    
    # Estado de resolución
    resuelto = Column(Boolean, default=False, index=True)
    resuelto_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    resuelto_at = Column(DateTime, nullable=True)
    notas_resolucion = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=get_colombia_now)
    
    # Relaciones
    invoice = relationship("Invoice", back_populates="irregularities")
    item = relationship("InvoiceItem", back_populates="irregularities")

    def __repr__(self):
        return f"<Irregularity {self.tipo} - {self.severidad}>"


class InvoiceRejectedFile(Base):
    """Modelo de Archivos rechazados/no compatibles"""
    __tablename__ = "invoice_rejected_files"

    id = Column(Integer, primary_key=True, index=True)
    archivo_nombre = Column(String(255), nullable=False)
    archivo_hash = Column(String(64), nullable=True)
    archivo_size = Column(Integer, nullable=True)
    
    # Razón del rechazo
    razon_rechazo = Column(Text, nullable=False)
    detalles_error = Column(JSON, default=dict)
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=get_colombia_now, index=True)
    puede_reintentar = Column(Boolean, default=True)

    def __repr__(self):
        return f"<RejectedFile {self.archivo_nombre}>"
