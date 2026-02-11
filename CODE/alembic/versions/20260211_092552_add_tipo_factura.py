"""add tipo_factura to invoices_v2

Revision ID: 20260211_092552
Revises: 536e9b775d34, add_supplier_invoices, create_customer_prefs, create_cufe_records, add_incremental_sync, add_products_001
Create Date: 2026-02-11 09:25:52

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260211_092552'
down_revision = (
    '536e9b775d34',           # merge traceability and invoice_v2
    'add_supplier_invoices',  # supplier invoices table
    'create_customer_prefs',  # customer preferences
    'create_cufe_records',    # cufe records
    'add_incremental_sync',   # incremental sync
    'add_products_001',       # products table
)
branch_labels = None
depends_on = None


def upgrade():
    # Agregar columna tipo_factura a invoices_v2
    op.add_column('invoices_v2', 
        sa.Column('tipo_factura', sa.String(20), nullable=False, server_default='reventa')
    )
    
    # Crear índice para búsquedas rápidas
    op.create_index('idx_invoices_tipo_factura', 'invoices_v2', ['tipo_factura'])


def downgrade():
    # Eliminar índice
    op.drop_index('idx_invoices_tipo_factura', 'invoices_v2')
    
    # Eliminar columna
    op.drop_column('invoices_v2', 'tipo_factura')
