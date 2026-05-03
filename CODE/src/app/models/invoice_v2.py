"""
Modelos para el sistema de facturas V2
Sistema de 3 tabs: FACTURAS, CUFE, PRODUCTOS
"""
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Text, Integer, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class InvoiceV2(Base):
    """
    Tabla principal de facturas
    Almacena tanto datos del PDF del proveedor como del archivo DIAN
    """
    __tablename__ = "invoices_v2"
    
    # Primary Key - CUFE es inmutable
    cufe = Column(String(96), primary_key=True, nullable=False)

    # ===== CONTROL DE CUFE (NUEVO) =====
    # Origen del CUFE: automatico (del filename) | manual_usuario (ingresado por usuario)
    cufe_origen = Column(String(20), default='automatico', nullable=False)

    # Usuario confirma que el CUFE ingresado manualmente es correcto
    cufe_validado_usuario = Column(Boolean, default=False, nullable=False)

    # Código alternativo para archivos no estándar (CUDE, etc)
    codigo_alternativo = Column(String(100), nullable=True)
    codigo_alternativo_tipo = Column(String(20), nullable=True)  # 'CUDE' | 'OTRO'

    # Archivos
    archivo_proveedor_url = Column(Text, nullable=True)
    archivo_proveedor_s3_key = Column(String(500), nullable=True)
    archivo_dian_url = Column(Text, nullable=True)
    archivo_dian_s3_key = Column(String(500), nullable=True)
    
    # ===== DATOS DEL PDF DEL PROVEEDOR (TAB FACTURAS) =====
    # Campos básicos extraídos con OCR genérico
    proveedor_nombre = Column(String(255), nullable=True)
    proveedor_nit = Column(String(20), nullable=True)
    fecha_emision = Column(DateTime, nullable=True)
    numero_factura = Column(String(100), nullable=True)
    total_factura = Column(Numeric(15, 2), nullable=True)
    
    # JSON flexible para datos adicionales del proveedor
    proveedor_datos_raw = Column(JSONB, nullable=True)
    
    # ===== DATOS DEL ARCHIVO DIAN (TAB CUFE) =====
    dian_validado = Column(Boolean, default=False, nullable=False)
    dian_fecha_validacion = Column(DateTime, nullable=True)
    dian_tipo_documento = Column(String(50), nullable=True)
    dian_numero_documento = Column(String(100), nullable=True)
    
    # Emisor/Vendedor
    dian_emisor_razon_social = Column(String(255), nullable=True)
    dian_emisor_nit = Column(String(20), nullable=True)
    dian_emisor_tipo_contribuyente = Column(String(50), nullable=True)
    dian_emisor_regimen_fiscal = Column(String(50), nullable=True)
    dian_emisor_responsabilidad_tributaria = Column(String(200), nullable=True)
    dian_emisor_direccion = Column(Text, nullable=True)
    dian_emisor_ciudad = Column(String(100), nullable=True)
    dian_emisor_departamento = Column(String(100), nullable=True)
    dian_emisor_telefono = Column(String(50), nullable=True)
    dian_emisor_email = Column(String(255), nullable=True)
    
    # Adquiriente/Comprador
    dian_adquiriente_razon_social = Column(String(255), nullable=True)
    dian_adquiriente_nit = Column(String(20), nullable=True)
    dian_adquiriente_tipo_contribuyente = Column(String(50), nullable=True)
    dian_adquiriente_direccion = Column(Text, nullable=True)
    dian_adquiriente_ciudad = Column(String(100), nullable=True)
    
    # Condiciones comerciales
    dian_forma_pago = Column(String(50), nullable=True)
    dian_medio_pago = Column(String(100), nullable=True)
    dian_moneda = Column(String(10), nullable=True, default='COP')
    dian_tipo_operacion = Column(String(100), nullable=True)
    
    # Totales financieros
    dian_subtotal = Column(Numeric(15, 2), nullable=True)
    dian_total_bruto = Column(Numeric(15, 2), nullable=True)
    dian_total_iva = Column(Numeric(15, 2), nullable=True)
    dian_total_inc = Column(Numeric(15, 2), nullable=True)
    dian_total_bolsas = Column(Numeric(15, 2), nullable=True)
    dian_total_descuentos = Column(Numeric(15, 2), nullable=True)
    dian_total_recargos = Column(Numeric(15, 2), nullable=True)
    dian_total_neto = Column(Numeric(15, 2), nullable=True)
    
    # Información técnica
    dian_proveedor_tecnologico = Column(String(255), nullable=True)
    dian_proveedor_tecnologico_nit = Column(String(20), nullable=True)
    dian_resolucion_numero = Column(String(100), nullable=True)
    dian_resolucion_rango_desde = Column(String(50), nullable=True)
    dian_resolucion_rango_hasta = Column(String(50), nullable=True)
    dian_resolucion_vigencia = Column(String(100), nullable=True)
    dian_codigo_qr = Column(Text, nullable=True)
    
    # JSON flexible para datos completos DIAN
    dian_datos_raw = Column(JSONB, nullable=True)
    
    # Estado y metadatos
    estado = Column(String(20), default='pendiente_dian', nullable=False)
    # Estados: pendiente_dian, completo, error, sin_dian
    
    # Tipo de factura (para filtrar productos de reventa vs consumo)
    tipo_factura = Column(String(20), default='reventa', nullable=False, index=True)
    # Tipos: reventa, consumo, servicio, otro
    
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relación con productos
    productos = relationship("InvoiceProductV2", back_populates="factura", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InvoiceV2(cufe={self.cufe[:16]}..., proveedor={self.proveedor_nombre}, total={self.total_factura})>"
    
    def to_dict(self, include_productos=False):
        """Convierte el modelo a diccionario"""
        data = {
            'cufe': self.cufe,
            'cufe_origen': self.cufe_origen,
            'cufe_validado_usuario': self.cufe_validado_usuario,
            'codigo_alternativo': self.codigo_alternativo,
            'codigo_alternativo_tipo': self.codigo_alternativo_tipo,
            'archivo_proveedor_url': self.archivo_proveedor_url,
            'archivo_dian_url': self.archivo_dian_url,
            'proveedor_nombre': self.proveedor_nombre,
            'proveedor_nit': self.proveedor_nit,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'numero_factura': self.numero_factura,
            'total_factura': float(self.total_factura) if self.total_factura else None,
            'dian_validado': self.dian_validado,
            'dian_emisor_razon_social': self.dian_emisor_razon_social,
            'dian_total_neto': float(self.dian_total_neto) if self.dian_total_neto else None,
            'estado': self.estado,
            'tipo_factura': self.tipo_factura,
            'notas': self.notas,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_productos:
            data['productos'] = [p.to_dict() for p in self.productos]
        
        return data


class InvoiceProductV2(Base):
    """
    Tabla de productos de facturas
    Almacena el detalle de cada ítem comprado
    """
    __tablename__ = "invoice_products_v2"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cufe = Column(String(96), ForeignKey('invoices_v2.cufe', ondelete='CASCADE'), nullable=False)
    
    # Identificación del producto
    linea_numero = Column(Integer, nullable=True)
    codigo_producto = Column(String(100), nullable=True)  # EAN/UPC
    codigo_interno = Column(String(100), nullable=True)  # Referencia proveedor
    descripcion = Column(Text, nullable=True)
    
    # Cantidades y medidas
    cantidad = Column(Numeric(10, 2), nullable=True)
    unidad_medida = Column(String(50), nullable=True)
    unidad_medida_descripcion = Column(String(200), nullable=True)
    
    # Precios
    precio_unitario = Column(Numeric(15, 2), nullable=True)
    precio_unitario_base = Column(Numeric(15, 2), nullable=True)
    
    # Impuestos
    iva_porcentaje = Column(Numeric(5, 2), nullable=True)
    iva_valor = Column(Numeric(15, 2), nullable=True)
    inc_porcentaje = Column(Numeric(5, 2), nullable=True)
    inc_valor = Column(Numeric(15, 2), nullable=True)
    
    # Descuentos y recargos
    descuento_valor = Column(Numeric(15, 2), nullable=True)
    recargo_valor = Column(Numeric(15, 2), nullable=True)
    
    # Totales
    subtotal = Column(Numeric(15, 2), nullable=True)
    total_item = Column(Numeric(15, 2), nullable=True)
    
    # ===== CAMPOS DE TRAZABILIDAD =====
    # NOTA: Estos campos requieren ejecutar la migración: alembic upgrade head
    # Comentados temporalmente para compatibilidad con BD sin migración
    
    # Información del proveedor (denormalizado para queries rápidas)
    # proveedor_nombre = Column(String(255), nullable=True, index=True)
    
    # Análisis de precios
    # precio_anterior = Column(Numeric(15, 2), nullable=True, comment='Precio unitario de la compra anterior')
    # variacion_precio = Column(Numeric(10, 2), nullable=True, comment='% de variación respecto al precio anterior')
    # variacion_tipo = Column(String(20), nullable=True, index=True, comment='subio, bajo, igual, primera_compra')
    # precio_promedio = Column(Numeric(15, 2), nullable=True, comment='Precio promedio histórico')
    # precio_minimo_historico = Column(Numeric(15, 2), nullable=True, comment='Precio mínimo histórico')
    # precio_maximo_historico = Column(Numeric(15, 2), nullable=True, comment='Precio máximo histórico')
    
    # Estadísticas de compra
    # total_compras_producto = Column(Integer, default=0, nullable=True, comment='Total de veces comprado')
    # ultimo_proveedor = Column(String(255), nullable=True, comment='Proveedor de la última compra')
    # dias_desde_ultima_compra = Column(Integer, nullable=True, comment='Días desde última compra')
    
    # Metadatos
    fecha_compra = Column(Date, nullable=True, index=True)
    datos_raw = Column(JSONB, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relación con factura
    factura = relationship("InvoiceV2", back_populates="productos")
    
    def __repr__(self):
        return f"<InvoiceProductV2(id={self.id}, descripcion={self.descripcion[:30]}..., cantidad={self.cantidad})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        base_dict = {
            'id': self.id,
            'cufe': self.cufe,
            'linea_numero': self.linea_numero,
            'codigo_producto': self.codigo_producto,
            'codigo_interno': self.codigo_interno,
            'descripcion': self.descripcion,
            'cantidad': float(self.cantidad) if self.cantidad else None,
            'unidad_medida': self.unidad_medida,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else None,
            'iva_porcentaje': float(self.iva_porcentaje) if self.iva_porcentaje else None,
            'iva_valor': float(self.iva_valor) if self.iva_valor else None,
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'total_item': float(self.total_item) if self.total_item else None,
            'fecha_compra': self.fecha_compra.isoformat() if self.fecha_compra else None,
        }
        
        # Agregar campos de trazabilidad solo si existen (compatibilidad con BD sin migración)
        if hasattr(self, 'proveedor_nombre'):
            base_dict.update({
                'proveedor_nombre': self.proveedor_nombre,
                'precio_anterior': float(self.precio_anterior) if self.precio_anterior else None,
                'variacion_precio': float(self.variacion_precio) if self.variacion_precio else None,
                'variacion_tipo': self.variacion_tipo,
                'precio_promedio': float(self.precio_promedio) if self.precio_promedio else None,
                'precio_minimo_historico': float(self.precio_minimo_historico) if self.precio_minimo_historico else None,
                'precio_maximo_historico': float(self.precio_maximo_historico) if self.precio_maximo_historico else None,
                'total_compras_producto': self.total_compras_producto,
                'ultimo_proveedor': self.ultimo_proveedor,
                'dias_desde_ultima_compra': self.dias_desde_ultima_compra,
            })
        
        return base_dict
