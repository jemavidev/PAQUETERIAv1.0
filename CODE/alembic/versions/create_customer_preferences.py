"""create customer preferences table

Revision ID: create_customer_prefs
Revises: 0001_customer_otp
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'create_customer_prefs'
down_revision = '0001_customer_otp'
branch_labels = None
depends_on = None


def upgrade():
    """
    Crea la tabla customer_preferences para almacenar preferencias de clientes (idempotente)
    """
    op.execute("""
        CREATE TABLE IF NOT EXISTS customer_preferences (
            id SERIAL PRIMARY KEY,
            customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
            token VARCHAR(64) NOT NULL,
            sms_notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            email_notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            notify_package_received BOOLEAN NOT NULL DEFAULT TRUE,
            notify_package_delivered BOOLEAN NOT NULL DEFAULT TRUE,
            notify_package_announced BOOLEAN NOT NULL DEFAULT TRUE,
            notify_payment_due BOOLEAN NOT NULL DEFAULT TRUE,
            marketing_enabled BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(customer_id),
            UNIQUE(token)
        )
    """)
    
    # Crear índices
    op.execute("CREATE INDEX IF NOT EXISTS idx_customer_preferences_customer_id ON customer_preferences (customer_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_customer_preferences_token ON customer_preferences (token)")


def downgrade():
    """
    Elimina la tabla customer_preferences
    """
    op.execute("DROP INDEX IF EXISTS idx_customer_preferences_token")
    op.execute("DROP INDEX IF EXISTS idx_customer_preferences_customer_id")
    op.execute("DROP TABLE IF EXISTS customer_preferences")
