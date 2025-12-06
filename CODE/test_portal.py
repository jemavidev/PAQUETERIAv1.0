#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el Portal de Clientes
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Probar que todos los imports funcionan"""
    print("🧪 Probando imports...")
    
    try:
        from app.models.customer_otp import CustomerOTP
        print("✅ Modelo CustomerOTP importado")
    except Exception as e:
        print(f"❌ Error importando CustomerOTP: {e}")
        return False
    
    try:
        from app.schemas.customer_portal import OTPRequest, OTPVerifyRequest
        print("✅ Schemas del portal importados")
    except Exception as e:
        print(f"❌ Error importando schemas: {e}")
        return False
    
    try:
        from app.services.customer_portal_service import CustomerPortalService
        print("✅ Servicio CustomerPortalService importado")
    except Exception as e:
        print(f"❌ Error importando servicio: {e}")
        return False
    
    try:
        from app.routes.customer_portal import router as api_router
        print("✅ Rutas API del portal importadas")
    except Exception as e:
        print(f"❌ Error importando rutas API: {e}")
        return False
    
    try:
        from app.routes.customer_portal_views import router as views_router
        print("✅ Rutas de vistas del portal importadas")
    except Exception as e:
        print(f"❌ Error importando rutas de vistas: {e}")
        return False
    
    return True


def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\n🧪 Probando conexión a base de datos...")
    
    try:
        from app.database import SessionLocal, engine
        from sqlalchemy import text
        
        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión a base de datos exitosa")
            
        # Verificar si la tabla customer_otps existe
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'customer_otps'
                );
            """))
            exists = result.scalar()
            
            if exists:
                print("✅ Tabla customer_otps existe")
            else:
                print("⚠️  Tabla customer_otps NO existe - necesitas ejecutar la migración")
                print("   Ejecuta: cd CODE && python3 -m alembic upgrade head")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def test_customer_exists():
    """Verificar que existen clientes en la base de datos"""
    print("\n🧪 Verificando clientes existentes...")
    
    try:
        from app.database import SessionLocal
        from app.models.customer import Customer
        
        db = SessionLocal()
        
        # Contar clientes
        count = db.query(Customer).filter(Customer.is_active == True).count()
        print(f"✅ Clientes activos encontrados: {count}")
        
        if count > 0:
            # Mostrar un cliente de ejemplo
            customer = db.query(Customer).filter(Customer.is_active == True).first()
            print(f"   Ejemplo: {customer.full_name} - {customer.phone}")
            return True, customer.phone
        else:
            print("⚠️  No hay clientes activos para probar")
            return False, None
            
    except Exception as e:
        print(f"❌ Error consultando clientes: {e}")
        return False, None
    finally:
        db.close()


def create_migration_sql():
    """Generar SQL para crear la tabla manualmente si es necesario"""
    print("\n📝 SQL para crear tabla customer_otps:")
    print("""
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
    );
    
    CREATE INDEX IF NOT EXISTS ix_customer_otps_customer_phone 
    ON customer_otps(customer_phone);
    """)


def main():
    print("=" * 60)
    print("🚀 PRUEBA DEL PORTAL DE CLIENTES")
    print("=" * 60)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Falló la prueba de imports")
        return
    
    # Test 2: Base de datos
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\n⚠️  La tabla customer_otps no existe.")
        print("Opciones:")
        print("1. Ejecutar migración: cd CODE && python3 -m alembic upgrade head")
        print("2. Crear tabla manualmente con el SQL mostrado abajo")
        create_migration_sql()
        return
    
    # Test 3: Clientes
    has_customers, example_phone = test_customer_exists()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print("✅ Imports: OK")
    print(f"{'✅' if db_ok else '❌'} Base de datos: {'OK' if db_ok else 'FALLO'}")
    print(f"{'✅' if has_customers else '⚠️ '} Clientes: {'OK' if has_customers else 'Sin clientes'}")
    
    if db_ok and has_customers:
        print("\n" + "=" * 60)
        print("🎉 ¡TODO LISTO PARA PROBAR!")
        print("=" * 60)
        print("\n📱 PASOS PARA PROBAR EL PORTAL:")
        print("\n1. Inicia el servidor:")
        print("   cd CODE/src")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("\n2. Abre en tu navegador:")
        print("   http://localhost:8000/customer-portal")
        print("\n3. Ingresa un teléfono de cliente existente:")
        print(f"   Ejemplo: {example_phone}")
        print("\n4. Recibirás un SMS con el código de 6 dígitos")
        print("\n5. Ingresa el código y accede al dashboard")
        print("\n" + "=" * 60)
    else:
        print("\n⚠️  Completa los pasos anteriores antes de probar")


if __name__ == "__main__":
    main()
