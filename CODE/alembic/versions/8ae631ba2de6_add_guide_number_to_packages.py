# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""add_guide_number_to_packages

Revision ID: 8ae631ba2de6
Revises: c92f6a52ac8e
Create Date: 2025-09-27 06:56:11.576544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ae631ba2de6'
down_revision = 'c92f6a52ac8e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add guide_number column to packages table
    op.add_column('packages', sa.Column('guide_number', sa.String(50), unique=True, nullable=True, index=True))


def downgrade() -> None:
    # Remove guide_number column from packages table
    op.drop_column('packages', 'guide_number')
