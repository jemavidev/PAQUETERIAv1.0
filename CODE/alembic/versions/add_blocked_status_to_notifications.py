"""add blocked status to notifications

Revision ID: add_blocked_status
Revises: 
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_blocked_status'
down_revision = None  # Actualizar con la última revisión
branch_labels = None
depends_on = None


def upgrade():
    """
    Agrega el estado 'blocked' al enum NotificationStatus
    y los nuevos eventos al enum NotificationEvent
    """
    
    # Para PostgreSQL
    op.execute("""
        ALTER TYPE notificationstatus ADD VALUE IF NOT EXISTS 'blocked';
    """)
    
    # Agregar nuevos eventos
    op.execute("""
        ALTER TYPE notificationevent ADD VALUE IF NOT EXISTS 'message_received';
    """)
    op.execute("""
        ALTER TYPE notificationevent ADD VALUE IF NOT EXISTS 'marketing';
    """)
    op.execute("""
        ALTER TYPE notificationevent ADD VALUE IF NOT EXISTS 'security_alert';
    """)
    op.execute("""
        ALTER TYPE notificationevent ADD VALUE IF NOT EXISTS 'account_locked';
    """)
    op.execute("""
        ALTER TYPE notificationevent ADD VALUE IF NOT EXISTS 'password_changed';
    """)
    op.execute("""
        ALTER TYPE notificationevent ADD VALUE IF NOT EXISTS 'password_reset';
    """)
    op.execute("""
        ALTER TYPE notificationevent ADD VALUE IF NOT EXISTS 'legal_notice';
    """)


def downgrade():
    """
    Nota: No se puede eliminar valores de un enum en PostgreSQL fácilmente.
    Si necesitas hacer downgrade, tendrías que recrear el enum completo.
    """
    pass
