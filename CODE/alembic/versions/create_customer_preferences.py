"""create customer preferences table

Revision ID: create_customer_prefs
Revises: add_blocked_status
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'create_customer_prefs'
down_revision = 'add_blocked_status'  # Actualizar con la última revisión
branch_labels = None
depends_on = None


def upgrade():
    """
    Crea la tabla customer_preferences para almacenar preferencias de clientes
    """
    op.create_table(
        'customer_preferences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('customer_id', UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('sms_notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notify_package_received', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notify_package_delivered', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notify_package_announced', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notify_payment_due', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('marketing_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_id'),
        sa.UniqueConstraint('token')
    )
    
    # Crear índices
    op.create_index('idx_customer_preferences_customer_id', 'customer_preferences', ['customer_id'])
    op.create_index('idx_customer_preferences_token', 'customer_preferences', ['token'])


def downgrade():
    """
    Elimina la tabla customer_preferences
    """
    op.drop_index('idx_customer_preferences_token', table_name='customer_preferences')
    op.drop_index('idx_customer_preferences_customer_id', table_name='customer_preferences')
    op.drop_table('customer_preferences')
