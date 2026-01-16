#!/usr/bin/env python3
import os, sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
db = sessionmaker(bind=engine)()

result = db.execute(text("SELECT id, original_filename, original_file_path FROM supplier_invoices ORDER BY id DESC LIMIT 10"))
rows = result.fetchall()

print("="*80)
for row in rows:
    status = "✅ OK" if row[2] else "❌ NO GUARDADO"
    print(f"ID: {row[0]} | {row[1][:40]} | {status}")
    if row[2]:
        print(f"     Path: {row[2]}")
print("="*80)
