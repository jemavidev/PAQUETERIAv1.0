# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""merge heads

Revision ID: 32325c92a96f
Revises: add_incremental_sync, add_products_001, create_customer_prefs
Create Date: 2026-01-13 20:36:12.545501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32325c92a96f'
down_revision = ('add_incremental_sync', 'add_products_001', 'create_customer_prefs')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
