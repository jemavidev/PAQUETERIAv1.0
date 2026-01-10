"""create customer otp table

Revision ID: 0001_customer_otp
Revises: fix_recipient_length
Create Date: 2025-01-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_customer_otp'
down_revision = 'fix_recipient_length'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla customer_otps (idempotente)
    op.execute("""
        CREATE TABLE IF NOT EXISTS customer_otps (
            id UUID PRIMARY KEY,
            customer_phone VARCHAR(20) NOT NULL,
            otp_code VARCHAR(6) NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            is_expired BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            verified_at TIMESTAMP
        )
    """)
    
    # Crear índice en customer_phone para búsquedas rápidas
    op.execute("CREATE INDEX IF NOT EXISTS ix_customer_otps_customer_phone ON customer_otps (customer_phone)")


def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_customer_otps_customer_phone")
    op.execute("DROP TABLE IF EXISTS customer_otps")
