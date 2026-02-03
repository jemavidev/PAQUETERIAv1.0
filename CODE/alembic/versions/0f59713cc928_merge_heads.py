# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""merge heads

Revision ID: 0f59713cc928
Revises: 036db1d68539, 20260203_add_indexes
Create Date: 2026-02-03 14:15:28.669078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f59713cc928'
down_revision = ('036db1d68539', '20260203_add_indexes')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
