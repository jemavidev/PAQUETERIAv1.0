"""create customer otp table

Revision ID: 0001_customer_otp
Revises: 
Create Date: 2025-01-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_customer_otp'
down_revision = None  # Se ejecutará independientemente
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla customer_otps
    op.create_table(
        'customer_otps',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=False),
        sa.Column('otp_code', sa.String(length=6), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_expired', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índice en customer_phone para búsquedas rápidas
    op.create_index(
        'ix_customer_otps_customer_phone',
        'customer_otps',
        ['customer_phone']
    )


def downgrade():
    # Eliminar índice
    op.drop_index('ix_customer_otps_customer_phone', table_name='customer_otps')
    
    # Eliminar tabla
    op.drop_table('customer_otps')
