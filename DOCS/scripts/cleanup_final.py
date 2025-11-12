#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Script de Limpieza Final
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script ejecuta la limpieza directamente usando psql en el contenedor.
"""

import subprocess
import sys
from pathlib import Path

def cleanup_via_psql():
    """Ejecutar limpieza usando psql en el contenedor"""
    
    print("🚀 PAQUETES EL CLUB v1.0 - Limpieza Final")
    print("="*60)
    
    # Mostrar advertencia
    print("\n" + "="*60)
    print("⚠️  ADVERTENCIA: LIMPIEZA DE BASE DE DATOS  ⚠️")
    print("="*60)
    print("Este script eliminará TODOS los datos de las siguientes tablas:")
    print("• packages")
    print("• package_history") 
    print("• package_announcements_new")
    print("• messages")
    print("• file_uploads")
    print("• customers")
    print("\nEsta acción NO SE PUEDE DESHACER.")
    print("="*60)
    
    # Ejecutar limpieza usando psql en el contenedor
    print("\n🧹 Iniciando limpieza...")
    
    # Script SQL de limpieza
    cleanup_sql = """
-- Obtener conteo actual
SELECT 'file_uploads' as table_name, COUNT(*) as count FROM file_uploads
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'package_history', COUNT(*) FROM package_history
UNION ALL
SELECT 'package_announcements_new', COUNT(*) FROM package_announcements_new
UNION ALL
SELECT 'packages', COUNT(*) FROM packages
UNION ALL
SELECT 'customers', COUNT(*) FROM customers;

-- Limpiar tablas en orden correcto
DELETE FROM file_uploads;
DELETE FROM messages;
DELETE FROM package_history;
DELETE FROM package_announcements_new;
DELETE FROM packages;
DELETE FROM customers;

-- Verificar limpieza
SELECT 'file_uploads' as table_name, COUNT(*) as count FROM file_uploads
UNION ALL
SELECT 'messages', COUNT(*) FROM messages
UNION ALL
SELECT 'package_history', COUNT(*) FROM package_history
UNION ALL
SELECT 'package_announcements_new', COUNT(*) FROM package_announcements_new
UNION ALL
SELECT 'packages', COUNT(*) FROM packages
UNION ALL
SELECT 'customers', COUNT(*) FROM customers;
"""
    
    try:
        # Ejecutar psql en el contenedor
        result = subprocess.run([
            'docker', 'exec', 'paqueteria_v40_app',
            'psql', '-h', 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
            '-p', '5432',
            '-U', 'jveyes',
            '-d', 'paqueteria_v4',
            '-c', cleanup_sql
        ], capture_output=True, text=True, timeout=60)
        
        print("📊 Resultados de la limpieza:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errores:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Limpieza completada exitosamente")
            return True
        else:
            print("❌ Error durante la limpieza")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout durante la limpieza")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar desde la raíz del proyecto")
        sys.exit(1)
    
    success = cleanup_via_psql()
    
    if success:
        print("\n✅ Limpieza completada exitosamente")
    else:
        print("\n❌ Error durante la limpieza")
        sys.exit(1)

if __name__ == "__main__":
    main()
