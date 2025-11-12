# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""fix_package_history_package_id_type

Revision ID: 52f07f833d6f
Revises: 31bf27ad341c
Create Date: 2025-09-25 16:16:15.533819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52f07f833d6f'
down_revision = '31bf27ad341c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change package_id from Integer to UUID to match packages.id
    op.alter_column('package_history', 'package_id',
                    type_=sa.UUID(),
                    postgresql_using='md5(package_id::text)::uuid')


def downgrade() -> None:
    # Change package_id back from UUID to Integer
    op.alter_column('package_history', 'package_id',
                    type_=sa.Integer(),
                    postgresql_using='(random() * 2147483647)::int')
