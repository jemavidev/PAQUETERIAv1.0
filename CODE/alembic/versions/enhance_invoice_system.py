"""Enhance invoice system with IVA tracking, validation, and indexes

Revision ID: enhance_invoice_system
Revises: create_invoice_tables
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'enhance_invoice_system'
down_revision = 'create_invoice_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========================================
    # NUEVOS ÍNDICES PARA BÚSQUEDAS EFICIENTES
    # ========================================
    
    # Índices en invoices
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoices_fecha_emision ON invoices (fecha_emision)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoices_supplier_id ON invoices (supplier_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoices_numero_documento ON invoices (numero_documento)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoices_total_neto ON invoices (total_neto)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoices_imported_at ON invoices (imported_at)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoices_document_type ON invoices (document_type)")
    
    # Índices en invoice_items
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoice_items_invoice_id ON invoice_items (invoice_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoice_items_codigo ON invoice_items (codigo)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoice_items_iva_porcentaje ON invoice_items (iva_porcentaje)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoice_items_precio_unitario ON invoice_items (precio_unitario)")
    
    # Índices en suppliers
    op.execute("CREATE INDEX IF NOT EXISTS ix_suppliers_razon_social ON suppliers (razon_social)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_suppliers_ciudad ON suppliers (ciudad)")
    
    # ========================================
    # NUEVOS CAMPOS EN INVOICES
    # ========================================
    
    # Estado del archivo importado
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'importstatus') THEN
                CREATE TYPE importstatus AS ENUM ('valid', 'warning', 'error', 'replaced');
            END IF;
        END $$;
    """)
    
    op.execute("""
        ALTER TABLE invoices 
        ADD COLUMN IF NOT EXISTS import_status VARCHAR(20) DEFAULT 'valid'
    """)
    
    op.execute("""
        ALTER TABLE invoices 
        ADD COLUMN IF NOT EXISTS import_errors JSONB DEFAULT '[]'::jsonb
    """)
    
    op.execute("""
        ALTER TABLE invoices 
        ADD COLUMN IF NOT EXISTS import_warnings JSONB DEFAULT '[]'::jsonb
    """)
    
    op.execute("""
        ALTER TABLE invoices 
        ADD COLUMN IF NOT EXISTS replaced_by_id INTEGER REFERENCES invoices(id)
    """)
    
    op.execute("""
        ALTER TABLE invoices 
        ADD COLUMN IF NOT EXISTS replaces_id INTEGER REFERENCES invoices(id)
    """)
    
    op.execute("""
        ALTER TABLE invoices 
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE
    """)
    
    op.execute("""
        ALTER TABLE invoices 
        ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64)
    """)
    
    # ========================================
    # NUEVOS CAMPOS EN INVOICE_ITEMS - IVA INFORMATIVO
    # ========================================
    
    # Marcador de IVA incluido (informativo)
    op.execute("""
        ALTER TABLE invoice_items 
        ADD COLUMN IF NOT EXISTS iva_incluido BOOLEAN DEFAULT NULL
    """)
    
    # Precio base sin IVA (calculado)
    op.execute("""
        ALTER TABLE invoice_items 
        ADD COLUMN IF NOT EXISTS precio_base INTEGER DEFAULT 0
    """)
    
    # Notas/observaciones del item
    op.execute("""
        ALTER TABLE invoice_items 
        ADD COLUMN IF NOT EXISTS notas TEXT
    """)
    
    # Flag de irregularidad detectada
    op.execute("""
        ALTER TABLE invoice_items 
        ADD COLUMN IF NOT EXISTS tiene_irregularidad BOOLEAN DEFAULT FALSE
    """)
    
    op.execute("""
        ALTER TABLE invoice_items 
        ADD COLUMN IF NOT EXISTS tipo_irregularidad VARCHAR(50)
    """)
    
    # ========================================
    # TABLA DE IRREGULARIDADES
    # ========================================
    
    op.execute("""
        CREATE TABLE IF NOT EXISTS invoice_irregularities (
            id SERIAL PRIMARY KEY,
            invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
            item_id INTEGER REFERENCES invoice_items(id) ON DELETE CASCADE,
            tipo VARCHAR(50) NOT NULL,
            severidad VARCHAR(20) DEFAULT 'warning',
            descripcion TEXT NOT NULL,
            valor_original TEXT,
            valor_sugerido TEXT,
            resuelto BOOLEAN DEFAULT FALSE,
            resuelto_por INTEGER REFERENCES users(id),
            resuelto_at TIMESTAMP,
            notas_resolucion TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    op.execute("CREATE INDEX IF NOT EXISTS ix_irregularities_invoice_id ON invoice_irregularities (invoice_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_irregularities_tipo ON invoice_irregularities (tipo)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_irregularities_resuelto ON invoice_irregularities (resuelto)")
    
    # ========================================
    # TABLA DE ARCHIVOS NO COMPATIBLES
    # ========================================
    
    op.execute("""
        CREATE TABLE IF NOT EXISTS invoice_rejected_files (
            id SERIAL PRIMARY KEY,
            archivo_nombre VARCHAR(255) NOT NULL,
            archivo_hash VARCHAR(64),
            archivo_size INTEGER,
            razon_rechazo TEXT NOT NULL,
            detalles_error JSONB DEFAULT '{}'::jsonb,
            uploaded_by INTEGER REFERENCES users(id),
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            puede_reintentar BOOLEAN DEFAULT TRUE
        )
    """)
    
    op.execute("CREATE INDEX IF NOT EXISTS ix_rejected_files_uploaded_at ON invoice_rejected_files (uploaded_at)")


def downgrade() -> None:
    # Eliminar tablas nuevas
    op.execute("DROP TABLE IF EXISTS invoice_rejected_files CASCADE")
    op.execute("DROP TABLE IF EXISTS invoice_irregularities CASCADE")
    
    # Eliminar columnas de invoice_items
    op.execute("ALTER TABLE invoice_items DROP COLUMN IF EXISTS iva_incluido")
    op.execute("ALTER TABLE invoice_items DROP COLUMN IF EXISTS precio_base")
    op.execute("ALTER TABLE invoice_items DROP COLUMN IF EXISTS notas")
    op.execute("ALTER TABLE invoice_items DROP COLUMN IF EXISTS tiene_irregularidad")
    op.execute("ALTER TABLE invoice_items DROP COLUMN IF EXISTS tipo_irregularidad")
    
    # Eliminar columnas de invoices
    op.execute("ALTER TABLE invoices DROP COLUMN IF EXISTS import_status")
    op.execute("ALTER TABLE invoices DROP COLUMN IF EXISTS import_errors")
    op.execute("ALTER TABLE invoices DROP COLUMN IF EXISTS import_warnings")
    op.execute("ALTER TABLE invoices DROP COLUMN IF EXISTS replaced_by_id")
    op.execute("ALTER TABLE invoices DROP COLUMN IF EXISTS replaces_id")
    op.execute("ALTER TABLE invoices DROP COLUMN IF EXISTS is_active")
    op.execute("ALTER TABLE invoices DROP COLUMN IF EXISTS file_hash")
    
    # Eliminar índices
    op.execute("DROP INDEX IF EXISTS ix_invoices_fecha_emision")
    op.execute("DROP INDEX IF EXISTS ix_invoices_supplier_id")
    op.execute("DROP INDEX IF EXISTS ix_invoices_numero_documento")
    op.execute("DROP INDEX IF EXISTS ix_invoices_total_neto")
    op.execute("DROP INDEX IF EXISTS ix_invoices_imported_at")
    op.execute("DROP INDEX IF EXISTS ix_invoices_document_type")
    op.execute("DROP INDEX IF EXISTS ix_invoice_items_invoice_id")
    op.execute("DROP INDEX IF EXISTS ix_invoice_items_codigo")
    op.execute("DROP INDEX IF EXISTS ix_invoice_items_iva_porcentaje")
    op.execute("DROP INDEX IF EXISTS ix_invoice_items_precio_unitario")
    op.execute("DROP INDEX IF EXISTS ix_suppliers_razon_social")
    op.execute("DROP INDEX IF EXISTS ix_suppliers_ciudad")
    
    # Eliminar tipos
    op.execute("DROP TYPE IF EXISTS importstatus")
