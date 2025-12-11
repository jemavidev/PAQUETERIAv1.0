#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar anuncios específicos que aparecen en pantalla
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT', 5432),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
    return conn

# Códigos que aparecen en la pantalla
codigos_pantalla = [
    'PAPYRUS-M6PRTC',
    'PAPYRUS-5V11WC',
    'TEMP-U3MW1G',
    'V3BV',
    'W19R',
    'DKMK'
]

conn = get_db_connection()
cursor = conn.cursor(cursor_factory=RealDictCursor)

print("\n" + "="*60)
print("VERIFICACIÓN DE ANUNCIOS ESPECÍFICOS")
print("="*60 + "\n")

for codigo in codigos_pantalla:
    # Buscar en anuncios
    cursor.execute("""
        SELECT id, guide_number, tracking_code, customer_name, customer_phone,
               customer_id, package_id, is_active, is_processed
        FROM package_announcements_new 
        WHERE guide_number = %s OR tracking_code = %s
    """, (codigo, codigo))
    
    anuncio = cursor.fetchone()
    
    if anuncio:
        print(f"📦 Código: {codigo}")
        print(f"   Guía: {anuncio['guide_number']}")
        print(f"   Tracking: {anuncio['tracking_code']}")
        print(f"   Cliente: {anuncio['customer_name']} ({anuncio['customer_phone']})")
        print(f"   Customer ID: {anuncio['customer_id']}")
        print(f"   Package ID: {anuncio['package_id']}")
        print(f"   Activo: {anuncio['is_active']}")
        print(f"   Procesado: {anuncio['is_processed']}")
        
        # Verificar si el cliente existe
        if anuncio['customer_id']:
            cursor.execute("""
                SELECT id, phone, full_name FROM customers WHERE id = %s
            """, (anuncio['customer_id'],))
            cliente = cursor.fetchone()
            if cliente:
                print(f"   ✅ Cliente existe: {cliente['full_name']}")
            else:
                print(f"   ❌ Cliente NO existe (huérfano)")
        else:
            print(f"   ⚠️  Sin customer_id (huérfano)")
        
        print()
    else:
        print(f"❌ {codigo} - NO ENCONTRADO en BD")
        print()

# Buscar todos los anuncios con JUAN PEREZ o JESUS VILLALOBOS
print("\n" + "="*60)
print("ANUNCIOS DE JUAN PEREZ Y JESUS VILLALOBOS")
print("="*60 + "\n")

cursor.execute("""
    SELECT guide_number, tracking_code, customer_name, customer_phone,
           customer_id, is_active, is_processed
    FROM package_announcements_new 
    WHERE customer_name LIKE '%JUAN PEREZ%' 
       OR customer_name LIKE '%JESUS VILLALOBOS%'
    ORDER BY announced_at DESC
""")

anuncios = cursor.fetchall()

if anuncios:
    print(f"Encontrados {len(anuncios)} anuncios:\n")
    for a in anuncios:
        print(f"  📦 {a['guide_number']} | {a['tracking_code']}")
        print(f"     {a['customer_name']} ({a['customer_phone']})")
        print(f"     Customer ID: {a['customer_id']}")
        print(f"     Activo: {a['is_active']} | Procesado: {a['is_processed']}")
        print()
else:
    print("✅ No hay anuncios de estos clientes")

cursor.close()
conn.close()
