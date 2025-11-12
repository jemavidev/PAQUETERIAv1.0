# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""add_missing_notification_columns

Revision ID: 65750a31dccb
Revises: 77c73591fe5a
Create Date: 2025-09-21 17:30:27.204315

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65750a31dccb'
down_revision = '77c73591fe5a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columnas faltantes a la tabla notifications usando tipos simples
    op.add_column('notifications', sa.Column('customer_id', sa.UUID(), nullable=True))
    op.add_column('notifications', sa.Column('announcement_id', sa.UUID(), nullable=True))
    op.add_column('notifications', sa.Column('event_type', sa.String(length=50), nullable=True, server_default='CUSTOM_MESSAGE'))
    op.add_column('notifications', sa.Column('priority', sa.String(length=20), nullable=True, server_default='NORMAL'))
    op.add_column('notifications', sa.Column('recipient_name', sa.String(length=100), nullable=True))
    op.add_column('notifications', sa.Column('subject', sa.String(length=200), nullable=True))
    op.add_column('notifications', sa.Column('message_template', sa.String(length=100), nullable=True))
    op.add_column('notifications', sa.Column('delivered_at', sa.DateTime(), nullable=True))
    op.add_column('notifications', sa.Column('error_code', sa.String(length=50), nullable=True))
    op.add_column('notifications', sa.Column('provider_id', sa.String(length=100), nullable=True))
    op.add_column('notifications', sa.Column('provider_response', sa.Text(), nullable=True))
    op.add_column('notifications', sa.Column('cost_cents', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('notifications', sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('notifications', sa.Column('max_retries', sa.Integer(), nullable=True, server_default='3'))
    op.add_column('notifications', sa.Column('next_retry_at', sa.DateTime(), nullable=True))
    op.add_column('notifications', sa.Column('is_scheduled', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('notifications', sa.Column('scheduled_at', sa.DateTime(), nullable=True))
    op.add_column('notifications', sa.Column('is_test', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('notifications', sa.Column('created_by_id', sa.UUID(), nullable=True))
    op.add_column('notifications', sa.Column('updated_by_id', sa.UUID(), nullable=True))


def downgrade() -> None:
    pass
