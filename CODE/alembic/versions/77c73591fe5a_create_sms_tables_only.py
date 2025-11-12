# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""create_sms_tables_only

Revision ID: 77c73591fe5a
Revises: c147367f657f
Create Date: 2025-09-21 17:26:25.779050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77c73591fe5a'
down_revision = 'c147367f657f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla de configuración SMS
    op.create_table('sms_configuration',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('account_id', sa.String(length=100), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=True),
        sa.Column('auth_url', sa.String(length=255), nullable=True),
        sa.Column('api_url', sa.String(length=255), nullable=True),
        sa.Column('default_sender', sa.String(length=20), nullable=False),
        sa.Column('max_message_length', sa.Integer(), nullable=False),
        sa.Column('enable_delivery_reports', sa.Boolean(), nullable=False),
        sa.Column('enable_test_mode', sa.Boolean(), nullable=False),
        sa.Column('daily_limit', sa.Integer(), nullable=False),
        sa.Column('monthly_limit', sa.Integer(), nullable=False),
        sa.Column('cost_per_sms_cents', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_test_at', sa.DateTime(), nullable=True),
        sa.Column('last_test_result', sa.Text(), nullable=True),
        sa.Column('updated_by_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla de plantillas de SMS
    op.create_table('sms_message_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('template_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('event_type', sa.Enum('PACKAGE_ANNOUNCED', 'PACKAGE_RECEIVED', 'PACKAGE_DELIVERED', 'PACKAGE_CANCELLED', 'PAYMENT_DUE', 'CUSTOM_MESSAGE', name='notificationevent'), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('subject', sa.String(length=200), nullable=True),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('available_variables', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('created_by_id', sa.UUID(), nullable=True),
        sa.Column('updated_by_id', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_id')
    )


def downgrade() -> None:
    pass
