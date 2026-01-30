# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""merge invoice v2 and cufe status heads

Revision ID: 036db1d68539
Revises: 20260130_invoice_v2, add_cufe_dian_status
Create Date: 2026-01-30 10:03:01.825252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '036db1d68539'
down_revision = ('20260130_invoice_v2', 'add_cufe_dian_status')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
