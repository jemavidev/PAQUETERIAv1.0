# PAQUETES EL CLUB v4.0 - ALEMBIC SCRIPT TEMPLATE
# Template para generar archivos de migración

"""create_package_events_table

Revision ID: d8e9a7b1c3f2
Revises: 492767fdcdfb
Create Date: 2025-10-26 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd8e9a7b1c3f2'
down_revision = '492767fdcdfb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crea la tabla package_events para almacenar el historial completo 
    de todas las operaciones del ciclo de vida del paquete.
    """
    
    # Crear enum para EventType
    event_type_enum = postgresql.ENUM(
        'ANUNCIO', 'RECEPCION', 'ENTREGA', 'CANCELACION', 
        'MODIFICACION', 'IMAGEN_AGREGADA', 'NOTA_AGREGADA',
        name='eventtype',
        create_type=True
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Crear tabla package_events
    op.create_table(
        'package_events',
        
        # Identificadores
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('package_id', sa.Integer(), nullable=True),
        sa.Column('announcement_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Tipo de evento y timestamp
        sa.Column('event_type', event_type_enum, nullable=False),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False),
        
        # Datos del paquete
        sa.Column('tracking_number', sa.String(length=50), nullable=True),
        sa.Column('guide_number', sa.String(length=50), nullable=True),
        sa.Column('access_code', sa.String(length=20), nullable=True),
        sa.Column('tracking_code', sa.String(length=10), nullable=True),
        
        # Estados
        sa.Column('status_before', sa.String(length=50), nullable=True),
        sa.Column('status_after', sa.String(length=50), nullable=False),
        sa.Column('package_type', sa.String(length=50), nullable=True),
        sa.Column('package_condition', sa.String(length=50), nullable=True),
        
        # Ubicación física
        sa.Column('baroti', sa.String(length=2), nullable=True),
        
        # Datos del cliente
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_name', sa.String(length=100), nullable=True),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('customer_email', sa.String(length=100), nullable=True),
        
        # Datos financieros
        sa.Column('base_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('storage_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('storage_days', sa.Integer(), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        
        # Datos de pago
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('payment_received', sa.Boolean(), nullable=True, default=False),
        
        # Datos del operador
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('operator_name', sa.String(length=100), nullable=True),
        sa.Column('operator_role', sa.String(length=50), nullable=True),
        
        # Archivos y observaciones
        sa.Column('file_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('observations', sa.Text(), nullable=True),
        sa.Column('cancellation_reason', sa.String(length=100), nullable=True),
        
        # Datos adicionales
        sa.Column('additional_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False),
        
        # Claves primarias y foráneas
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['announcement_id'], ['package_announcements_new.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Crear índices para mejorar el rendimiento de consultas
    op.create_index('ix_package_events_package_id', 'package_events', ['package_id'])
    op.create_index('ix_package_events_event_type', 'package_events', ['event_type'])
    op.create_index('ix_package_events_event_timestamp', 'package_events', ['event_timestamp'])
    op.create_index('ix_package_events_tracking_number', 'package_events', ['tracking_number'])
    op.create_index('ix_package_events_guide_number', 'package_events', ['guide_number'])
    op.create_index('ix_package_events_tracking_code', 'package_events', ['tracking_code'])
    op.create_index('ix_package_events_customer_phone', 'package_events', ['customer_phone'])
    op.create_index('ix_package_events_operator_id', 'package_events', ['operator_id'])
    
    # Crear índice compuesto para consultas de fecha por tipo de evento
    op.create_index(
        'ix_package_events_event_type_timestamp',
        'package_events',
        ['event_type', 'event_timestamp']
    )


def downgrade() -> None:
    """
    Elimina la tabla package_events y el enum EventType
    """
    
    # Eliminar índices
    op.drop_index('ix_package_events_event_type_timestamp', table_name='package_events')
    op.drop_index('ix_package_events_operator_id', table_name='package_events')
    op.drop_index('ix_package_events_customer_phone', table_name='package_events')
    op.drop_index('ix_package_events_tracking_code', table_name='package_events')
    op.drop_index('ix_package_events_guide_number', table_name='package_events')
    op.drop_index('ix_package_events_tracking_number', table_name='package_events')
    op.drop_index('ix_package_events_event_timestamp', table_name='package_events')
    op.drop_index('ix_package_events_event_type', table_name='package_events')
    op.drop_index('ix_package_events_package_id', table_name='package_events')
    
    # Eliminar tabla
    op.drop_table('package_events')
    
    # Eliminar enum
    event_type_enum = postgresql.ENUM(name='eventtype')
    event_type_enum.drop(op.get_bind(), checkfirst=True)


