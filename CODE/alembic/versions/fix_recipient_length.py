"""fix recipient length in notifications table

Revision ID: fix_recipient_length
Revises: 
Create Date: 2025-01-24 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_recipient_length'
down_revision = None  # Cambiar esto al último revision ID si es necesario
branch_labels = None
depends_on = None


def upgrade():
    # Aumentar el tamaño del campo recipient de VARCHAR(20) a VARCHAR(100)
    op.alter_column('notifications', 'recipient',
                    existing_type=sa.VARCHAR(length=20),
                    type_=sa.VARCHAR(length=100),
                    existing_nullable=False)
    
    print("✅ Campo 'recipient' actualizado de VARCHAR(20) a VARCHAR(100)")


def downgrade():
    # Revertir el cambio
    op.alter_column('notifications', 'recipient',
                    existing_type=sa.VARCHAR(length=100),
                    type_=sa.VARCHAR(length=20),
                    existing_nullable=False)
    
    print("⚠️  Campo 'recipient' revertido a VARCHAR(20)")
