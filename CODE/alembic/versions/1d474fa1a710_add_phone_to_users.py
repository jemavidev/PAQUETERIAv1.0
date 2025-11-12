# PAQUETES EL CLUB v1.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""add_phone_to_users

Revision ID: 1d474fa1a710
Revises: 8ae631ba2de6
Create Date: 2025-09-30 07:04:59.907018

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d474fa1a710'
down_revision = '8ae631ba2de6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add phone column to users table
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))


def downgrade() -> None:
    # Remove phone column from users table
    op.drop_column('users', 'phone')
