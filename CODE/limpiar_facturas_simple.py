#!/usr/bin/env python3
"""
Script simple para limpiar TODAS las facturas usando SQL directo
ADVERTENCIA: Esta operación es IRREVERSIBLE
"""

import os
import sys
import psycopg2
from pathlib import Path

def cargar_env():
    """Carga variables de entorno desde .env"""
    env_path = Path(__file__).parent / '.env'
    env_vars = {}
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"').strip("'")
    
    return env_vars

def limpiar_archivos_pdf():
    """Elimina todos los archivos PDF de facturas"""
    pdf_directory = Path(__file__).parent / "src" / "uploads" / "invoices"
    
    if not pdf_directory.exists():
        print(f"✓ Directorio {pdf_directory} no existe")
        return 0
    
    archivos_eliminados = 0
    for archivo in pdf_directory.glob("*.pdf"):
        try:
            archivo.unlink()
            archivos_eliminados += 1
        except Exception as e:
            print(f"✗ Error eliminando {archivo.name}: {e}")
    
    print(f"✓ {archivos_eliminados} archivos PDF eliminados")
    return archivos_eliminados

def limpiar_base_datos(env_vars):
    """Elimina todos los registros de las tablas de facturas"""
    
    # Conectar a la base de datos
    try:
        conn = psycopg2.connect(
            host=env_vars.get('POSTGRES_HOST', 'localhost'),
            port=env_vars.get('POSTGRES_PORT', '5432'),
            database=env_vars.get('POSTGRES_DB', 'paquetex'),
            user=env_vars.get('POSTGRES_USER', 'postgres'),
            password=env_vars.get('POSTGRES_PASSWORD', '')
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("\n=== LIMPIEZA DE BASE DE DATOS ===\n")
        
        # Contar registros antes de eliminar
        cursor.execute("SELECT COUNT(*) FROM invoice_irregularities")
        count_irregularities = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoice_items")
        count_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoices")
        count_invoices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        count_suppliers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoice_rejected_files")
        count_rejected = cursor.fetchone()[0]
        
        print(f"Registros a eliminar:")
        print(f"  - Irregularidades: {count_irregularities}")
        print(f"  - Items: {count_items}")
        print(f"  - Facturas: {count_invoices}")
        print(f"  - Proveedores: {count_suppliers}")
        print(f"  - Archivos rechazados: {count_rejected}")
        print()
        
        # Eliminar en orden (respetando foreign keys)
        cursor.execute("DELETE FROM invoice_irregularities")
        print(f"✓ {count_irregularities} irregularidades eliminadas")
        
        cursor.execute("DELETE FROM invoice_items")
        print(f"✓ {count_items} items de facturas eliminados")
        
        cursor.execute("DELETE FROM invoices")
        print(f"✓ {count_invoices} facturas eliminadas")
        
        cursor.execute("DELETE FROM suppliers")
        print(f"✓ {count_suppliers} proveedores eliminados")
        
        cursor.execute("DELETE FROM invoice_rejected_files")
        print(f"✓ {count_rejected} archivos rechazados eliminados")
        
        # Commit
        conn.commit()
        print("\n✓ Todos los cambios guardados en la base de datos")
        
        # Resetear secuencias
        print("\n=== RESETEO DE SECUENCIAS ===\n")
        
        tablas = [
            'invoice_irregularities',
            'invoice_items',
            'invoices',
            'suppliers',
            'invoice_rejected_files'
        ]
        
        for tabla in tablas:
            try:
                cursor.execute(f"ALTER SEQUENCE {tabla}_id_seq RESTART WITH 1")
                print(f"✓ Secuencia de {tabla} reseteada")
            except Exception as e:
                print(f"⚠ No se pudo resetear {tabla}: {e}")
        
        conn.commit()
        print("\n✓ Secuencias reseteadas")
        
        cursor.close()
        conn.close()
        
        return {
            'irregularities': count_irregularities,
            'items': count_items,
            'invoices': count_invoices,
            'suppliers': count_suppliers,
            'rejected': count_rejected
        }
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

def main():
    print("=" * 60)
    print("LIMPIEZA COMPLETA DE FACTURAS")
    print("=" * 60)
    print("\n⚠️  ADVERTENCIA: Esta operación eliminará:")
    print("   - Todas las facturas")
    print("   - Todos los items de facturas")
    print("   - Todas las irregularidades")
    print("   - Todos los proveedores")
    print("   - Todos los archivos rechazados")
    print("   - Todos los archivos PDF")
    print("\n⚠️  ESTA OPERACIÓN ES IRREVERSIBLE\n")
    
    respuesta = input("¿Estás seguro de continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta.strip().upper() != 'SI':
        print("\n✗ Operación cancelada")
        return
    
    print("\n🚀 Iniciando limpieza...\n")
    
    # Cargar variables de entorno
    env_vars = cargar_env()
    
    # Limpiar base de datos
    stats = limpiar_base_datos(env_vars)
    
    # Limpiar archivos
    print("\n=== LIMPIEZA DE ARCHIVOS ===\n")
    archivos = limpiar_archivos_pdf()
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE LIMPIEZA")
    print("=" * 60)
    print(f"Irregularidades eliminadas: {stats['irregularities']}")
    print(f"Items eliminados: {stats['items']}")
    print(f"Facturas eliminadas: {stats['invoices']}")
    print(f"Proveedores eliminados: {stats['suppliers']}")
    print(f"Archivos rechazados eliminados: {stats['rejected']}")
    print(f"Archivos PDF eliminados: {archivos}")
    print("=" * 60)
    print("\n✅ Limpieza completada exitosamente")
    print("   Ahora puedes importar las facturas nuevamente\n")

if __name__ == "__main__":
    main()
