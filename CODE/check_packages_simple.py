#!/usr/bin/env python3
"""Script simple para verificar paquetes"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Conectar a la base de datos
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("\n" + "="*60)
print("🔍 BUSCANDO PAQUETES CON CÓDIGOS: XNCC y ySVC5")
print("="*60)

# Buscar paquetes
cur.execute("""
    SELECT 
        p.id,
        p.tracking_number,
        p.guide_number,
        p.status,
        p.customer_id,
        c.full_name,
        c.phone,
        c.email
    FROM packages p
    LEFT JOIN customers c ON p.customer_id = c.id
    WHERE p.tracking_number IN ('XNCC', 'ySVC5')
    ORDER BY p.created_at DESC
""")

packages = cur.fetchall()

if packages:
    for pkg in packages:
        print(f"\n📦 Paquete:")
        print(f"   - Tracking: {pkg[1]}")
        print(f"   - Guía: {pkg[2]}")
        print(f"   - Estado: {pkg[3]}")
        print(f"   - Customer ID: {pkg[4]}")
        if pkg[5]:
            print(f"   - Cliente: {pkg[5]}")
            print(f"   - Teléfono: {pkg[6]}")
            print(f"   - Email: {pkg[7]}")
        else:
            print(f"   ⚠️  Sin cliente asignado")
else:
    print("\n❌ No se encontraron paquetes")

# Si encontramos paquetes, buscar todos los paquetes del mismo cliente
if packages and packages[0][4]:
    customer_id = packages[0][4]
    print(f"\n" + "="*60)
    print(f"📦 TODOS LOS PAQUETES DEL CLIENTE {packages[0][5]}")
    print("="*60)
    
    cur.execute("""
        SELECT 
            tracking_number,
            guide_number,
            status,
            created_at
        FROM packages
        WHERE customer_id = %s
        ORDER BY created_at DESC
    """, (customer_id,))
    
    all_packages = cur.fetchall()
    print(f"\nTotal de paquetes: {len(all_packages)}\n")
    
    for pkg in all_packages:
        print(f"   • {pkg[0]} - {pkg[2]} - Guía: {pkg[1] or 'N/A'} - Fecha: {pkg[3]}")

cur.close()
conn.close()

print("\n" + "="*60)
