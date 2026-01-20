# ========================================
# PAQUETES EL CLUB - Modelos de Facturas/CUFE
# ========================================

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import TYPE_CHECKING

from app.models.base import Base
from app.utils.datetime_utils import get_colombia_now

if TYPE_CHECKING:
    from app.models.product import Product


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


class CufeStatus(enum.Enum):
    """Estado del CUFE en la factura"""
    EXTRACTED = "extracted"      # CUFE extraído del PDF proveedor
    MANUAL = "manual"             # CUFE agregado manualmente
    VALIDATED = "validated"       # CUFE validado con archivo DIAN
    MISSING = "missing"           # Sin CUFE
    ERROR = "error"               # Error al extraer CUFE


class DianStatus(enum.Enum):
    """Estado del archivo DIAN"""
    PENDING = "pending"           # Pendiente de obtener de DIAN
    DOWNLOADING = "downloading"   # Descargando de DIAN
    DOWNLOADED = "downloaded"     # PDF DIAN descargado
    PROCESSED = "processed"       # PDF DIAN procesado
    ERROR = "error"               # Error al procesar DIAN
    NOT_REQUIRED = "not_required" # No requiere archivo DIAN


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
    # NUEVO: Irregularidades de integración
    COMPRADOR_NO_ES_PAPYRUS = "comprador_no_es_papyrus"
    PRODUCTO_NO_EN_CATALOGO = "producto_no_en_catalogo"
    PRECIO_COMPRA_MAYOR_VENTA = "precio_compra_mayor_venta"


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
    
    # Proveedor (vendedor)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    supplier = relationship("Supplier", back_populates="invoices")
    
    # NUEVO: Comprador (Papyrus)
    buyer_nit = Column(String(20), nullable=True, index=True)
    buyer_razon_social = Column(String(255), nullable=True)
    buyer_direccion = Column(String(255), nullable=True)
    is_papyrus_buyer = Column(Boolean, default=False, index=True)
    
    # NUEVO: Relación con supplier_invoice (PDF original)
    # Nota: La foreign key existe en la BD (creada por migración)
    supplier_invoice_id = Column(Integer, nullable=True, index=True)
    # La relación se define dinámicamente para evitar problemas de orden de carga
    
    # NUEVO: Estados de CUFE y DIAN
    cufe_status = Column(SQLEnum(CufeStatus, values_callable=lambda x: [e.value for e in x]), default=CufeStatus.EXTRACTED, nullable=True, index=True)
    dian_status = Column(SQLEnum(DianStatus, values_callable=lambda x: [e.value for e in x]), default=DianStatus.PENDING, nullable=True, index=True)
    dian_pdf_id = Column(Integer, nullable=True, index=True)  # ID del PDF oficial de DIAN
    cufe_source = Column(String(20), nullable=True)  # 'extracted', 'manual', 'dian'
    
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
    
    @property
    def has_dian_pdf(self) -> bool:
        """Verifica si tiene PDF oficial de DIAN"""
        return self.dian_pdf_id is not None or self.dian_status == DianStatus.PROCESSED
    
    @property
    def cufe_status_display(self) -> str:
        """Texto amigable del estado CUFE"""
        status_map = {
            CufeStatus.EXTRACTED: "CUFE Extraído",
            CufeStatus.MANUAL: "CUFE Manual",
            CufeStatus.VALIDATED: "CUFE Validado",
            CufeStatus.MISSING: "Sin CUFE",
            CufeStatus.ERROR: "Error CUFE"
        }
        return status_map.get(self.cufe_status, "Desconocido")
    
    @property
    def dian_status_display(self) -> str:
        """Texto amigable del estado DIAN"""
        status_map = {
            DianStatus.PENDING: "Pendiente DIAN",
            DianStatus.DOWNLOADING: "Descargando",
            DianStatus.DOWNLOADED: "Descargado",
            DianStatus.PROCESSED: "Procesado DIAN",
            DianStatus.ERROR: "Error DIAN",
            DianStatus.NOT_REQUIRED: "No Requerido"
        }
        return status_map.get(self.dian_status, "Desconocido")


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
    
    # NUEVO: Relación con producto del catálogo
    # Nota: La foreign key existe en la BD (creada por migración) pero no la definimos
    # aquí para evitar problemas de orden de carga de modelos
    product_id = Column(Integer, nullable=True, index=True)
    # La relación 'product' se carga dinámicamente cuando se necesita
    matched_with_catalog = Column(Boolean, default=False, index=True)
    match_confidence = Column(Float, default=0.0)  # 0.0 a 1.0
    match_method = Column(String(50), nullable=True)  # 'codigo', 'codigo_barra', 'nombre', 'manual'
    
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


