# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""make_customer_id_nullable_in_packages

Revision ID: a782e48f4e6c
Revises: 7f53ef7efa1a
Create Date: 2025-09-23 14:41:47.790366

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a782e48f4e6c'
down_revision = '7f53ef7efa1a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make customer_id nullable in packages table
    op.alter_column('packages', 'customer_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)


def downgrade() -> None:
    # Make customer_id not nullable in packages table (revert)
    op.alter_column('packages', 'customer_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)
