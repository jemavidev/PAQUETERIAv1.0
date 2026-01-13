"""
Modelo de Producto sincronizado desde DynamiaERP
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    """Modelo de Producto con todos los campos de DynamiaERP"""
    __tablename__ = "products"
    
    # IDs
    id = Column(Integer, primary_key=True, index=True)
    dynamia_id = Column(Integer, unique=True, nullable=False, index=True)
    account_id = Column(Integer, nullable=False)
    
    # Información básica
    codigo = Column(String(100), nullable=False, index=True)
    nombre = Column(String(500), nullable=False, index=True)
    referencia = Column(String(200))
    descripcion = Column(Text)
    codigo_barra = Column(String(200), index=True)
    codigo_referencia = Column(String(200))
    codigo_lector = Column(String(200))
    external_ref = Column(String(200))
    
    # Precios y costos
    precio_venta = Column(Numeric(15, 2), default=0)
    costo_aproximado = Column(Numeric(15, 2), default=0)
    costo_efectivo = Column(Numeric(15, 2), default=0)
    precio_fijo = Column(Boolean, default=False)
    precio_venta_calculado = Column(Boolean, default=False)
    tiene_precio_temp = Column(Boolean, default=False)
    usar_precio_sucursales = Column(Boolean, default=False)
    
    # Impuestos
    impuesto_incluido = Column(Boolean, default=False)
    porcentaje_impuesto = Column(Numeric(5, 2), default=0)
    exento_impuestos = Column(Boolean, default=False)
    impuesto_fijo = Column(Numeric(15, 2), default=0)
    
    # Inventario
    existencias_totales = Column(Numeric(15, 2), default=0)
    existencias_minimas = Column(Numeric(15, 2), default=0)
    existencias_maximas = Column(Numeric(15, 2), default=0)
    existencias_externas = Column(Numeric(15, 2), default=0)
    
    # Clasificación - Tipo
    tipo_id = Column(Integer, index=True)
    tipo_nombre = Column(String(200))
    tipo_class = Column(String(500))
    
    # Clasificación - Marca
    marca_id = Column(Integer, index=True)
    marca_nombre = Column(String(200))
    marca_class = Column(String(500))
    
    # Clasificación - Línea
    linea_id = Column(Integer, index=True)
    linea_nombre = Column(String(500))
    linea_class = Column(String(500))
    
    # Estados
    activo = Column(Boolean, default=True, index=True)
    vendible = Column(Boolean, default=True, index=True)
    comprable = Column(Boolean, default=True)
    trasladable = Column(Boolean, default=True)
    visualizable_web = Column(Boolean, default=True)
    destacado = Column(Boolean, default=False, index=True)
    permite_pedidos = Column(Boolean, default=False)
    
    # Configuración de ventas
    cantidad_en_ventas = Column(Numeric(15, 2), default=1)
    cantidad_manual = Column(Boolean, default=False)
    orden_en_ventas = Column(Integer, default=0)
    permite_descuentos = Column(Boolean, default=True)
    bloquear_descuentos = Column(Boolean, default=False)
    porcentaje_descuento = Column(Numeric(5, 2), default=0)
    modo_precio = Column(String(50), default='POR_DEFECTO')
    
    # Domicilios y delivery
    domicilios = Column(Boolean, default=True)
    para_llevar = Column(Boolean, default=True)
    bebida_alcoholica = Column(Boolean, default=False)
    valor_envio = Column(Numeric(15, 2), default=0)
    
    # Comisiones
    comisionable = Column(Boolean, default=False)
    descontar_en_comisiones = Column(Boolean, default=False)
    porcentaje_comision = Column(Numeric(5, 2), default=0)
    total_comision_calculada = Column(Numeric(15, 2), default=0)
    
    # Configuraciones avanzadas
    compuesto = Column(Boolean, default=False)
    compuesto_dinamico = Column(Boolean, default=False)
    multi_presentaciones = Column(Boolean, default=False)
    presentaciones_obligatorias = Column(Boolean, default=False)
    usa_seriales = Column(Boolean, default=False)
    usar_balanza = Column(Boolean, default=False)
    autolotes = Column(Boolean, default=False)
    usar_en_transformaciones = Column(Boolean, default=False)
    usar_preguntas_obligatorias = Column(Boolean, default=False)
    nombre_generado = Column(Boolean, default=False)
    autocreado_proveedor = Column(Boolean, default=False)
    
    # Gestión
    porcentaje_pmg = Column(Numeric(5, 2), default=0)
    porcentaje_admin = Column(Numeric(5, 2), default=0)
    porcentaje_utilidad = Column(Numeric(5, 2), default=0)
    porcentaje_imprevisto = Column(Numeric(5, 2), default=0)
    valor_admin = Column(Numeric(15, 2), default=0)
    valor_utilidad = Column(Numeric(15, 2), default=0)
    valor_imprevisto = Column(Numeric(15, 2), default=0)
    
    # Datos adicionales (JSONB)
    subitems = Column(JSONB, default=[])
    preguntas_obligatorias = Column(JSONB, default=[])
    metadata_adicional = Column(JSONB, default={})
    
    # Auditoría DynamiaERP
    dynamia_creator = Column(String(200))
    dynamia_creation_date = Column(String(50))
    dynamia_creation_time = Column(String(50))
    dynamia_creation_timestamp = Column(String(100))
    dynamia_last_update = Column(String(100))
    dynamia_creation_instant = Column(String(100))
    dynamia_last_update_instant = Column(String(100))
    
    # Auditoría local
    fecha_sincronizacion = Column(DateTime, nullable=False)
    ultima_sincronizacion = Column(DateTime)
    sincronizado = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'dynamia_id': self.dynamia_id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'referencia': self.referencia,
            'descripcion': self.descripcion,
            'precio_venta': float(self.precio_venta) if self.precio_venta else 0,
            'costo_aproximado': float(self.costo_aproximado) if self.costo_aproximado else 0,
            'existencias_totales': float(self.existencias_totales) if self.existencias_totales else 0,
            'existencias_minimas': float(self.existencias_minimas) if self.existencias_minimas else 0,
            'existencias_maximas': float(self.existencias_maximas) if self.existencias_maximas else 0,
            'tipo_nombre': self.tipo_nombre,
            'marca_nombre': self.marca_nombre,
            'linea_nombre': self.linea_nombre,
            'codigo_barra': self.codigo_barra,
            'activo': self.activo,
            'vendible': self.vendible,
            'destacado': self.destacado,
            'impuesto_incluido': self.impuesto_incluido,
            'porcentaje_impuesto': float(self.porcentaje_impuesto) if self.porcentaje_impuesto else 0,
            'permite_descuentos': self.permite_descuentos,
            'porcentaje_descuento': float(self.porcentaje_descuento) if self.porcentaje_descuento else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ProductColumnConfig(Base):
    """Configuración de columnas visibles por usuario"""
    __tablename__ = "product_column_config"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    column_key = Column(String(100), nullable=False)
    column_label = Column(String(200), nullable=False)
    visible = Column(Boolean, default=True)
    order_index = Column(Integer, default=0)
    width = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'column_key': self.column_key,
            'column_label': self.column_label,
            'visible': self.visible,
            'order_index': self.order_index,
            'width': self.width
        }


class ProductSyncLog(Base):
    """Log de sincronizaciones de productos"""
    __tablename__ = "product_sync_log"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_date = Column(DateTime, nullable=False, index=True)
    total_products = Column(Integer, default=0)
    new_products = Column(Integer, default=0)
    updated_products = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    duration_seconds = Column(Numeric(10, 2))
    status = Column(String(50))
    error_message = Column(Text)
    details = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'sync_date': self.sync_date.isoformat() if self.sync_date else None,
            'total_products': self.total_products,
            'new_products': self.new_products,
            'updated_products': self.updated_products,
            'errors': self.errors,
            'duration_seconds': float(self.duration_seconds) if self.duration_seconds else 0,
            'status': self.status,
            'error_message': self.error_message,
            'details': self.details
        }


# Índice de búsqueda de texto completo
Index('idx_products_search', 
      func.to_tsvector('spanish', 
                       func.coalesce(Product.nombre, '') + ' ' + 
                       func.coalesce(Product.descripcion, '') + ' ' + 
                       func.coalesce(Product.codigo, '')),
      postgresql_using='gin')
