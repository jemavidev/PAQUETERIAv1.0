#!/usr/bin/env python3
"""
Script para eliminar el sistema completo de invoices/facturas
ADVERTENCIA: Esta operación es IRREVERSIBLE
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "CODE"))

from sqlalchemy import create_engine, text
from app.config import settings

def confirmar_eliminacion():
    """Solicitar confirmación múltiple antes de eliminar"""
    print("=" * 60)
    print("⚠️  ADVERTENCIA: ELIMINACIÓN DE SISTEMA DE INVOICES")
    print("=" * 60)
    print()
    print("Este script eliminará PERMANENTEMENTE las siguientes tablas:")
    print()
    print("  1. invoice_irregularities    - Irregularidades detectadas")
    print("  2. invoice_items             - Items/productos de facturas")
    print("  3. invoice_rejected_files    - Archivos rechazados")
    print("  4. invoices                  - Facturas principales")
    print("  5. supplier_invoices         - Facturas de proveedores")
    print("  6. suppliers                 - Proveedores")
    print("  7. cufe_records              - Registros CUFE")
    print()
    print("TABLAS QUE NO SE ELIMINARÁN (sistema principal):")
    print("  ✓ users, customers, packages, notifications, rates, reports")
    print("  ✓ products, product_column_config, product_sync_log")
    print()
    print("=" * 60)
    print("⚠️  ESTA OPERACIÓN ES IRREVERSIBLE")
    print("=" * 60)
    print()
    
    # Primera confirmación
    respuesta1 = input("¿Estás seguro de que deseas continuar? (escribe 'SI' en mayúsculas): ")
    if respuesta1 != "SI":
        print("\n❌ Operación cancelada por el usuario")
        return False
    
    # Segunda confirmación
    print()
    print("⚠️  ÚLTIMA ADVERTENCIA")
    print()
    respuesta2 = input("Escribe 'ELIMINAR INVOICES' para confirmar: ")
    if respuesta2 != "ELIMINAR INVOICES":
        print("\n❌ Operación cancelada por el usuario")
        return False
    
    return True


def eliminar_tablas():
    """Ejecutar el script SQL de eliminación"""
    
    if not confirmar_eliminacion():
        return
    
    print()
    print("=" * 60)
    print("🔄 Conectando a la base de datos...")
    print("=" * 60)
    
    # Crear conexión
    engine = create_engine(settings.DATABASE_URL)
    
    # Leer el script SQL
    script_path = Path(__file__).parent / "eliminar_sistema_invoices.sql"
    with open(script_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    print(f"📄 Script SQL cargado desde: {script_path}")
    print()
    
    try:
        with engine.connect() as conn:
            print("🔄 Ejecutando eliminación de tablas...")
            print()
            
            # Ejecutar el script
            conn.execute(text(sql_script))
            conn.commit()
            
            print()
            print("=" * 60)
            print("✅ ELIMINACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print()
            print("Las siguientes tablas han sido eliminadas:")
            print("  ✓ invoice_irregularities")
            print("  ✓ invoice_items")
            print("  ✓ invoice_rejected_files")
            print("  ✓ invoices")
            print("  ✓ supplier_invoices")
            print("  ✓ suppliers")
            print("  ✓ cufe_records")
            print()
            print("Tablas del sistema principal (NO eliminadas):")
            print("  ✓ users, customers, packages, notifications")
            print("  ✓ products, product_column_config, product_sync_log")
            print()
            print("=" * 60)
            
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR AL ELIMINAR TABLAS")
        print("=" * 60)
        print(f"Error: {str(e)}")
        print()
        print("Posibles causas:")
        print("  - Las tablas no existen")
        print("  - Hay dependencias que no se pudieron eliminar")
        print("  - Problemas de permisos en la base de datos")
        print()
        sys.exit(1)
    
    finally:
        engine.dispose()


def main():
    """Función principal"""
    print()
    print("=" * 60)
    print("SCRIPT DE ELIMINACIÓN DE SISTEMA DE INVOICES")
    print("=" * 60)
    print()
    print(f"Base de datos: {settings.POSTGRES_DB}")
    print(f"Host: {settings.POSTGRES_HOST}")
    print()
    
    eliminar_tablas()


if __name__ == "__main__":
    main()
