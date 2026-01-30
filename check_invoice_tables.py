#!/usr/bin/env python3
"""Script rápido para verificar si hay datos en las tablas de invoices"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE'))

from sqlalchemy import create_engine, text
from src.app.config import settings

def check_tables():
    engine = create_engine(settings.database_url)
    
    tables = [
        'supplier_invoices',
        'invoices',
        'invoice_items',
        'invoice_irregularities',
        'invoice_rejected_files',
        'cufe_records',
    ]
    
    print("\n📊 VERIFICACIÓN RÁPIDA DE TABLAS\n")
    print("="*50)
    
    total_records = 0
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                total_records += count
                
                if count > 0:
                    print(f"⚠️  {table}: {count} registros")
                else:
                    print(f"✅ {table}: vacía")
            except Exception as e:
                print(f"❌ {table}: {str(e)[:50]}")
    
    print("="*50)
    
    if total_records == 0:
        print("\n✅ TODAS LAS TABLAS ESTÁN VACÍAS")
        print("   → Puedes eliminarlas sin pérdida de datos\n")
    else:
        print(f"\n⚠️  TOTAL: {total_records} registros en las tablas")
        print("   → Considera hacer backup antes de eliminar\n")

if __name__ == "__main__":
    check_tables()
