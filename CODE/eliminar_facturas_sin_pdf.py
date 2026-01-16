#!/usr/bin/env python3
"""Elimina facturas sin PDF guardado"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Eliminar facturas sin path
result = db.execute(text("DELETE FROM supplier_invoices WHERE original_file_path IS NULL OR original_file_path = ''"))
db.commit()
count = result.rowcount

print(f"✅ Eliminadas {count} facturas sin PDF guardado")

# Verificar
result = db.execute(text("SELECT COUNT(*) FROM supplier_invoices"))
total = result.fetchone()[0]
print(f"📊 Total de facturas restantes: {total}")
