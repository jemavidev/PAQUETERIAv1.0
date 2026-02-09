# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""merge_traceability_and_invoice_v2

Revision ID: 536e9b775d34
Revises: 036db1d68539, add_traceability_001
Create Date: 2026-02-09 15:16:24.312073

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '536e9b775d34'
down_revision = ('036db1d68539', 'add_traceability_001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
