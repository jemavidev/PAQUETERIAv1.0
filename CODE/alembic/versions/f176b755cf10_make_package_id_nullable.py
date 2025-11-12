# PAQUETES EL CLUB v1.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""make_package_id_nullable

Revision ID: f176b755cf10
Revises: 65750a31dccb
Create Date: 2025-09-21 18:57:18.818485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f176b755cf10'
down_revision = '65750a31dccb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Hacer que package_id permita valores NULL
    op.alter_column('notifications', 'package_id', nullable=True)


def downgrade() -> None:
    # Revertir: hacer que package_id no permita valores NULL
    op.alter_column('notifications', 'package_id', nullable=False)
