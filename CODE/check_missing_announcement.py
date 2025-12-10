#!/usr/bin/env python3
"""Verificar el anuncio faltante"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

customer_id = "6f93711c-5bd0-455a-971e-b4353cf13fe6"

query = text('''
    SELECT 
        id,
        guide_number,
        tracking_code,
        is_processed,
        is_active,
        announced_at
    FROM package_announcements_new
    WHERE customer_id = :customer_id
      AND is_processed = FALSE
    ORDER BY announced_at DESC
''')

results = db.execute(query, {'customer_id': customer_id}).fetchall()

print(f"Anuncios pendientes (is_processed=FALSE):")
for r in results:
    print(f"  Guía: {r[1]}, Código: {r[2]}, is_active: {r[4]}, Fecha: {r[5]}")

db.close()
