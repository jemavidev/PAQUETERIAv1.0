"""create invoice system v2

Revision ID: 20260130_invoice_v2
Revises: 20260119_170057
Create Date: 2026-01-30 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '20260130_invoice_v2'
down_revision = '20260119_170057'
branch_labels = None
depends_on = None


def upgrade():
    # Habilitar extensión para búsqueda de texto PRIMERO
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
    
    # Tabla principal de facturas
    op.create_table(
        'invoices_v2',
        sa.Column('cufe', sa.String(96), primary_key=True, nullable=False),
        
        # Archivos
        sa.Column('archivo_proveedor_url', sa.Text, nullable=True),
        sa.Column('archivo_proveedor_s3_key', sa.String(500), nullable=True),
        sa.Column('archivo_dian_url', sa.Text, nullable=True),
        sa.Column('archivo_dian_s3_key', sa.String(500), nullable=True),
        
        # Datos básicos extraídos del PDF del proveedor (TAB FACTURAS)
        sa.Column('proveedor_nombre', sa.String(255), nullable=True),
        sa.Column('proveedor_nit', sa.String(20), nullable=True),
        sa.Column('fecha_emision', sa.DateTime, nullable=True),
        sa.Column('numero_factura', sa.String(100), nullable=True),
        sa.Column('total_factura', sa.Numeric(15, 2), nullable=True),
        
        # Datos extraídos del PDF del proveedor (raw JSON para flexibilidad)
        sa.Column('proveedor_datos_raw', JSONB, nullable=True, comment='Todos los datos extraídos del PDF proveedor'),
        
        # Datos completos del archivo DIAN (TAB CUFE)
        sa.Column('dian_validado', sa.Boolean, default=False, nullable=False),
        sa.Column('dian_fecha_validacion', sa.DateTime, nullable=True),
        sa.Column('dian_tipo_documento', sa.String(50), nullable=True, comment='FACTURA, POS, etc'),
        sa.Column('dian_numero_documento', sa.String(100), nullable=True),
        
        # Emisor/Vendedor (datos DIAN)
        sa.Column('dian_emisor_razon_social', sa.String(255), nullable=True),
        sa.Column('dian_emisor_nit', sa.String(20), nullable=True),
        sa.Column('dian_emisor_tipo_contribuyente', sa.String(50), nullable=True),
        sa.Column('dian_emisor_regimen_fiscal', sa.String(50), nullable=True),
        sa.Column('dian_emisor_responsabilidad_tributaria', sa.String(200), nullable=True),
        sa.Column('dian_emisor_direccion', sa.Text, nullable=True),
        sa.Column('dian_emisor_ciudad', sa.String(100), nullable=True),
        sa.Column('dian_emisor_departamento', sa.String(100), nullable=True),
        sa.Column('dian_emisor_telefono', sa.String(50), nullable=True),
        sa.Column('dian_emisor_email', sa.String(255), nullable=True),
        
        # Adquiriente/Comprador (datos DIAN)
        sa.Column('dian_adquiriente_razon_social', sa.String(255), nullable=True),
        sa.Column('dian_adquiriente_nit', sa.String(20), nullable=True),
        sa.Column('dian_adquiriente_tipo_contribuyente', sa.String(50), nullable=True),
        sa.Column('dian_adquiriente_direccion', sa.Text, nullable=True),
        sa.Column('dian_adquiriente_ciudad', sa.String(100), nullable=True),
        
        # Condiciones comerciales (datos DIAN)
        sa.Column('dian_forma_pago', sa.String(50), nullable=True, comment='Contado, Crédito'),
        sa.Column('dian_medio_pago', sa.String(100), nullable=True, comment='Efectivo, Tarjeta, etc'),
        sa.Column('dian_moneda', sa.String(10), nullable=True, default='COP'),
        sa.Column('dian_tipo_operacion', sa.String(100), nullable=True),
        
        # Totales financieros (datos DIAN)
        sa.Column('dian_subtotal', sa.Numeric(15, 2), nullable=True),
        sa.Column('dian_total_bruto', sa.Numeric(15, 2), nullable=True),
        sa.Column('dian_total_iva', sa.Numeric(15, 2), nullable=True),
        sa.Column('dian_total_inc', sa.Numeric(15, 2), nullable=True, comment='Impuesto al consumo'),
        sa.Column('dian_total_bolsas', sa.Numeric(15, 2), nullable=True),
        sa.Column('dian_total_descuentos', sa.Numeric(15, 2), nullable=True),
        sa.Column('dian_total_recargos', sa.Numeric(15, 2), nullable=True),
        sa.Column('dian_total_neto', sa.Numeric(15, 2), nullable=True),
        
        # Información técnica (datos DIAN)
        sa.Column('dian_proveedor_tecnologico', sa.String(255), nullable=True),
        sa.Column('dian_proveedor_tecnologico_nit', sa.String(20), nullable=True),
        sa.Column('dian_resolucion_numero', sa.String(100), nullable=True),
        sa.Column('dian_resolucion_rango_desde', sa.String(50), nullable=True),
        sa.Column('dian_resolucion_rango_hasta', sa.String(50), nullable=True),
        sa.Column('dian_resolucion_vigencia', sa.String(100), nullable=True),
        sa.Column('dian_codigo_qr', sa.Text, nullable=True),
        
        # Datos completos del archivo DIAN (raw JSON para flexibilidad)
        sa.Column('dian_datos_raw', JSONB, nullable=True, comment='Todos los datos extraídos del archivo DIAN'),
        
        # Estado y metadatos
        sa.Column('estado', sa.String(20), default='pendiente_dian', nullable=False, 
                  comment='pendiente_dian, completo, error, sin_dian'),
        sa.Column('notas', sa.Text, nullable=True, comment='Notas editables por el usuario'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        
        # Índices
        sa.Index('idx_invoices_v2_proveedor_nombre', 'proveedor_nombre'),
        sa.Index('idx_invoices_v2_fecha_emision', 'fecha_emision'),
        sa.Index('idx_invoices_v2_numero_factura', 'numero_factura'),
        sa.Index('idx_invoices_v2_estado', 'estado'),
        sa.Index('idx_invoices_v2_dian_validado', 'dian_validado'),
    )
    
    # Tabla de productos
    op.create_table(
        'invoice_products_v2',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('cufe', sa.String(96), sa.ForeignKey('invoices_v2.cufe', ondelete='CASCADE'), nullable=False),
        
        # Identificación del producto
        sa.Column('linea_numero', sa.Integer, nullable=True, comment='Orden en la factura'),
        sa.Column('codigo_producto', sa.String(100), nullable=True, comment='EAN/UPC del archivo DIAN'),
        sa.Column('codigo_interno', sa.String(100), nullable=True, comment='Referencia interna del proveedor'),
        sa.Column('descripcion', sa.Text, nullable=True),
        
        # Cantidades y medidas
        sa.Column('cantidad', sa.Numeric(10, 2), nullable=True),
        sa.Column('unidad_medida', sa.String(50), nullable=True, comment='NIU, UND, etc'),
        sa.Column('unidad_medida_descripcion', sa.String(200), nullable=True),
        
        # Precios
        sa.Column('precio_unitario', sa.Numeric(15, 2), nullable=True),
        sa.Column('precio_unitario_base', sa.Numeric(15, 2), nullable=True, comment='Precio sin impuestos'),
        
        # Impuestos
        sa.Column('iva_porcentaje', sa.Numeric(5, 2), nullable=True),
        sa.Column('iva_valor', sa.Numeric(15, 2), nullable=True),
        sa.Column('inc_porcentaje', sa.Numeric(5, 2), nullable=True),
        sa.Column('inc_valor', sa.Numeric(15, 2), nullable=True),
        
        # Descuentos y recargos
        sa.Column('descuento_valor', sa.Numeric(15, 2), nullable=True),
        sa.Column('recargo_valor', sa.Numeric(15, 2), nullable=True),
        
        # Totales
        sa.Column('subtotal', sa.Numeric(15, 2), nullable=True, comment='Cantidad * Precio base'),
        sa.Column('total_item', sa.Numeric(15, 2), nullable=True, comment='Total con impuestos'),
        
        # Metadatos
        sa.Column('fecha_compra', sa.Date, nullable=True),
        sa.Column('datos_raw', JSONB, nullable=True, comment='Datos adicionales del producto'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        
        # Índices para búsqueda eficiente
        sa.Index('idx_invoice_products_v2_cufe', 'cufe'),
        sa.Index('idx_invoice_products_v2_codigo_producto', 'codigo_producto'),
        sa.Index('idx_invoice_products_v2_descripcion', 'descripcion', postgresql_using='gin', postgresql_ops={'descripcion': 'gin_trgm_ops'}),
        sa.Index('idx_invoice_products_v2_fecha_compra', 'fecha_compra'),
    )


def downgrade():
    op.drop_table('invoice_products_v2')
    op.drop_table('invoices_v2')
