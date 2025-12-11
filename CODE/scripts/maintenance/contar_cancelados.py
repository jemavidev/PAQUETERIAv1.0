#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contar paquetes cancelados en la BD
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT', 5432),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

cursor = conn.cursor(cursor_factory=RealDictCursor)

# Contar por estado
cursor.execute("""
    SELECT status, COUNT(*) as total
    FROM packages
    GROUP BY status
    ORDER BY status
""")

print("\n📊 PAQUETES POR ESTADO:\n")
for row in cursor.fetchall():
    print(f"  {row['status']}: {row['total']}")

# Mostrar algunos cancelados
cursor.execute("""
    SELECT tracking_number, guide_number, cancelled_at,
           (SELECT full_name FROM customers WHERE id = packages.customer_id) as customer_name
    FROM packages 
    WHERE status = 'CANCELADO'
    ORDER BY cancelled_at DESC
    LIMIT 20
""")

cancelados = cursor.fetchall()

print(f"\n📦 PAQUETES CANCELADOS (últimos 20):\n")
for pkg in cancelados:
    print(f"  {pkg['tracking_number']} | {pkg['guide_number']} | {pkg['customer_name']} | {pkg['cancelled_at']}")

cursor.close()
conn.close()
