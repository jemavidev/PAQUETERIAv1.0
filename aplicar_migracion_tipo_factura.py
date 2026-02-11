#!/usr/bin/env python3
"""
Script para aplicar la migración de tipo_factura
"""
import sys
import os

# Agregar el directorio CODE al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE'))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('CODE/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

print("🔧 Aplicando migración: tipo_factura")
print(f"📊 Base de datos: {DATABASE_URL.split('@')[1].split('/')[0]}")
print()

try:
    # Crear conexión
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. Agregar columna tipo_factura
        print("1️⃣ Agregando columna tipo_factura...")
        conn.execute(text("""
            ALTER TABLE invoices_v2 
            ADD COLUMN IF NOT EXISTS tipo_factura VARCHAR(20) DEFAULT 'reventa' NOT NULL
        """))
        conn.commit()
        print("   ✅ Columna agregada")
        
        # 2. Crear índice
        print("2️⃣ Creando índice idx_invoices_tipo_factura...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_invoices_tipo_factura 
            ON invoices_v2(tipo_factura)
        """))
        conn.commit()
        print("   ✅ Índice creado")
        
        # 3. Verificar
        print("3️⃣ Verificando migración...")
        result = conn.execute(text("""
            SELECT column_name, data_type, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'invoices_v2' 
            AND column_name = 'tipo_factura'
        """))
        row = result.fetchone()
        
        if row:
            print(f"   ✅ Columna verificada:")
            print(f"      - Nombre: {row[0]}")
            print(f"      - Tipo: {row[1]}")
            print(f"      - Default: {row[2]}")
        else:
            print("   ❌ Error: Columna no encontrada")
            sys.exit(1)
        
        # 4. Estadísticas
        print("4️⃣ Estadísticas:")
        result = conn.execute(text("""
            SELECT 
                tipo_factura,
                COUNT(*) as total_facturas
            FROM invoices_v2
            GROUP BY tipo_factura
            ORDER BY total_facturas DESC
        """))
        
        for row in result:
            print(f"   - {row[0]}: {row[1]} facturas")
        
        print()
        print("🎉 Migración aplicada exitosamente!")
        print()
        print("📝 Próximos pasos:")
        print("   1. Reiniciar el servidor: cd CODE && ./start_server.sh")
        print("   2. Ir al TAB PRODUCTOS y ver el filtro 'Solo reventa'")
        print("   3. Ir al TAB FACTURAS y editar una factura para cambiar el tipo")
        
except Exception as e:
    print(f"❌ Error aplicando migración: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
