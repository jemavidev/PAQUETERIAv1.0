#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado de todas las tablas en la base de datos
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import text, inspect
from app.database import SessionLocal, engine

def verify_database_status():
    """
    Verifica el estado de todas las tablas en la base de datos
    """
    db = SessionLocal()
    
    try:
        print("🔍 Verificando estado de la base de datos...\n")
        
        # Obtener todas las tablas
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Total de tablas en la base de datos: {len(tables)}\n")
        
        # Verificar cada tabla
        for table in sorted(tables):
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                
                if count > 0:
                    print(f"✓ {table:40} → {count:6} registros")
                else:
                    print(f"○ {table:40} → vacía")
            except Exception as e:
                print(f"✗ {table:40} → Error: {str(e)[:50]}")
        
        print("\n" + "="*70)
        print("RESUMEN DE TABLAS CON DATOS:")
        print("="*70 + "\n")
        
        tables_with_data = []
        for table in sorted(tables):
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                if count > 0:
                    tables_with_data.append((table, count))
            except:
                pass
        
        if tables_with_data:
            for table, count in tables_with_data:
                print(f"  📦 {table}: {count} registros")
        else:
            print("  ✓ Todas las tablas están vacías (excepto las que se deben mantener)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    verify_database_status()
