# PAQUETES EL CLUB v1.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""fix_package_announcements_uuid_types

Revision ID: c147367f657f
Revises: 47be80bb0cf6
Create Date: 2025-09-21 17:12:21.234392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c147367f657f'
down_revision = 'b6183f4234d3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Primero eliminar las foreign keys existentes que causan conflictos
    op.execute("ALTER TABLE package_announcements_new DROP CONSTRAINT IF EXISTS package_announcements_new_customer_id_fkey")
    op.execute("ALTER TABLE package_announcements_new DROP CONSTRAINT IF EXISTS package_announcements_new_package_id_fkey")
    op.execute("ALTER TABLE package_announcements_new DROP CONSTRAINT IF EXISTS package_announcements_new_created_by_id_fkey")

    # Cambiar tipos de columnas UUID en package_announcements_new
    # Como las columnas son nullable y probablemente vacías, podemos cambiar el tipo directamente
    op.execute("ALTER TABLE package_announcements_new ALTER COLUMN customer_id TYPE UUID USING customer_id::text::uuid")
    op.execute("ALTER TABLE package_announcements_new ALTER COLUMN package_id TYPE UUID USING package_id::text::uuid")
    op.execute("ALTER TABLE package_announcements_new ALTER COLUMN created_by_id TYPE UUID USING created_by_id::text::uuid")


def downgrade() -> None:
    pass
