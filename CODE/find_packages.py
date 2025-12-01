#!/usr/bin/env python3
"""Script para encontrar paquetes cancelados"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("\n" + "="*60)
print("🔍 BUSCANDO PAQUETES CANCELADOS")
print("="*60)

# Buscar paquetes cancelados
cur.execute("""
    SELECT 
        p.id,
        p.tracking_number,
        p.guide_number,
        p.status,
        p.customer_id,
        c.full_name,
        c.phone
    FROM packages p
    LEFT JOIN customers c ON p.customer_id = c.id
    WHERE p.status = 'CANCELADO'
    ORDER BY p.created_at DESC
    LIMIT 10
""")

packages = cur.fetchall()

print(f"\nTotal de paquetes cancelados: {len(packages)}\n")

for pkg in packages:
    print(f"📦 Paquete:")
    print(f"   - Tracking: {pkg[1]}")
    print(f"   - Guía: {pkg[2]}")
    print(f"   - Estado: {pkg[3]}")
    print(f"   - Customer ID: {pkg[4]}")
    if pkg[5]:
        print(f"   - Cliente: {pkg[5]} ({pkg[6]})")
    print()

# Buscar paquetes que contengan las letras mencionadas
print("="*60)
print("🔍 BUSCANDO PAQUETES QUE CONTENGAN 'XNC' o 'ySVC'")
print("="*60 + "\n")

cur.execute("""
    SELECT 
        p.tracking_number,
        p.guide_number,
        p.status,
        c.full_name,
        c.phone
    FROM packages p
    LEFT JOIN customers c ON p.customer_id = c.id
    WHERE p.tracking_number ILIKE '%XNC%' OR p.tracking_number ILIKE '%ySVC%'
    ORDER BY p.created_at DESC
""")

packages = cur.fetchall()

if packages:
    for pkg in packages:
        print(f"📦 {pkg[0]} - {pkg[2]} - Cliente: {pkg[3] or 'N/A'}")
else:
    print("❌ No se encontraron paquetes")

cur.close()
conn.close()

print("\n" + "="*60)
