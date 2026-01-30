#!/usr/bin/env python3
"""
Script para limpiar las tablas de invoices de la base de datos
Ejecutar desde: python cleanup_invoices_database.py
"""

import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE'))

from sqlalchemy import create_engine, text, inspect
from src.app.config import settings

def get_invoice_tables():
    """Retorna lista de tablas relacionadas con invoices"""
    return [
        'supplier_invoices',
        'invoices',
        'invoice_items',
        'invoice_irregularities',
        'invoice_rejected_files',
        'cufe_records',
    ]

def analyze_tables(engine):
    """Analiza las tablas y muestra información"""
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE TABLAS DE INVOICES")
    print("="*60 + "\n")
    
    inspector = inspect(engine)
    tables = get_invoice_tables()
    
    results = {}
    
    with engine.connect() as conn:
        for table in tables:
            if table in inspector.get_table_names():
                # Contar registros
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                
                # Obtener columnas
                columns = inspector.get_columns(table)
                
                results[table] = {
                    'exists': True,
                    'count': count,
                    'columns': len(columns)
                }
                
                status = "✅" if count == 0 else f"⚠️  {count} registros"
                print(f"{status} {table}")
                print(f"   └─ {len(columns)} columnas")
            else:
                results[table] = {'exists': False}
                print(f"❌ {table} (no existe)")
    
    return results

def backup_data(engine):
    """Hace backup de los datos antes de eliminar"""
    print("\n" + "="*60)
    print("💾 BACKUP DE DATOS")
    print("="*60 + "\n")
    
    import json
    from datetime import datetime
    
    backup_file = f"BACKUP_INVOICES_DATA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_data = {}
    
    tables = get_invoice_tables()
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                
                if rows:
                    # Convertir a dict
                    backup_data[table] = []
                    for row in rows:
                        backup_data[table].append(dict(row._mapping))
                    
                    print(f"✅ {table}: {len(rows)} registros respaldados")
                else:
                    print(f"⚪ {table}: vacía (no se respalda)")
            except Exception as e:
                print(f"❌ {table}: Error - {e}")
    
    if backup_data:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, default=str)
        print(f"\n✅ Backup guardado en: {backup_file}")
        return backup_file
    else:
        print("\n⚪ No hay datos para respaldar")
        return None

def drop_tables(engine, confirm=False):
    """Elimina las tablas de invoices"""
    if not confirm:
        print("\n⚠️  ADVERTENCIA: Esta operación es IRREVERSIBLE")
        response = input("¿Estás seguro de eliminar las tablas? (escribe 'SI' para confirmar): ")
        if response != "SI":
            print("❌ Operación cancelada")
            return False
    
    print("\n" + "="*60)
    print("🗑️  ELIMINANDO TABLAS")
    print("="*60 + "\n")
    
    tables = get_invoice_tables()
    
    with engine.connect() as conn:
        # Eliminar en orden inverso para respetar foreign keys
        for table in reversed(tables):
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                conn.commit()
                print(f"✅ {table} eliminada")
            except Exception as e:
                print(f"❌ {table}: Error - {e}")
    
    print("\n✅ Tablas eliminadas correctamente")
    return True

def truncate_tables(engine, confirm=False):
    """Vacía las tablas sin eliminarlas"""
    if not confirm:
        print("\n⚠️  ADVERTENCIA: Esto eliminará todos los datos")
        response = input("¿Estás seguro de vaciar las tablas? (escribe 'SI' para confirmar): ")
        if response != "SI":
            print("❌ Operación cancelada")
            return False
    
    print("\n" + "="*60)
    print("🧹 VACIANDO TABLAS")
    print("="*60 + "\n")
    
    tables = get_invoice_tables()
    
    with engine.connect() as conn:
        for table in reversed(tables):
            try:
                conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                conn.commit()
                print(f"✅ {table} vaciada")
            except Exception as e:
                print(f"❌ {table}: Error - {e}")
    
    print("\n✅ Tablas vaciadas correctamente")
    return True

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔧 LIMPIEZA DE BASE DE DATOS - Sistema de Facturas")
    print("="*60)
    
    # Conectar a la base de datos
    try:
        engine = create_engine(settings.database_url)
        print(f"\n✅ Conectado a: {settings.database_url.split('@')[1].split('/')[0]}")
    except Exception as e:
        print(f"\n❌ Error conectando a la base de datos: {e}")
        return
    
    # Analizar tablas
    results = analyze_tables(engine)
    
    # Verificar si hay datos
    has_data = any(r.get('count', 0) > 0 for r in results.values() if r.get('exists'))
    
    if not has_data:
        print("\n✅ No hay datos en las tablas. Puedes eliminarlas sin pérdida.")
    
    # Menú de opciones
    print("\n" + "="*60)
    print("📋 OPCIONES")
    print("="*60)
    print("\n1. Solo analizar (ya hecho)")
    print("2. Hacer backup de datos")
    print("3. Vaciar tablas (TRUNCATE - mantiene estructura)")
    print("4. Eliminar tablas (DROP - elimina todo)")
    print("5. Backup + Vaciar tablas")
    print("6. Backup + Eliminar tablas")
    print("0. Salir")
    
    choice = input("\nSelecciona una opción: ")
    
    if choice == "1":
        print("\n✅ Análisis completado")
    elif choice == "2":
        backup_data(engine)
    elif choice == "3":
        truncate_tables(engine)
    elif choice == "4":
        drop_tables(engine)
    elif choice == "5":
        backup_file = backup_data(engine)
        if backup_file:
            truncate_tables(engine, confirm=True)
    elif choice == "6":
        backup_file = backup_data(engine)
        if backup_file:
            drop_tables(engine, confirm=True)
    elif choice == "0":
        print("\n👋 Saliendo...")
    else:
        print("\n❌ Opción inválida")
    
    print("\n" + "="*60)
    print("✅ Proceso completado")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
