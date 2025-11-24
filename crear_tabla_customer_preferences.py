#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear la tabla customer_preferences
"""

import sys
import os

# Agregar el directorio CODE/src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE', 'src'))

from sqlalchemy import create_engine, text
from app.config import settings

def create_customer_preferences_table():
    """Crea la tabla customer_preferences si no existe"""
    
    print("🔧 Conectando a la base de datos...")
    
    try:
        # Crear engine
        engine = create_engine(settings.database_url)
        
        print("✅ Conexión establecida")
        print("🔧 Creando tabla customer_preferences...")
        
        # SQL para crear la tabla
        sql = """
        CREATE TABLE IF NOT EXISTS customer_preferences (
            id SERIAL PRIMARY KEY,
            customer_id UUID NOT NULL UNIQUE,
            token VARCHAR(64) NOT NULL UNIQUE,
            sms_notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            email_notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            notify_package_received BOOLEAN NOT NULL DEFAULT TRUE,
            notify_package_delivered BOOLEAN NOT NULL DEFAULT TRUE,
            notify_package_announced BOOLEAN NOT NULL DEFAULT TRUE,
            notify_payment_due BOOLEAN NOT NULL DEFAULT TRUE,
            marketing_enabled BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            CONSTRAINT fk_customer_preferences_customer 
                FOREIGN KEY (customer_id) 
                REFERENCES customers(id) 
                ON DELETE CASCADE
        );
        
        CREATE INDEX IF NOT EXISTS idx_customer_preferences_customer_id 
            ON customer_preferences(customer_id);
        
        CREATE INDEX IF NOT EXISTS idx_customer_preferences_token 
            ON customer_preferences(token);
        """
        
        # Ejecutar SQL
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        
        print("✅ Tabla customer_preferences creada exitosamente")
        
        # Verificar que se creó
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name = 'customer_preferences'
            """))
            count = result.fetchone()[0]
            
            if count > 0:
                print("✅ Verificación exitosa: Tabla existe")
                
                # Mostrar estructura
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = 'customer_preferences'
                    ORDER BY ordinal_position
                """))
                
                print("\n📋 Estructura de la tabla:")
                print("-" * 80)
                for row in result:
                    print(f"  {row[0]:30} {row[1]:20} NULL: {row[2]:3} Default: {row[3]}")
                print("-" * 80)
            else:
                print("❌ Error: La tabla no se creó")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("CREAR TABLA CUSTOMER_PREFERENCES")
    print("=" * 80)
    print()
    
    success = create_customer_preferences_table()
    
    print()
    if success:
        print("✅ ¡Tabla creada exitosamente!")
        print()
        print("Próximos pasos:")
        print("1. Reinicia el servidor: docker compose restart")
        print("2. Recarga la página: http://localhost:8000/customers/manage")
        print("3. Haz clic en el botón morado de preferencias")
    else:
        print("❌ Error al crear la tabla")
        print()
        print("Verifica:")
        print("1. Que la base de datos esté corriendo")
        print("2. Que las credenciales en .env sean correctas")
        print("3. Los logs arriba para más detalles")
    
    print("=" * 80)
