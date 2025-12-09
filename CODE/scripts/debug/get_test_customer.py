#!/usr/bin/env python3
"""
Script para obtener un cliente de prueba
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

os.environ.setdefault('AWS_ACCESS_KEY_ID', 'dummy')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'dummy')
os.environ.setdefault('AWS_S3_BUCKET', 'dummy')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('.env')
DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT 
            first_name, 
            last_name, 
            phone, 
            email,
            address_street
        FROM customers 
        WHERE is_active = true 
        AND phone IS NOT NULL 
        AND phone != ''
        LIMIT 5
    """))
    
    customers = result.fetchall()
    
    if customers:
        print("📱 Clientes disponibles para probar el portal:\n")
        for i, c in enumerate(customers, 1):
            print(f"{i}. {c[0]} {c[1]}")
            print(f"   📞 Teléfono: {c[2]}")
            print(f"   📧 Email: {c[3] or 'Sin email'}")
            print(f"   📍 Dirección: {c[4] or 'Sin dirección'}")
            print()
        
        print("="*60)
        print("🧪 Para probar el portal:")
        print(f"1. Ve a: http://localhost:8000/customer-portal")
        print(f"2. Ingresa uno de estos teléfonos")
        print(f"3. Recibirás un SMS con el código")
        print("="*60)
    else:
        print("⚠️  No se encontraron clientes activos")
