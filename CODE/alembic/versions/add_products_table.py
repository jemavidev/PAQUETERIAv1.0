"""add products table

Revision ID: add_products_001
Revises: 
Create Date: 2026-01-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers
revision = 'add_products_001'
down_revision = 'add_blocked_status'
branch_labels = None
depends_on = None


def upgrade():
    # Tabla principal de productos
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dynamia_id', sa.Integer(), unique=True, nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        
        # Información básica
        sa.Column('codigo', sa.String(100), nullable=False),
        sa.Column('nombre', sa.String(500), nullable=False),
        sa.Column('referencia', sa.String(200)),
        sa.Column('descripcion', sa.Text()),
        sa.Column('codigo_barra', sa.String(200)),
        sa.Column('codigo_referencia', sa.String(200)),
        sa.Column('codigo_lector', sa.String(200)),
        sa.Column('external_ref', sa.String(200)),
        
        # Precios y costos
        sa.Column('precio_venta', sa.Numeric(15, 2), default=0),
        sa.Column('costo_aproximado', sa.Numeric(15, 2), default=0),
        sa.Column('costo_efectivo', sa.Numeric(15, 2), default=0),
        sa.Column('precio_fijo', sa.Boolean(), default=False),
        sa.Column('precio_venta_calculado', sa.Boolean(), default=False),
        sa.Column('tiene_precio_temp', sa.Boolean(), default=False),
        sa.Column('usar_precio_sucursales', sa.Boolean(), default=False),
        
        # Impuestos
        sa.Column('impuesto_incluido', sa.Boolean(), default=False),
        sa.Column('porcentaje_impuesto', sa.Numeric(5, 2), default=0),
        sa.Column('exento_impuestos', sa.Boolean(), default=False),
        sa.Column('impuesto_fijo', sa.Numeric(15, 2), default=0),
        
        # Inventario
        sa.Column('existencias_totales', sa.Numeric(15, 2), default=0),
        sa.Column('existencias_minimas', sa.Numeric(15, 2), default=0),
        sa.Column('existencias_maximas', sa.Numeric(15, 2), default=0),
        sa.Column('existencias_externas', sa.Numeric(15, 2), default=0),
        
        # Clasificación - Tipo
        sa.Column('tipo_id', sa.Integer()),
        sa.Column('tipo_nombre', sa.String(200)),
        sa.Column('tipo_class', sa.String(500)),
        
        # Clasificación - Marca
        sa.Column('marca_id', sa.Integer()),
        sa.Column('marca_nombre', sa.String(200)),
        sa.Column('marca_class', sa.String(500)),
        
        # Clasificación - Línea
        sa.Column('linea_id', sa.Integer()),
        sa.Column('linea_nombre', sa.String(500)),
        sa.Column('linea_class', sa.String(500)),
        
        # Estados
        sa.Column('activo', sa.Boolean(), default=True),
        sa.Column('vendible', sa.Boolean(), default=True),
        sa.Column('comprable', sa.Boolean(), default=True),
        sa.Column('trasladable', sa.Boolean(), default=True),
        sa.Column('visualizable_web', sa.Boolean(), default=True),
        sa.Column('destacado', sa.Boolean(), default=False),
        sa.Column('permite_pedidos', sa.Boolean(), default=False),
        
        # Configuración de ventas
        sa.Column('cantidad_en_ventas', sa.Numeric(15, 2), default=1),
        sa.Column('cantidad_manual', sa.Boolean(), default=False),
        sa.Column('orden_en_ventas', sa.Integer(), default=0),
        sa.Column('permite_descuentos', sa.Boolean(), default=True),
        sa.Column('bloquear_descuentos', sa.Boolean(), default=False),
        sa.Column('porcentaje_descuento', sa.Numeric(5, 2), default=0),
        sa.Column('modo_precio', sa.String(50), default='POR_DEFECTO'),
        
        # Domicilios y delivery
        sa.Column('domicilios', sa.Boolean(), default=True),
        sa.Column('para_llevar', sa.Boolean(), default=True),
        sa.Column('bebida_alcoholica', sa.Boolean(), default=False),
        sa.Column('valor_envio', sa.Numeric(15, 2), default=0),
        
        # Comisiones
        sa.Column('comisionable', sa.Boolean(), default=False),
        sa.Column('descontar_en_comisiones', sa.Boolean(), default=False),
        sa.Column('porcentaje_comision', sa.Numeric(5, 2), default=0),
        sa.Column('total_comision_calculada', sa.Numeric(15, 2), default=0),
        
        # Configuraciones avanzadas
        sa.Column('compuesto', sa.Boolean(), default=False),
        sa.Column('compuesto_dinamico', sa.Boolean(), default=False),
        sa.Column('multi_presentaciones', sa.Boolean(), default=False),
        sa.Column('presentaciones_obligatorias', sa.Boolean(), default=False),
        sa.Column('usa_seriales', sa.Boolean(), default=False),
        sa.Column('usar_balanza', sa.Boolean(), default=False),
        sa.Column('autolotes', sa.Boolean(), default=False),
        sa.Column('usar_en_transformaciones', sa.Boolean(), default=False),
        sa.Column('usar_preguntas_obligatorias', sa.Boolean(), default=False),
        sa.Column('nombre_generado', sa.Boolean(), default=False),
        sa.Column('autocreado_proveedor', sa.Boolean(), default=False),
        
        # Gestión
        sa.Column('porcentaje_pmg', sa.Numeric(5, 2), default=0),
        sa.Column('porcentaje_admin', sa.Numeric(5, 2), default=0),
        sa.Column('porcentaje_utilidad', sa.Numeric(5, 2), default=0),
        sa.Column('porcentaje_imprevisto', sa.Numeric(5, 2), default=0),
        sa.Column('valor_admin', sa.Numeric(15, 2), default=0),
        sa.Column('valor_utilidad', sa.Numeric(15, 2), default=0),
        sa.Column('valor_imprevisto', sa.Numeric(15, 2), default=0),
        
        # Datos adicionales (JSONB para flexibilidad)
        sa.Column('subitems', JSONB, default=[]),
        sa.Column('preguntas_obligatorias', JSONB, default=[]),
        sa.Column('metadata_adicional', JSONB, default={}),
        
        # Auditoría DynamiaERP
        sa.Column('dynamia_creator', sa.String(200)),
        sa.Column('dynamia_creation_date', sa.String(50)),
        sa.Column('dynamia_creation_time', sa.String(50)),
        sa.Column('dynamia_creation_timestamp', sa.String(100)),
        sa.Column('dynamia_last_update', sa.String(100)),
        sa.Column('dynamia_creation_instant', sa.String(100)),
        sa.Column('dynamia_last_update_instant', sa.String(100)),
        
        # Auditoría local
        sa.Column('fecha_sincronizacion', sa.DateTime(), nullable=False),
        sa.Column('ultima_sincronizacion', sa.DateTime()),
        sa.Column('sincronizado', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Índices para búsqueda y filtrado eficiente
    op.create_index('idx_products_dynamia_id', 'products', ['dynamia_id'])
    op.create_index('idx_products_codigo', 'products', ['codigo'])
    op.create_index('idx_products_nombre', 'products', ['nombre'])
    op.create_index('idx_products_codigo_barra', 'products', ['codigo_barra'])
    op.create_index('idx_products_activo', 'products', ['activo'])
    op.create_index('idx_products_vendible', 'products', ['vendible'])
    op.create_index('idx_products_tipo_id', 'products', ['tipo_id'])
    op.create_index('idx_products_marca_id', 'products', ['marca_id'])
    op.create_index('idx_products_linea_id', 'products', ['linea_id'])
    op.create_index('idx_products_destacado', 'products', ['destacado'])
    
    # Índice de texto completo para búsqueda
    op.execute("""
        CREATE INDEX idx_products_search ON products 
        USING gin(to_tsvector('spanish', coalesce(nombre, '') || ' ' || coalesce(descripcion, '') || ' ' || coalesce(codigo, '')))
    """)
    
    # Tabla de configuración de columnas visibles por usuario
    op.create_table(
        'product_column_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('column_key', sa.String(100), nullable=False),
        sa.Column('column_label', sa.String(200), nullable=False),
        sa.Column('visible', sa.Boolean(), default=True),
        sa.Column('order_index', sa.Integer(), default=0),
        sa.Column('width', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'column_key', name='uq_user_column')
    )
    
    op.create_index('idx_column_config_user', 'product_column_config', ['user_id'])
    
    # Tabla de historial de sincronización
    op.create_table(
        'product_sync_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_date', sa.DateTime(), nullable=False),
        sa.Column('total_products', sa.Integer(), default=0),
        sa.Column('new_products', sa.Integer(), default=0),
        sa.Column('updated_products', sa.Integer(), default=0),
        sa.Column('errors', sa.Integer(), default=0),
        sa.Column('duration_seconds', sa.Numeric(10, 2)),
        sa.Column('status', sa.String(50)),
        sa.Column('error_message', sa.Text()),
        sa.Column('details', JSONB),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('idx_sync_log_date', 'product_sync_log', ['sync_date'])


def downgrade():
    op.drop_index('idx_sync_log_date', table_name='product_sync_log')
    op.drop_table('product_sync_log')
    
    op.drop_index('idx_column_config_user', table_name='product_column_config')
    op.drop_table('product_column_config')
    
    op.execute('DROP INDEX IF EXISTS idx_products_search')
    op.drop_index('idx_products_destacado', table_name='products')
    op.drop_index('idx_products_linea_id', table_name='products')
    op.drop_index('idx_products_marca_id', table_name='products')
    op.drop_index('idx_products_tipo_id', table_name='products')
    op.drop_index('idx_products_vendible', table_name='products')
    op.drop_index('idx_products_activo', table_name='products')
    op.drop_index('idx_products_codigo_barra', table_name='products')
    op.drop_index('idx_products_nombre', table_name='products')
    op.drop_index('idx_products_codigo', table_name='products')
    op.drop_index('idx_products_dynamia_id', table_name='products')
    op.drop_table('products')
