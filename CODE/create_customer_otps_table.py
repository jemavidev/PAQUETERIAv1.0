#!/usr/bin/env python3
"""
Script para crear la tabla customer_otps directamente en la base de datos
"""
import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configurar variables de entorno mínimas para evitar errores
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'dummy')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'dummy')
os.environ.setdefault('AWS_S3_BUCKET', 'dummy')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar .env
load_dotenv('.env')

# Obtener DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no encontrada en .env")
    sys.exit(1)

print(f"🔗 Conectando a base de datos...")
print(f"   Host: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'unknown'}")

try:
    # Crear engine
    engine = create_engine(DATABASE_URL)
    
    # Conectar y crear tabla
    with engine.connect() as conn:
        print("\n📋 Creando tabla customer_otps...")
        
        # Crear tabla
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customer_otps (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                customer_phone VARCHAR(20) NOT NULL,
                otp_code VARCHAR(6) NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                max_attempts INTEGER NOT NULL DEFAULT 3,
                is_verified BOOLEAN NOT NULL DEFAULT FALSE,
                is_expired BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                expires_at TIMESTAMP NOT NULL,
                verified_at TIMESTAMP NULL
            )
        """))
        
        print("✅ Tabla customer_otps creada")
        
        # Crear índice
        print("\n📋 Creando índice...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_customer_otps_customer_phone 
            ON customer_otps(customer_phone)
        """))
        
        print("✅ Índice ix_customer_otps_customer_phone creado")
        
        # Commit
        conn.commit()
        
        # Verificar
        print("\n🔍 Verificando tabla...")
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'customer_otps'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        if columns:
            print("✅ Tabla verificada. Columnas:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
        else:
            print("⚠️  No se pudo verificar la tabla")
        
        print("\n" + "="*60)
        print("🎉 ¡Tabla customer_otps creada exitosamente!")
        print("="*60)
        print("\n✅ Ahora puedes iniciar el servidor:")
        print("   cd CODE/src")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("\n✅ Y acceder al portal en:")
        print("   http://localhost:8000/customer-portal")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
