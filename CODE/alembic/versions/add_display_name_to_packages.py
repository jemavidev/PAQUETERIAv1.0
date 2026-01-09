"""Add display_name column to packages table

Revision ID: add_display_name_001
Revises: d8e9a7b1c3f2
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_display_name_001'
down_revision = 'd8e9a7b1c3f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columna display_name a la tabla packages
    op.add_column('packages', sa.Column('display_name', sa.String(100), nullable=True))


def downgrade() -> None:
    # Eliminar columna display_name de la tabla packages
    op.drop_column('packages', 'display_name')
