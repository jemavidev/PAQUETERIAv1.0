"""create cufe records table

Revision ID: create_cufe_records
Revises: integrate_invoices_products
Create Date: 2025-01-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_cufe_records'
down_revision = 'integrate_invoices_products'
branch_labels = None
depends_on = None


def upgrade():
    # Crear enum para estados de CUFE
    cufe_status_enum = postgresql.ENUM(
        'pending', 'downloading', 'downloaded', 'processing', 'processed', 'error',
        name='cufestatus',
        create_type=False
    )
    cufe_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Crear tabla cufe_records
    op.create_table(
        'cufe_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cufe', sa.String(length=96), nullable=False),
        sa.Column('status', cufe_status_enum, nullable=False, server_default='pending'),
        sa.Column('supplier_name', sa.String(length=255), nullable=True),
        sa.Column('invoice_number', sa.String(length=100), nullable=True),
        sa.Column('invoice_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices
    op.create_index('ix_cufe_records_id', 'cufe_records', ['id'], unique=False)
    op.create_index('ix_cufe_records_cufe', 'cufe_records', ['cufe'], unique=True)
    op.create_index('ix_cufe_records_status', 'cufe_records', ['status'], unique=False)
    op.create_index('ix_cufe_records_created_at', 'cufe_records', ['created_at'], unique=False)


def downgrade():
    # Eliminar índices
    op.drop_index('ix_cufe_records_created_at', table_name='cufe_records')
    op.drop_index('ix_cufe_records_status', table_name='cufe_records')
    op.drop_index('ix_cufe_records_cufe', table_name='cufe_records')
    op.drop_index('ix_cufe_records_id', table_name='cufe_records')
    
    # Eliminar tabla
    op.drop_table('cufe_records')
    
    # Eliminar enum
    cufe_status_enum = postgresql.ENUM(
        'pending', 'downloading', 'downloaded', 'processing', 'processed', 'error',
        name='cufestatus'
    )
    cufe_status_enum.drop(op.get_bind(), checkfirst=True)
