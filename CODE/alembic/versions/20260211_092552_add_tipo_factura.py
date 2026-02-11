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
    # Verificar si la columna ya existe antes de agregarla
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('invoices_v2')]
    
    if 'tipo_factura' not in columns:
        # Agregar columna tipo_factura a invoices_v2
        op.add_column('invoices_v2', 
            sa.Column('tipo_factura', sa.String(20), nullable=False, server_default='reventa')
        )
        print("✅ Columna 'tipo_factura' agregada")
    else:
        print("ℹ️  Columna 'tipo_factura' ya existe, saltando...")
    
    # Verificar si el índice ya existe antes de crearlo
    indexes = [idx['name'] for idx in inspector.get_indexes('invoices_v2')]
    
    if 'idx_invoices_tipo_factura' not in indexes:
        # Crear índice para búsquedas rápidas
        op.create_index('idx_invoices_tipo_factura', 'invoices_v2', ['tipo_factura'])
        print("✅ Índice 'idx_invoices_tipo_factura' creado")
    else:
        print("ℹ️  Índice 'idx_invoices_tipo_factura' ya existe, saltando...")


def downgrade():
    # Verificar si el índice existe antes de eliminarlo
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    indexes = [idx['name'] for idx in inspector.get_indexes('invoices_v2')]
    
    if 'idx_invoices_tipo_factura' in indexes:
        # Eliminar índice
        op.drop_index('idx_invoices_tipo_factura', 'invoices_v2')
    
    # Verificar si la columna existe antes de eliminarla
    columns = [col['name'] for col in inspector.get_columns('invoices_v2')]
    
    if 'tipo_factura' in columns:
        # Eliminar columna
        op.drop_column('invoices_v2', 'tipo_factura')
