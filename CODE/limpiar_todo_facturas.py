#!/usr/bin/env python3
"""Limpia TODAS las facturas del sistema"""
import os, sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
db = sessionmaker(bind=engine)()

print("="*80)
print("LIMPIANDO TODAS LAS FACTURAS")
print("="*80)

# Orden correcto para evitar errores de foreign key
tables = [
    'invoice_irregularities',
    'invoice_items',
    'invoice_rejected_files',
    'invoices',
    'supplier_invoices',
    'suppliers'
]

total = 0
for table in tables:
    result = db.execute(text(f"DELETE FROM {table}"))
    db.commit()
    count = result.rowcount
    total += count
    print(f"✅ {table}: {count} registros eliminados")

print(f"\n📊 Total eliminado: {total} registros")
print("="*80)
