"""Create invoice tables for CUFE management

Revision ID: create_invoice_tables
Revises: 
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_invoice_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nit', sa.String(20), nullable=False),
        sa.Column('razon_social', sa.String(255), nullable=False),
        sa.Column('nombre_comercial', sa.String(255), nullable=True),
        sa.Column('direccion', sa.String(255), nullable=True),
        sa.Column('telefono', sa.String(50), nullable=True),
        sa.Column('correo', sa.String(100), nullable=True),
        sa.Column('departamento', sa.String(100), nullable=True),
        sa.Column('ciudad', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suppliers_id'), 'suppliers', ['id'], unique=False)
    op.create_index(op.f('ix_suppliers_nit'), 'suppliers', ['nit'], unique=True)

    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cufe_cude', sa.String(100), nullable=False),
        sa.Column('document_type', sa.Enum('FACTURA', 'POS', name='documenttype'), nullable=False),
        sa.Column('numero_documento', sa.String(50), nullable=False),
        sa.Column('fecha_emision', sa.DateTime(), nullable=False),
        sa.Column('fecha_vencimiento', sa.DateTime(), nullable=True),
        sa.Column('forma_pago', sa.String(50), nullable=True),
        sa.Column('medio_pago', sa.String(50), nullable=True),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('subtotal', sa.Integer(), default=0),
        sa.Column('descuento', sa.Integer(), default=0),
        sa.Column('total_bruto', sa.Integer(), default=0),
        sa.Column('total_iva', sa.Integer(), default=0),
        sa.Column('total_otros_impuestos', sa.Integer(), default=0),
        sa.Column('total_neto', sa.Integer(), default=0),
        sa.Column('archivo_nombre', sa.String(255), nullable=True),
        sa.Column('archivo_path', sa.String(500), nullable=True),
        sa.Column('imported_by', sa.Integer(), nullable=True),
        sa.Column('imported_at', sa.DateTime(), nullable=True),
        sa.Column('is_validated', sa.Boolean(), default=False),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
        sa.ForeignKeyConstraint(['imported_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    op.create_index(op.f('ix_invoices_cufe_cude'), 'invoices', ['cufe_cude'], unique=True)

    # Create invoice_items table
    op.create_table(
        'invoice_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('numero_item', sa.Integer(), nullable=False),
        sa.Column('codigo', sa.String(50), nullable=True),
        sa.Column('descripcion', sa.String(500), nullable=False),
        sa.Column('unidad_medida', sa.String(50), nullable=True),
        sa.Column('cantidad', sa.Integer(), default=1),
        sa.Column('precio_unitario', sa.Integer(), default=0),
        sa.Column('descuento', sa.Integer(), default=0),
        sa.Column('recargo', sa.Integer(), default=0),
        sa.Column('iva_porcentaje', sa.Float(), default=0),
        sa.Column('iva_valor', sa.Integer(), default=0),
        sa.Column('inc_porcentaje', sa.Float(), default=0),
        sa.Column('inc_valor', sa.Integer(), default=0),
        sa.Column('valor_total', sa.Integer(), default=0),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_items_id'), 'invoice_items', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_invoice_items_id'), table_name='invoice_items')
    op.drop_table('invoice_items')
    op.drop_index(op.f('ix_invoices_cufe_cude'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_id'), table_name='invoices')
    op.drop_table('invoices')
    op.drop_index(op.f('ix_suppliers_nit'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_id'), table_name='suppliers')
    op.drop_table('suppliers')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS documenttype')
