"""Create invoice tables for CUFE management

Revision ID: create_invoice_tables
Revises: add_display_name_001
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_invoice_tables'
down_revision = 'add_display_name_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create suppliers table (idempotente)
    op.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id SERIAL PRIMARY KEY,
            nit VARCHAR(20) NOT NULL,
            razon_social VARCHAR(255) NOT NULL,
            nombre_comercial VARCHAR(255),
            direccion VARCHAR(255),
            telefono VARCHAR(50),
            correo VARCHAR(100),
            departamento VARCHAR(100),
            ciudad VARCHAR(100),
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_suppliers_id ON suppliers (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_suppliers_nit ON suppliers (nit)")

    # Create invoices table (idempotente)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'documenttype') THEN
                CREATE TYPE documenttype AS ENUM ('FACTURA', 'POS');
            END IF;
        END $$;
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            cufe_cude VARCHAR(100) NOT NULL,
            document_type documenttype NOT NULL,
            numero_documento VARCHAR(50) NOT NULL,
            fecha_emision TIMESTAMP NOT NULL,
            fecha_vencimiento TIMESTAMP,
            forma_pago VARCHAR(50),
            medio_pago VARCHAR(50),
            supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
            subtotal INTEGER DEFAULT 0,
            descuento INTEGER DEFAULT 0,
            total_bruto INTEGER DEFAULT 0,
            total_iva INTEGER DEFAULT 0,
            total_otros_impuestos INTEGER DEFAULT 0,
            total_neto INTEGER DEFAULT 0,
            archivo_nombre VARCHAR(255),
            archivo_path VARCHAR(500),
            imported_by INTEGER REFERENCES users(id),
            imported_at TIMESTAMP,
            is_validated BOOLEAN DEFAULT FALSE,
            validation_notes TEXT
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoices_id ON invoices (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_invoices_cufe_cude ON invoices (cufe_cude)")

    # Create invoice_items table (idempotente)
    op.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id SERIAL PRIMARY KEY,
            invoice_id INTEGER NOT NULL REFERENCES invoices(id),
            numero_item INTEGER NOT NULL,
            codigo VARCHAR(50),
            descripcion VARCHAR(500) NOT NULL,
            unidad_medida VARCHAR(50),
            cantidad INTEGER DEFAULT 1,
            precio_unitario INTEGER DEFAULT 0,
            descuento INTEGER DEFAULT 0,
            recargo INTEGER DEFAULT 0,
            iva_porcentaje FLOAT DEFAULT 0,
            iva_valor INTEGER DEFAULT 0,
            inc_porcentaje FLOAT DEFAULT 0,
            inc_valor INTEGER DEFAULT 0,
            valor_total INTEGER DEFAULT 0
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoice_items_id ON invoice_items (id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS invoice_items CASCADE")
    op.execute("DROP TABLE IF EXISTS invoices CASCADE")
    op.execute("DROP TABLE IF EXISTS suppliers CASCADE")
    op.execute("DROP TYPE IF EXISTS documenttype")
