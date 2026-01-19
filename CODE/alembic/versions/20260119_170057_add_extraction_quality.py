"""add extraction quality to supplier invoices

Revision ID: 20260119_170057
Revises: 
Create Date: 2026-01-19 17:00:57

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260119_170057'
down_revision = None  # Actualizar con la última revisión
branch_labels = None
depends_on = None


def upgrade():
    # Verificar si la columna ya existe antes de agregarla
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('supplier_invoices')]
    
    if 'extraction_quality' not in columns:
        op.add_column('supplier_invoices', 
            sa.Column('extraction_quality', sa.Float(), nullable=True, server_default='0.0')
        )


def downgrade():
    op.drop_column('supplier_invoices', 'extraction_quality')
