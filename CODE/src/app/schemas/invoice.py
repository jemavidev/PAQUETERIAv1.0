# ========================================
# PAQUETES EL CLUB - Schemas de Facturas/CUFE
# ========================================

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentTypeEnum(str, Enum):
    FACTURA = "FACTURA"
    POS = "POS"


# ========================================
# Schemas de Proveedor
# ========================================

class SupplierBase(BaseModel):
    nit: str
    razon_social: str
    nombre_comercial: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    departamento: Optional[str] = None
    ciudad: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========================================
# Schemas de Items de Factura
# ========================================

class InvoiceItemBase(BaseModel):
    numero_item: int
    codigo: Optional[str] = None
    descripcion: str
    unidad_medida: Optional[str] = None
    cantidad: int = 1
    precio_unitario: int = 0
    descuento: int = 0
    recargo: int = 0
    iva_porcentaje: float = 0
    iva_valor: int = 0
    inc_porcentaje: float = 0
    inc_valor: int = 0
    valor_total: int = 0


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int

    class Config:
        from_attributes = True


class InvoiceItemReview(InvoiceItemBase):
    """Schema para revisión/corrección de items"""
    has_warning: bool = False
    warning_message: Optional[str] = None
    suggested_fix: Optional[str] = None


# ========================================
# Schemas de Factura
# ========================================

class InvoiceBase(BaseModel):
    cufe_cude: str
    document_type: DocumentTypeEnum
    numero_documento: str
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime] = None
    forma_pago: Optional[str] = None
    medio_pago: Optional[str] = None
    subtotal: int = 0
    descuento: int = 0
    total_bruto: int = 0
    total_iva: int = 0
    total_otros_impuestos: int = 0
    total_neto: int = 0


class InvoiceCreate(InvoiceBase):
    supplier_nit: str
    supplier_razon_social: str
    items: List[InvoiceItemCreate] = []


class InvoiceResponse(InvoiceBase):
    id: int
    supplier: SupplierResponse
    items: List[InvoiceItemResponse] = []
    imported_at: datetime
    is_validated: bool

    class Config:
        from_attributes = True


# ========================================
# Schemas para Extracción y Revisión
# ========================================

class ExtractionWarning(BaseModel):
    """Advertencia durante la extracción"""
    field: str
    message: str
    original_value: Optional[str] = None
    suggested_value: Optional[str] = None
    severity: str = "warning"  # warning, error, info


class ExtractedInvoiceData(BaseModel):
    """Datos extraídos del PDF para revisión"""
    # Identificación
    cufe_cude: str
    document_type: DocumentTypeEnum
    numero_documento: str
    
    # Fechas
    fecha_emision: str
    fecha_vencimiento: Optional[str] = None
    
    # Pago
    forma_pago: Optional[str] = None
    medio_pago: Optional[str] = None
    
    # Proveedor
    supplier_nit: str
    supplier_razon_social: str
    supplier_direccion: Optional[str] = None
    supplier_telefono: Optional[str] = None
    supplier_correo: Optional[str] = None
    supplier_ciudad: Optional[str] = None
    supplier_departamento: Optional[str] = None
    
    # Totales (ya formateados)
    subtotal: int = 0
    descuento: int = 0
    total_bruto: int = 0
    total_iva: int = 0
    total_neto: int = 0
    
    # Items
    items: List[InvoiceItemReview] = []
    
    # Validación
    is_valid: bool = True
    is_duplicate: bool = False
    warnings: List[ExtractionWarning] = []
    
    # Archivo
    archivo_nombre: Optional[str] = None


class InvoiceConfirmation(BaseModel):
    """Datos confirmados para guardar"""
    extracted_data: ExtractedInvoiceData
    corrections: dict = {}  # Campo -> valor corregido


# ========================================
# Schemas para Listados y Exportación
# ========================================

class InvoiceListItem(BaseModel):
    """Item para listado de facturas"""
    id: int
    numero_documento: str
    document_type: DocumentTypeEnum
    fecha_emision: datetime
    supplier_razon_social: str
    supplier_nit: str
    total_neto: int
    items_count: int
    is_validated: bool

    class Config:
        from_attributes = True


class PaginatedInvoices(BaseModel):
    """Respuesta paginada de facturas"""
    items: List[InvoiceListItem]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool


# ========================================
# Schemas para Exportación Flexible
# ========================================

