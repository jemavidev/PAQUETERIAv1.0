# PAQUETES EL CLUB v1.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""add_default_rates

Revision ID: 61567198240c
Revises: 2ffe0c3ab4e8
Create Date: 2025-11-05 16:37:01.877345

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime
import uuid


# revision identifiers, used by Alembic.
revision = '61567198240c'
down_revision = '2ffe0c3ab4e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create rates table
    op.create_table('rates',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('rate_type', sa.String(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('base_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('daily_storage_rate', sa.Numeric(10, 2), nullable=False),
        sa.Column('delivery_rate', sa.Numeric(10, 2), nullable=False),
        sa.Column('package_type_multiplier', sa.Numeric(10, 2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('valid_from', sa.DateTime(), nullable=False),
        sa.Column('valid_to', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index(op.f('ix_rates_rate_type'), 'rates', ['rate_type'], unique=False)
    op.create_index(op.f('ix_rates_is_active'), 'rates', ['is_active'], unique=False)
    
    # Reference to rates table for data insertion
    rates = sa.table('rates',
        sa.column('id', postgresql.UUID()),
        sa.column('rate_type', sa.String()),
        sa.column('name', sa.String()),
        sa.column('description', sa.String()),
        sa.column('base_price', sa.Numeric()),
        sa.column('daily_storage_rate', sa.Numeric()),
        sa.column('delivery_rate', sa.Numeric()),
        sa.column('package_type_multiplier', sa.Numeric()),
        sa.column('is_active', sa.Boolean()),
        sa.column('valid_from', sa.DateTime()),
        sa.column('valid_to', sa.DateTime()),
        sa.column('created_at', sa.DateTime()),
        sa.column('updated_at', sa.DateTime())
    )

    # Generate current timestamp
    now = datetime.now()

    # Insert default rates
    op.bulk_insert(rates, [
        {
            'id': uuid.uuid4(),
            'rate_type': 'package_type',
            'name': 'NORMAL',
            'description': 'Tarifa base para paquetes normales (hasta 30x30x30cm)',
            'base_price': 1800.00,
            'daily_storage_rate': 1000.00,
            'delivery_rate': 0.00,
            'package_type_multiplier': 1.0,
            'is_active': True,
            'valid_from': now,
            'valid_to': None,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': uuid.uuid4(),
            'rate_type': 'package_type',
            'name': 'EXTRA_DIMENSIONADO',
            'description': 'Tarifa base para paquetes extra dimensionados (más de 30x30x30cm)',
            'base_price': 2500.00,
            'daily_storage_rate': 1000.00,
            'delivery_rate': 0.00,
            'package_type_multiplier': 1.4,
            'is_active': True,
            'valid_from': now,
            'valid_to': None,
            'created_at': now,
            'updated_at': now
        }
    ])


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_rates_is_active'), table_name='rates')
    op.drop_index(op.f('ix_rates_rate_type'), table_name='rates')
    
    # Drop rates table
    op.drop_table('rates')
