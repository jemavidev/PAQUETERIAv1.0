# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""change_customer_id_to_uuid

Revision ID: c92f6a52ac8e
Revises: 52f07f833d6f
Create Date: 2025-09-26 09:05:24.415509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c92f6a52ac8e'
down_revision = '52f07f833d6f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable uuid-ossp extension for UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Drop foreign key constraints that reference customers.id
    op.execute("ALTER TABLE packages DROP CONSTRAINT IF EXISTS packages_customer_id_fkey")
    op.execute("ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_customer_id_fkey")

    # Drop the default value for id column before changing type
    op.execute("ALTER TABLE customers ALTER COLUMN id DROP DEFAULT")

    # Change foreign key columns from INTEGER to UUID first
    op.execute("ALTER TABLE packages ALTER COLUMN customer_id TYPE UUID USING md5(customer_id::text)::uuid")
    op.execute("ALTER TABLE messages ALTER COLUMN customer_id TYPE UUID USING md5(customer_id::text)::uuid")

    # Change customer ID from INTEGER to UUID
    # Since there are no existing customers (database was truncated), this is safe
    op.alter_column('customers', 'id',
                    existing_type=sa.INTEGER(),
                    type_=sa.UUID(),
                    postgresql_using='uuid_generate_v4()',
                    nullable=False)

    # Recreate the foreign key constraints
    op.create_foreign_key('packages_customer_id_fkey', 'packages', 'customers', ['customer_id'], ['id'])
    op.create_foreign_key('messages_customer_id_fkey', 'messages', 'customers', ['customer_id'], ['id'])


def downgrade() -> None:
    # Drop foreign key constraints
    op.execute("ALTER TABLE packages DROP CONSTRAINT IF EXISTS packages_customer_id_fkey")
    op.execute("ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_customer_id_fkey")

    # Change foreign key columns from UUID to INTEGER
    op.execute("ALTER TABLE packages ALTER COLUMN customer_id TYPE INTEGER USING (random() * 2147483647)::int")
    op.execute("ALTER TABLE messages ALTER COLUMN customer_id TYPE INTEGER USING (random() * 2147483647)::int")

    # Revert customer ID from UUID to INTEGER
    # This will require casting UUIDs back to integers, which may lose data
    op.alter_column('customers', 'id',
                    existing_type=sa.UUID(),
                    type_=sa.INTEGER(),
                    nullable=False)

    # Recreate the foreign key constraints
    op.create_foreign_key('packages_customer_id_fkey', 'packages', 'customers', ['customer_id'], ['id'])
    op.create_foreign_key('messages_customer_id_fkey', 'messages', 'customers', ['customer_id'], ['id'])
