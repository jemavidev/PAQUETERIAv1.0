"""add incremental sync fields

Revision ID: add_incremental_sync
Revises: enhance_invoice_system
Create Date: 2026-01-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_incremental_sync'
down_revision = 'enhance_invoice_system'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar campos a product_sync_log para sincronización incremental
    op.add_column('product_sync_log', 
        sa.Column('sync_type', sa.String(50), server_default='FULL', nullable=False)
    )
    op.add_column('product_sync_log', 
        sa.Column('last_product_date', sa.DateTime(), nullable=True)
    )
    
    # Crear índice para consultas rápidas de última sincronización
    op.create_index(
        'idx_product_sync_log_date_status', 
        'product_sync_log', 
        ['sync_date', 'status']
    )


def downgrade():
    # Eliminar índice
    op.drop_index('idx_product_sync_log_date_status', table_name='product_sync_log')
    
    # Eliminar columnas
    op.drop_column('product_sync_log', 'last_product_date')
    op.drop_column('product_sync_log', 'sync_type')
