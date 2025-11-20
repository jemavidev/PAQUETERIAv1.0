#!/usr/bin/env python3
"""Script para verificar anuncios en la base de datos"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text
from app.database import get_db

def check_announcements():
    db = next(get_db())
    
    try:
        # Verificar si la tabla existe
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'package_announcements_new'
            )
        """))
        table_exists = result.scalar()
        print(f"✅ Tabla package_announcements_new existe: {table_exists}")
        
        if not table_exists:
            print("❌ La tabla no existe!")
            return
        
        # Contar anuncios totales
        result = db.execute(text("SELECT COUNT(*) FROM package_announcements_new"))
        total = result.scalar()
        print(f"📦 Total de anuncios: {total}")
        
        # Contar anuncios no procesados
        result = db.execute(text("SELECT COUNT(*) FROM package_announcements_new WHERE is_processed = false"))
        unprocessed = result.scalar()
        print(f"📦 Anuncios no procesados: {unprocessed}")
        
        # Contar anuncios activos
        result = db.execute(text("SELECT COUNT(*) FROM package_announcements_new WHERE is_active = true"))
        active = result.scalar()
        print(f"📦 Anuncios activos: {active}")
        
        # Mostrar algunos anuncios no procesados
        if unprocessed > 0:
            print("\n📋 Primeros 5 anuncios no procesados:")
            result = db.execute(text("""
                SELECT id, tracking_code, customer_name, customer_phone, announced_at, is_processed, is_active
                FROM package_announcements_new 
                WHERE is_processed = false
                ORDER BY announced_at DESC
                LIMIT 5
            """))
            for row in result:
                print(f"  - ID: {row[0]}, Tracking: {row[1]}, Cliente: {row[2]}, Teléfono: {row[3]}, Fecha: {row[4]}, Procesado: {row[5]}, Activo: {row[6]}")
        
        # Verificar estructura de la tabla
        print("\n📋 Estructura de la tabla:")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'package_announcements_new'
            ORDER BY ordinal_position
        """))
        for row in result:
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_announcements()
