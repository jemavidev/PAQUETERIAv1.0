#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Índices adicionales
indexes = [
    "CREATE INDEX IF NOT EXISTS idx_invoices_v2_created_at ON invoices_v2 (created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_invoices_v2_search_created ON invoices_v2 (proveedor_nombre, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_invoices_v2_s3_key ON invoices_v2 (archivo_proveedor_s3_key) WHERE archivo_proveedor_s3_key IS NOT NULL",
]

for idx in indexes:
    try:
        print(f'Creando: {idx[:60]}...')
        db.execute(text(idx))
        db.commit()
        print('  ✅ Creado')
    except Exception as e:
        print(f'  ⚠️ {str(e)[:80]}')
        db.rollback()

db.close()
print('\n✅ Índices adicionales aplicados')
