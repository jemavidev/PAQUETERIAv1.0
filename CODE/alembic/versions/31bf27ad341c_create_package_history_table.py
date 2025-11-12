# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""create_package_history_table

Revision ID: 31bf27ad341c
Revises: a782e48f4e6c
Create Date: 2025-09-23 14:45:08.429487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31bf27ad341c'
down_revision = 'a782e48f4e6c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create package_history table
    op.create_table('package_history',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('package_id', sa.UUID(), nullable=False),
        sa.Column('previous_status', sa.String(length=50), nullable=True),
        sa.Column('new_status', sa.String(length=50), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.Column('changed_by', sa.String(length=100), nullable=True),
        sa.Column('additional_data', sa.JSON(), nullable=True),
        sa.Column('observations', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop package_history table
    op.drop_table('package_history')
