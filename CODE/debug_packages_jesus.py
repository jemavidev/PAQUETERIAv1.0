#!/usr/bin/env python3
"""Script para investigar paquetes de JESUS VILLALOBOS"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

# Conectar a la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL no está configurada")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

print("=" * 80)
print("INVESTIGACIÓN: Paquetes de JESUS VILLALOBOS")
print("=" * 80)

# Buscar el cliente JESUS VILLALOBOS
query = text('''
    SELECT 
        c.id,
        c.first_name,
        c.last_name,
        c.phone,
        c.is_active
    FROM customers c
    WHERE UPPER(c.first_name) LIKE '%JESUS%' 
      AND UPPER(c.last_name) LIKE '%VILLALOBOS%'
''')

customers = db.execute(query).fetchall()

if not customers:
    print("❌ Cliente no encontrado")
    db.close()
    sys.exit(1)

for customer in customers:
    customer_id = customer[0]
    print(f"\n✅ Cliente encontrado:")
    print(f"   ID: {customer_id}")
    print(f"   Nombre: {customer[1]} {customer[2]}")
    print(f"   Teléfono: {customer[3]}")
    print(f"   Activo: {customer[4]}")
    
    # Contar paquetes por estado
    query_count = text('''
        SELECT 
            p.status,
            COUNT(*) as cantidad
        FROM packages p
        WHERE p.customer_id = :customer_id
        GROUP BY p.status
        ORDER BY p.status
    ''')
    
    counts = db.execute(query_count, {'customer_id': customer_id}).fetchall()
    
    print(f"\n📊 Resumen de paquetes:")
    total = 0
    for status, count in counts:
        print(f"   {status}: {count}")
        total += count
    print(f"   TOTAL: {total}")
    
    # Ver paquetes individuales
    query_packages = text('''
        SELECT 
            p.id,
            p.tracking_number,
            p.guide_number,
            p.status,
            p.created_at
        FROM packages p
        WHERE p.customer_id = :customer_id
        ORDER BY p.created_at DESC
    ''')
    
    packages = db.execute(query_packages, {'customer_id': customer_id}).fetchall()
    
    print(f"\n📦 Paquetes individuales ({len(packages)} total):")
    for i, pkg in enumerate(packages, 1):
        print(f"   {i}. ID: {pkg[0]}")
        print(f"      Tracking: {pkg[1]}")
        print(f"      Guía: {pkg[2]}")
        print(f"      Estado: {pkg[3]}")
        print(f"      Fecha: {pkg[4]}")
        print()
    
    # Buscar también en anuncios (package_announcements_new)
    print(f"\n📢 Buscando en anuncios...")
    query_announcements = text('''
        SELECT 
            a.id,
            a.guide_number,
            a.tracking_code,
            a.customer_name,
            a.customer_phone,
            a.is_processed,
            a.announced_at,
            a.customer_id
        FROM package_announcements_new a
        WHERE a.customer_id = :customer_id
        ORDER BY a.announced_at DESC
    ''')
    
    announcements = db.execute(query_announcements, {'customer_id': customer_id}).fetchall()
    
    if announcements:
        print(f"   Encontrados {len(announcements)} anuncios:")
        for i, ann in enumerate(announcements, 1):
            processed = "✅ Procesado" if ann[5] else "⏳ Pendiente"
            print(f"   {i}. ID: {ann[0]}")
            print(f"      Guía: {ann[1]}")
            print(f"      Código: {ann[2]}")
            print(f"      Estado: {processed}")
            print(f"      Fecha: {ann[6]}")
            print()
    else:
        print(f"   No se encontraron anuncios para este cliente")

db.close()

print("=" * 80)
print("Investigación completada")
print("=" * 80)
