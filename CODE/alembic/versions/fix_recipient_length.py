"""fix recipient length in notifications table

Revision ID: fix_recipient_length
Revises: create_invoice_tables
Create Date: 2025-01-24 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_recipient_length'
down_revision = 'create_invoice_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Aumentar el tamaño del campo recipient de VARCHAR(20) a VARCHAR(100)
    # Idempotente: solo ejecuta si la columna existe y es menor a 100
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='notifications' AND column_name='recipient'
                AND character_maximum_length < 100
            ) THEN
                ALTER TABLE notifications ALTER COLUMN recipient TYPE VARCHAR(100);
            END IF;
        END $$;
    """)
    print("✅ Campo 'recipient' verificado/actualizado a VARCHAR(100)")


def downgrade():
    # Revertir el cambio
    op.alter_column('notifications', 'recipient',
                    existing_type=sa.VARCHAR(length=100),
                    type_=sa.VARCHAR(length=20),
                    existing_nullable=False)
    print("⚠️  Campo 'recipient' revertido a VARCHAR(20)")
