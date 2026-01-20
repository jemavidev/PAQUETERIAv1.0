#!/usr/bin/env python3
"""Aplicar migración de estados CUFE y DIAN manualmente"""
import sys
import os
sys.path.insert(0, '/app/src')

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

sql = """
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS cufe_status VARCHAR(20);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS dian_status VARCHAR(20);
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS dian_pdf_id INTEGER;
ALTER TABLE invoices ADD COLUMN IF NOT EXISTS cufe_source VARCHAR(20);

CREATE INDEX IF NOT EXISTS ix_invoices_cufe_status ON invoices(cufe_status);
CREATE INDEX IF NOT EXISTS ix_invoices_dian_status ON invoices(dian_status);
CREATE INDEX IF NOT EXISTS ix_invoices_dian_pdf_id ON invoices(dian_pdf_id);

UPDATE invoices 
SET cufe_status = 'extracted',
    dian_status = CASE 
        WHEN supplier_invoice_id IS NOT NULL THEN 'processed'
        ELSE 'pending'
    END,
    cufe_source = 'extracted'
WHERE cufe_status IS NULL;
"""

try:
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✅ Migración aplicada exitosamente")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
