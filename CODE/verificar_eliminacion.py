#!/usr/bin/env python3
"""
Script para verificar que las facturas fueron eliminadas
"""
import psycopg2

DB_CONFIG = {
    'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
    'port': 5432,
    'database': 'paqueteria_staging',
    'user': 'jveyes',
    'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("\n📊 Estado actual de la base de datos:")
    print("="*60)
    
    cursor.execute("SELECT COUNT(*) FROM invoices_v2")
    facturas = cursor.fetchone()[0]
    print(f"  • Facturas: {facturas}")
    
    cursor.execute("SELECT COUNT(*) FROM invoice_products_v2")
    productos = cursor.fetchone()[0]
    print(f"  • Productos: {productos}")
    
    if facturas == 0 and productos == 0:
        print("\n✅ Base de datos limpia - No hay facturas ni productos")
    else:
        print(f"\n⚠️  Aún hay datos: {facturas} facturas, {productos} productos")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