class ExportableColumn(str, Enum):
    """Columnas disponibles para exportación"""
    # Datos del producto
    CODIGO = "codigo"
    DESCRIPCION = "descripcion"
    CANTIDAD = "cantidad"
    UNIDAD_MEDIDA = "unidad_medida"
    PRECIO_UNITARIO = "precio_unitario"
    DESCUENTO_ITEM = "descuento_item"
    IVA_PORCENTAJE = "iva_porcentaje"
    IVA_VALOR = "iva_valor"
    VALOR_TOTAL = "valor_total"
    
    # Datos del proveedor
    PROVEEDOR_NIT = "proveedor_nit"
    PROVEEDOR_NOMBRE = "proveedor_nombre"
    PROVEEDOR_CIUDAD = "proveedor_ciudad"
    PROVEEDOR_TELEFONO = "proveedor_telefono"
    
    # Datos de la factura
    NUMERO_FACTURA = "numero_factura"
    TIPO_DOCUMENTO = "tipo_documento"
    FECHA_FACTURA = "fecha_factura"
    FORMA_PAGO = "forma_pago"
    MEDIO_PAGO = "medio_pago"
    CUFE_CUDE = "cufe_cude"
    
    # Totales de factura
    FACTURA_SUBTOTAL = "factura_subtotal"
    FACTURA_DESCUENTO = "factura_descuento"
    FACTURA_IVA = "factura_iva"
    FACTURA_TOTAL = "factura_total"


# Columnas por defecto para exportación rápida
DEFAULT_EXPORT_COLUMNS = [
    ExportableColumn.CODIGO,
    ExportableColumn.DESCRIPCION,
    ExportableColumn.CANTIDAD,
    ExportableColumn.PRECIO_UNITARIO,
    ExportableColumn.IVA_PORCENTAJE,
    ExportableColumn.VALOR_TOTAL,
    ExportableColumn.PROVEEDOR_NIT,
    ExportableColumn.PROVEEDOR_NOMBRE,
    ExportableColumn.NUMERO_FACTURA,
    ExportableColumn.FECHA_FACTURA,
]

# Nombres legibles para las columnas (para headers de exportación)
COLUMN_DISPLAY_NAMES = {
    ExportableColumn.CODIGO: "Código",
    ExportableColumn.DESCRIPCION: "Descripción",
    ExportableColumn.CANTIDAD: "Cantidad",
    ExportableColumn.UNIDAD_MEDIDA: "Unidad",
    ExportableColumn.PRECIO_UNITARIO: "Precio Unitario",
    ExportableColumn.DESCUENTO_ITEM: "Descuento",
    ExportableColumn.IVA_PORCENTAJE: "IVA %",
    ExportableColumn.IVA_VALOR: "IVA $",
    ExportableColumn.VALOR_TOTAL: "Valor Total",
    ExportableColumn.PROVEEDOR_NIT: "NIT Proveedor",
    ExportableColumn.PROVEEDOR_NOMBRE: "Proveedor",
    ExportableColumn.PROVEEDOR_CIUDAD: "Ciudad Proveedor",
    ExportableColumn.PROVEEDOR_TELEFONO: "Teléfono Proveedor",
    ExportableColumn.NUMERO_FACTURA: "No. Factura",
    ExportableColumn.TIPO_DOCUMENTO: "Tipo Documento",
    ExportableColumn.FECHA_FACTURA: "Fecha",
    ExportableColumn.FORMA_PAGO: "Forma de Pago",
    ExportableColumn.MEDIO_PAGO: "Medio de Pago",
    ExportableColumn.CUFE_CUDE: "CUFE/CUDE",
    ExportableColumn.FACTURA_SUBTOTAL: "Subtotal Factura",
    ExportableColumn.FACTURA_DESCUENTO: "Descuento Factura",
    ExportableColumn.FACTURA_IVA: "IVA Factura",
    ExportableColumn.FACTURA_TOTAL: "Total Factura",
}


class ExportRequest(BaseModel):
    """Solicitud de exportación con columnas seleccionadas"""
    columns: List[ExportableColumn] = DEFAULT_EXPORT_COLUMNS
    invoice_ids: Optional[List[int]] = None  # None = todas
    supplier_nit: Optional[str] = None  # Filtrar por proveedor
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    format: str = "csv"  # csv, xlsx
    include_headers: bool = True
    
    @validator('columns')
    def validate_columns(cls, v):
        if not v:
            return DEFAULT_EXPORT_COLUMNS
        return v


class ExportResponse(BaseModel):
    """Respuesta de exportación"""
    filename: str
    content_type: str
    row_count: int
    columns_exported: List[str]


# ========================================
# Schemas para Análisis de Datos
# ========================================

class ProductPriceHistory(BaseModel):
    """Historial de precios de un producto"""
    codigo: str
    descripcion: str
    precios: List[dict]  # [{fecha, precio, proveedor, factura}]
    precio_minimo: int
    precio_maximo: int
    precio_promedio: int
    variacion_porcentaje: float


class SupplierSummary(BaseModel):
    """Resumen de compras por proveedor"""
    nit: str
    razon_social: str
    total_facturas: int
    total_compras: int
    primera_compra: datetime
    ultima_compra: datetime
    productos_unicos: int


class ProductSummary(BaseModel):
    """Resumen de un producto"""
    codigo: str
    descripcion: str
    total_comprado: int  # Cantidad total
    total_gastado: int  # Valor total
    proveedores: List[str]  # NITs de proveedores
    ultimo_precio: int
    ultima_compra: datetime
