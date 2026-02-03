"""add indexes to invoices_v2 for performance

Revision ID: 20260203_add_indexes
Revises: 20260130_invoice_v2
Create Date: 2026-02-03 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260203_add_indexes'
down_revision = '20260130_invoice_v2'
branch_labels = None
depends_on = None


def upgrade():
    """
    Agregar índices para mejorar el rendimiento de consultas
    """
    # Índice en estado (filtro común)
    op.create_index(
        'ix_invoices_v2_estado',
        'invoices_v2',
        ['estado'],
        unique=False
    )
    
    # Índice en fecha_emision (ordenamiento y filtro)
    op.create_index(
        'ix_invoices_v2_fecha_emision',
        'invoices_v2',
        ['fecha_emision'],
        unique=False
    )
    
    # Índice en proveedor_nombre (búsqueda)
    op.create_index(
        'ix_invoices_v2_proveedor_nombre',
        'invoices_v2',
        ['proveedor_nombre'],
        unique=False
    )
    
    # Índice en numero_factura (búsqueda)
    op.create_index(
        'ix_invoices_v2_numero_factura',
        'invoices_v2',
        ['numero_factura'],
        unique=False
    )
    
    # Índice compuesto para consultas comunes (estado + fecha)
    op.create_index(
        'ix_invoices_v2_estado_fecha',
        'invoices_v2',
        ['estado', 'fecha_emision'],
        unique=False
    )


def downgrade():
    """
    Eliminar índices
    """
    op.drop_index('ix_invoices_v2_estado_fecha', table_name='invoices_v2')
    op.drop_index('ix_invoices_v2_numero_factura', table_name='invoices_v2')
    op.drop_index('ix_invoices_v2_proveedor_nombre', table_name='invoices_v2')
    op.drop_index('ix_invoices_v2_fecha_emision', table_name='invoices_v2')
    op.drop_index('ix_invoices_v2_estado', table_name='invoices_v2')
