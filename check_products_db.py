#!/usr/bin/env python3
import sys
sys.path.insert(0, 'CODE/src')

from sqlalchemy import create_engine, text
import os

# Leer DATABASE_URL del .env
env_file = 'CODE/.env'
db_url = None
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            if line.startswith('DATABASE_URL='):
                db_url = line.split('=', 1)[1].strip().strip('"').strip("'")
                break

if not db_url:
    db_url = 'postgresql://postgres:postgres@localhost:5432/paquetex'

print(f"Conectando a: {db_url[:50]}...")

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2"))
        total = result.scalar()
        print(f"\n✅ Total de productos en BD: {total}")
        
        if total > 0:
            result = conn.execute(text("""
                SELECT id, descripcion, cantidad, precio_unitario, total_item 
                FROM invoice_products_v2 
                LIMIT 3
            """))
            print("\nPrimeros 3 productos:")
            for row in result:
                print(f"  - ID: {row[0]}, Desc: {row[1][:40] if row[1] else 'N/A'}, Cant: {row[2]}, Precio: {row[3]}")
        else:
            print("\n⚠️ No hay productos en la base de datos")
            
except Exception as e:
    print(f"\n❌ Error: {e}")
