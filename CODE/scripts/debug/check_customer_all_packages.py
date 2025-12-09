#!/usr/bin/env python3
"""Ver todos los paquetes de JESUS VILLALOBOS"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

customer_id = '6f93711c-5bd0-455a-971e-b4353cf13fe6'

print("\n" + "="*60)
print("📦 TODOS LOS PAQUETES DE JESUS VILLALOBOS")
print("="*60 + "\n")

cur.execute("""
    SELECT 
        tracking_number,
        guide_number,
        status,
        created_at,
        announced_at,
        received_at,
        delivered_at
    FROM packages
    WHERE customer_id = %s
    ORDER BY created_at DESC
""", (customer_id,))

packages = cur.fetchall()

print(f"Total de paquetes: {len(packages)}\n")

for i, pkg in enumerate(packages, 1):
    print(f"{i}. Código: {pkg[0]}")
    print(f"   Guía: {pkg[1] or 'N/A'}")
    print(f"   Estado: {pkg[2]}")
    print(f"   Creado: {pkg[3]}")
    if pkg[4]:
        print(f"   Anunciado: {pkg[4]}")
    if pkg[5]:
        print(f"   Recibido: {pkg[5]}")
    if pkg[6]:
        print(f"   Entregado: {pkg[6]}")
    print()

cur.close()
conn.close()

print("="*60)
