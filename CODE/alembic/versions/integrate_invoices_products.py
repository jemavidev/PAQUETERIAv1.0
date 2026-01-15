"""Integrate invoices with products and supplier_invoices

Revision ID: integrate_invoices_products
Revises: add_supplier_invoices
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'integrate_invoices_products'
down_revision = 'add_supplier_invoices'  # Apunta a la migración de supplier_invoices
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Agregar campos de comprador a invoices
    op.add_column('invoices', sa.Column('buyer_nit', sa.String(20), nullable=True))
    op.add_column('invoices', sa.Column('buyer_razon_social', sa.String(255), nullable=True))
    op.add_column('invoices', sa.Column('buyer_direccion', sa.String(255), nullable=True))
    op.add_column('invoices', sa.Column('is_papyrus_buyer', sa.Boolean(), default=False, nullable=True))
    
    # 2. Agregar relación con supplier_invoices
    op.add_column('invoices', sa.Column('supplier_invoice_id', sa.Integer(), nullable=True))
    
    # 3. Agregar campos de matching a invoice_items
    op.add_column('invoice_items', sa.Column('product_id', sa.Integer(), nullable=True))
    op.add_column('invoice_items', sa.Column('matched_with_catalog', sa.Boolean(), default=False, nullable=True))
    op.add_column('invoice_items', sa.Column('match_confidence', sa.Float(), default=0.0, nullable=True))
    op.add_column('invoice_items', sa.Column('match_method', sa.String(50), nullable=True))
    
    # 4. Crear índices
    op.create_index('ix_invoices_buyer_nit', 'invoices', ['buyer_nit'])
    op.create_index('ix_invoices_is_papyrus_buyer', 'invoices', ['is_papyrus_buyer'])
    op.create_index('ix_invoices_supplier_invoice_id', 'invoices', ['supplier_invoice_id'])
    op.create_index('ix_invoice_items_product_id', 'invoice_items', ['product_id'])
    op.create_index('ix_invoice_items_matched_with_catalog', 'invoice_items', ['matched_with_catalog'])
    
    # 5. Crear foreign keys
    op.create_foreign_key(
        'fk_invoices_supplier_invoice_id',
        'invoices', 'supplier_invoices',
        ['supplier_invoice_id'], ['id'],
        ondelete='SET NULL'
    )
    
    op.create_foreign_key(
        'fk_invoice_items_product_id',
        'invoice_items', 'products',
        ['product_id'], ['id'],
        ondelete='SET NULL'
    )
    
    print("✅ Migración completada: Integración de facturas con productos")


def downgrade() -> None:
    # Eliminar foreign keys
    op.drop_constraint('fk_invoice_items_product_id', 'invoice_items', type_='foreignkey')
    op.drop_constraint('fk_invoices_supplier_invoice_id', 'invoices', type_='foreignkey')
    
    # Eliminar índices
    op.drop_index('ix_invoice_items_matched_with_catalog', table_name='invoice_items')
    op.drop_index('ix_invoice_items_product_id', table_name='invoice_items')
    op.drop_index('ix_invoices_supplier_invoice_id', table_name='invoices')
    op.drop_index('ix_invoices_is_papyrus_buyer', table_name='invoices')
    op.drop_index('ix_invoices_buyer_nit', table_name='invoices')
    
    # Eliminar columnas de invoice_items
    op.drop_column('invoice_items', 'match_method')
    op.drop_column('invoice_items', 'match_confidence')
    op.drop_column('invoice_items', 'matched_with_catalog')
    op.drop_column('invoice_items', 'product_id')
    
    # Eliminar columnas de invoices
    op.drop_column('invoices', 'supplier_invoice_id')
    op.drop_column('invoices', 'is_papyrus_buyer')
    op.drop_column('invoices', 'buyer_direccion')
    op.drop_column('invoices', 'buyer_razon_social')
    op.drop_column('invoices', 'buyer_nit')
