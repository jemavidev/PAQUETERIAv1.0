"""Add supplier_invoices table

Revision ID: add_supplier_invoices
Revises: 32325c92a96f
Create Date: 2026-01-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_supplier_invoices'
down_revision = '32325c92a96f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create supplier_invoices table
    op.create_table(
        'supplier_invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('original_file_hash', sa.String(64), nullable=True),
        sa.Column('original_file_path', sa.String(500), nullable=True),
        sa.Column('supplier_name', sa.String(255), nullable=True),
        sa.Column('supplier_nit', sa.String(20), nullable=True),
        sa.Column('invoice_number', sa.String(50), nullable=True),
        sa.Column('invoice_date', sa.DateTime(), nullable=True),
        sa.Column('total_amount', sa.Integer(), nullable=True),
        sa.Column('cufe', sa.String(100), nullable=True),
        sa.Column('cufe_source', sa.String(20), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('status_message', sa.Text(), nullable=True),
        sa.Column('dian_file_hash', sa.String(64), nullable=True),
        sa.Column('dian_downloaded_at', sa.DateTime(), nullable=True),
        sa.Column('processed_invoice_id', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['processed_invoice_id'], ['invoices.id']),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
    )
    
    # Create indexes
    op.create_index('ix_supplier_invoices_original_file_hash', 'supplier_invoices', ['original_file_hash'], unique=True)
    op.create_index('ix_supplier_invoices_cufe', 'supplier_invoices', ['cufe'])
    op.create_index('ix_supplier_invoices_status', 'supplier_invoices', ['status'])
    op.create_index('ix_supplier_invoices_supplier_name', 'supplier_invoices', ['supplier_name'])
    op.create_index('ix_supplier_invoices_supplier_nit', 'supplier_invoices', ['supplier_nit'])
    op.create_index('ix_supplier_invoices_invoice_date', 'supplier_invoices', ['invoice_date'])
    op.create_index('ix_supplier_invoices_uploaded_at', 'supplier_invoices', ['uploaded_at'])


def downgrade() -> None:
    op.drop_index('ix_supplier_invoices_uploaded_at', table_name='supplier_invoices')
    op.drop_index('ix_supplier_invoices_invoice_date', table_name='supplier_invoices')
    op.drop_index('ix_supplier_invoices_supplier_nit', table_name='supplier_invoices')
    op.drop_index('ix_supplier_invoices_supplier_name', table_name='supplier_invoices')
    op.drop_index('ix_supplier_invoices_status', table_name='supplier_invoices')
    op.drop_index('ix_supplier_invoices_cufe', table_name='supplier_invoices')
    op.drop_index('ix_supplier_invoices_original_file_hash', table_name='supplier_invoices')
    op.drop_table('supplier_invoices')
