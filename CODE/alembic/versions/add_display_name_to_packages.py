"""Add display_name column to packages table

Revision ID: add_display_name_001
Revises: 61567198240c
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_display_name_001'
down_revision = '61567198240c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columna display_name a la tabla packages
    # Usar IF NOT EXISTS para evitar errores si la columna ya existe
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='packages' AND column_name='display_name'
            ) THEN
                ALTER TABLE packages ADD COLUMN display_name VARCHAR(100) NULL;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Eliminar columna display_name de la tabla packages
    op.drop_column('packages', 'display_name')
