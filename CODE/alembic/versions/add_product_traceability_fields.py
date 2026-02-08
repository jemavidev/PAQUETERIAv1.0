"""add product traceability fields

Revision ID: add_traceability_001
Revises: 20260130_invoice_v2
Create Date: 2026-02-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_traceability_001'
down_revision = '20260130_invoice_v2'  # La última migración del sistema de facturas V2
branch_labels = None
depends_on = None


def upgrade():
    """
    Agregar campos de trazabilidad a la tabla invoice_products_v2
    """
    # Agregar campos de trazabilidad
    op.add_column('invoice_products_v2', 
        sa.Column('proveedor_nombre', sa.String(255), nullable=True, 
                  comment='Nombre del proveedor (denormalizado para queries rápidas)')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('precio_anterior', sa.Numeric(15, 2), nullable=True,
                  comment='Precio unitario de la compra anterior')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('variacion_precio', sa.Numeric(10, 2), nullable=True,
                  comment='Porcentaje de variación respecto al precio anterior')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('variacion_tipo', sa.String(20), nullable=True,
                  comment='Tipo de variación: subio, bajo, igual, primera_compra')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('precio_promedio', sa.Numeric(15, 2), nullable=True,
                  comment='Precio promedio histórico del producto')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('total_compras_producto', sa.Integer, default=0, nullable=True,
                  comment='Número total de veces que se ha comprado este producto')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('ultimo_proveedor', sa.String(255), nullable=True,
                  comment='Nombre del proveedor de la última compra')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('dias_desde_ultima_compra', sa.Integer, nullable=True,
                  comment='Días transcurridos desde la última compra')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('precio_minimo_historico', sa.Numeric(15, 2), nullable=True,
                  comment='Precio mínimo histórico del producto')
    )
    
    op.add_column('invoice_products_v2', 
        sa.Column('precio_maximo_historico', sa.Numeric(15, 2), nullable=True,
                  comment='Precio máximo histórico del producto')
    )
    
    # Crear índices para mejorar performance de queries
    op.create_index('idx_products_codigo_producto', 'invoice_products_v2', ['codigo_producto'])
    op.create_index('idx_products_fecha_compra', 'invoice_products_v2', ['fecha_compra'])
    op.create_index('idx_products_proveedor', 'invoice_products_v2', ['proveedor_nombre'])
    op.create_index('idx_products_variacion_tipo', 'invoice_products_v2', ['variacion_tipo'])
    
    # Índice compuesto para búsquedas por código y fecha
    op.create_index('idx_products_codigo_fecha', 'invoice_products_v2', 
                    ['codigo_producto', 'fecha_compra'])


def downgrade():
    """
    Revertir cambios de trazabilidad
    """
    # Eliminar índices
    op.drop_index('idx_products_codigo_fecha', table_name='invoice_products_v2')
    op.drop_index('idx_products_variacion_tipo', table_name='invoice_products_v2')
    op.drop_index('idx_products_proveedor', table_name='invoice_products_v2')
    op.drop_index('idx_products_fecha_compra', table_name='invoice_products_v2')
    op.drop_index('idx_products_codigo_producto', table_name='invoice_products_v2')
    
    # Eliminar columnas
    op.drop_column('invoice_products_v2', 'precio_maximo_historico')
    op.drop_column('invoice_products_v2', 'precio_minimo_historico')
    op.drop_column('invoice_products_v2', 'dias_desde_ultima_compra')
    op.drop_column('invoice_products_v2', 'ultimo_proveedor')
    op.drop_column('invoice_products_v2', 'total_compras_producto')
    op.drop_column('invoice_products_v2', 'precio_promedio')
    op.drop_column('invoice_products_v2', 'variacion_tipo')
    op.drop_column('invoice_products_v2', 'variacion_precio')
    op.drop_column('invoice_products_v2', 'precio_anterior')
    op.drop_column('invoice_products_v2', 'proveedor_nombre')
