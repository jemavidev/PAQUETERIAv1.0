"""add_cufe_dian_status_fields

Revision ID: add_cufe_dian_status
Revises: 20260119_170057, create_cufe_records
Create Date: 2026-01-20 14:00:00.000000

Agrega campos para rastrear el estado del CUFE y el archivo DIAN
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_cufe_dian_status'
down_revision = ('20260119_170057', 'create_cufe_records')
branch_labels = None
depends_on = None


def upgrade():
    # Crear enum para estado CUFE
    cufe_status_enum = postgresql.ENUM(
        'extracted',      # CUFE extraído del PDF proveedor
        'manual',         # CUFE agregado manualmente
        'validated',      # CUFE validado con archivo DIAN
        'missing',        # Sin CUFE
        'error',          # Error al extraer CUFE
        name='cufestatus',
        create_type=False
    )
    cufe_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Crear enum para estado DIAN
    dian_status_enum = postgresql.ENUM(
        'pending',        # Pendiente de obtener de DIAN
        'downloading',    # Descargando de DIAN
        'downloaded',     # PDF DIAN descargado
        'processed',      # PDF DIAN procesado
        'error',          # Error al procesar DIAN
        'not_required',   # No requiere archivo DIAN
        name='dianstatus',
        create_type=False
    )
    dian_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Agregar columnas a la tabla invoices
    op.add_column('invoices', sa.Column('cufe_status', sa.Enum('extracted', 'manual', 'validated', 'missing', 'error', name='cufestatus'), nullable=True))
    op.add_column('invoices', sa.Column('dian_status', sa.Enum('pending', 'downloading', 'downloaded', 'processed', 'error', 'not_required', name='dianstatus'), nullable=True))
    op.add_column('invoices', sa.Column('dian_pdf_id', sa.Integer(), nullable=True))
    op.add_column('invoices', sa.Column('cufe_source', sa.String(20), nullable=True))  # 'extracted', 'manual', 'dian'
    
    # Crear índices
    op.create_index('ix_invoices_cufe_status', 'invoices', ['cufe_status'])
    op.create_index('ix_invoices_dian_status', 'invoices', ['dian_status'])
    op.create_index('ix_invoices_dian_pdf_id', 'invoices', ['dian_pdf_id'])
    
    # Actualizar registros existentes con valores por defecto
    op.execute("""
        UPDATE invoices 
        SET cufe_status = 'extracted',
            dian_status = CASE 
                WHEN supplier_invoice_id IS NOT NULL THEN 'processed'
                ELSE 'pending'
            END,
            cufe_source = 'extracted'
        WHERE cufe_status IS NULL
    """)


def downgrade():
    # Eliminar índices
    op.drop_index('ix_invoices_dian_pdf_id', 'invoices')
    op.drop_index('ix_invoices_dian_status', 'invoices')
    op.drop_index('ix_invoices_cufe_status', 'invoices')
    
    # Eliminar columnas
    op.drop_column('invoices', 'cufe_source')
    op.drop_column('invoices', 'dian_pdf_id')
    op.drop_column('invoices', 'dian_status')
    op.drop_column('invoices', 'cufe_status')
    
    # Eliminar enums
    sa.Enum(name='dianstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='cufestatus').drop(op.get_bind(), checkfirst=True)