# ========================================
# FACTURAS DE PROVEEDORES PENDIENTES
# ========================================

class SupplierInvoiceStatus(enum.Enum):
    """Estado de procesamiento de factura de proveedor"""
    PENDING = "pending"              # Subida, pendiente de procesar CUFE
    NO_CUFE = "no_cufe"              # Sin CUFE detectado
    CUFE_EXTRACTED = "cufe_extracted"  # CUFE extraído, pendiente descarga DIAN
    DIAN_DOWNLOADED = "dian_downloaded"  # PDF de DIAN descargado
    PROCESSED = "processed"          # Procesada e importada al sistema
    ERROR = "error"                  # Error en el proceso
    DUPLICATE = "duplicate"          # CUFE duplicado


class SupplierInvoice(Base):
    """
    Modelo para facturas de proveedores subidas.
    Gestiona el flujo: Subir PDF → Extraer CUFE → Descargar DIAN → Importar
    """
    __tablename__ = "supplier_invoices"

    id = Column(Integer, primary_key=True, index=True)
    
    # Archivo original subido
    original_filename = Column(String(255), nullable=False)
    original_file_hash = Column(String(64), unique=True, index=True)
    original_file_path = Column(String(500), nullable=True)
    
    # Datos extraídos del PDF original
    supplier_name = Column(String(255), nullable=True, index=True)
    supplier_nit = Column(String(20), nullable=True, index=True)
    invoice_number = Column(String(50), nullable=True)
    invoice_date = Column(DateTime, nullable=True, index=True)
    total_amount = Column(Integer, nullable=True)
    
    # Calidad de extracción (0.0 - 1.0)
    extraction_quality = Column(Float, default=0.0)
    
    # CUFE extraído
    cufe = Column(String(100), nullable=True, index=True)
    cufe_source = Column(String(20), nullable=True)  # 'filename', 'content', 'manual'
    
    # Estado del proceso
    status = Column(SQLEnum(SupplierInvoiceStatus), default=SupplierInvoiceStatus.PENDING, index=True)
    status_message = Column(Text, nullable=True)
    
    # PDF de DIAN descargado
    dian_file_hash = Column(String(64), nullable=True)
    dian_downloaded_at = Column(DateTime, nullable=True)
    
    # NUEVO: Vinculación con factura procesada
    # Nota: La foreign key existe en la BD pero no definimos la relación aquí
    processed_invoice_id = Column(Integer, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime, default=get_colombia_now, index=True)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now)
    
    # Notas del usuario
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SupplierInvoice {self.original_filename} - {self.status.value}>"
    
    @property
    def cufe_short(self) -> str:
        """Retorna CUFE abreviado para mostrar"""
        if not self.cufe:
            return "-"
        return f"{self.cufe[:12]}...{self.cufe[-8:]}"
    
    @property
    def dian_url(self) -> str:
        """Genera URL de consulta DIAN"""
        if not self.cufe:
            return None
        return f"https://catalogo-vpfe.dian.gov.co/User/SearchDocument?DocumentKey={self.cufe}"
