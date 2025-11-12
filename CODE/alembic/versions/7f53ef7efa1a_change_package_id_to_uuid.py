# PAQUETES EL CLUB v1.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""change_package_id_to_uuid

Revision ID: 7f53ef7efa1a
Revises: f176b755cf10
Create Date: 2025-09-23 14:31:33.689797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f53ef7efa1a'
down_revision = 'f176b755cf10'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Cambiar la columna id de packages de INTEGER a UUID
    # Primero eliminar las foreign keys que referencian a packages.id (solo las que existen)
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_package_id_fkey")
    op.execute("ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_package_id_fkey")
    op.execute("ALTER TABLE file_uploads DROP CONSTRAINT IF EXISTS file_uploads_package_id_fkey")
    op.execute("ALTER TABLE package_announcements_new DROP CONSTRAINT IF EXISTS package_announcements_new_package_id_fkey")

    # Eliminar el default de la columna id antes de cambiar el tipo
    op.execute("ALTER TABLE packages ALTER COLUMN id DROP DEFAULT")

    # Cambiar las columnas foreign key de INTEGER a UUID antes de cambiar packages.id
    op.execute("ALTER TABLE notifications ALTER COLUMN package_id TYPE UUID USING md5(package_id::text)::uuid")
    op.execute("ALTER TABLE messages ALTER COLUMN package_id TYPE UUID USING md5(package_id::text)::uuid")
    op.execute("ALTER TABLE file_uploads ALTER COLUMN package_id TYPE UUID USING md5(package_id::text)::uuid")
    op.execute("ALTER TABLE package_announcements_new ALTER COLUMN package_id TYPE UUID USING md5(package_id::text)::uuid")

    # Cambiar el tipo de la columna id de INTEGER a UUID
    # Convertir los valores existentes a UUID
    op.execute("ALTER TABLE packages ALTER COLUMN id TYPE UUID USING md5(id::text)::uuid")

    # Recrear las foreign keys (solo las que existían)
    op.create_foreign_key('notifications_package_id_fkey', 'notifications', 'packages', ['package_id'], ['id'])
    op.create_foreign_key('messages_package_id_fkey', 'messages', 'packages', ['package_id'], ['id'])
    op.create_foreign_key('file_uploads_package_id_fkey', 'file_uploads', 'packages', ['package_id'], ['id'])
    op.create_foreign_key('package_announcements_new_package_id_fkey', 'package_announcements_new', 'packages', ['package_id'], ['id'])


def downgrade() -> None:
    # Revertir el cambio de UUID a INTEGER
    # Primero eliminar las foreign keys
    op.execute("ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_package_id_fkey")
    op.execute("ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_package_id_fkey")
    op.execute("ALTER TABLE file_uploads DROP CONSTRAINT IF EXISTS file_uploads_package_id_fkey")
    op.execute("ALTER TABLE package_history DROP CONSTRAINT IF EXISTS package_history_package_id_fkey")
    op.execute("ALTER TABLE package_announcements_new DROP CONSTRAINT IF EXISTS package_announcements_new_package_id_fkey")

    # Cambiar las columnas foreign key de UUID a INTEGER
    op.execute("ALTER TABLE notifications ALTER COLUMN package_id TYPE INTEGER USING (random() * 2147483647)::int")
    op.execute("ALTER TABLE messages ALTER COLUMN package_id TYPE INTEGER USING (random() * 2147483647)::int")
    op.execute("ALTER TABLE file_uploads ALTER COLUMN package_id TYPE INTEGER USING (random() * 2147483647)::int")
    op.execute("ALTER TABLE package_announcements_new ALTER COLUMN package_id TYPE INTEGER USING (random() * 2147483647)::int")

    # Cambiar de UUID a INTEGER (esto puede perder datos si hay UUIDs complejos)
    op.execute("ALTER TABLE packages ALTER COLUMN id TYPE INTEGER USING (random() * 2147483647)::int")

    # Recrear las foreign keys
    op.create_foreign_key('notifications_package_id_fkey', 'notifications', 'packages', ['package_id'], ['id'])
    op.create_foreign_key('messages_package_id_fkey', 'messages', 'packages', ['package_id'], ['id'])
    op.create_foreign_key('file_uploads_package_id_fkey', 'file_uploads', 'packages', ['package_id'], ['id'])
    op.execute("ALTER TABLE package_history ADD CONSTRAINT package_history_package_id_fkey FOREIGN KEY(package_id) REFERENCES packages (id)")
    op.create_foreign_key('package_announcements_new_package_id_fkey', 'package_announcements_new', 'packages', ['package_id'], ['id'])
