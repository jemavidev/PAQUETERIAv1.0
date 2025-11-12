#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Script de Limpieza via API
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script ejecuta la limpieza de base de datos a través de la API de la aplicación.
"""

import requests
import json
import sys
from pathlib import Path

def cleanup_via_api():
    """Ejecutar limpieza a través de la API"""
    
    # URL base de la aplicación
    base_url = "http://localhost:8000"
    
    # Endpoint de limpieza (necesitamos crearlo)
    cleanup_url = f"{base_url}/admin/cleanup-database"
    
    print("🚀 PAQUETES EL CLUB v1.0 - Limpieza via API")
    print("="*50)
    
    try:
        # Verificar que la aplicación esté ejecutándose
        health_url = f"{base_url}/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Aplicación ejecutándose correctamente")
        else:
            print("❌ La aplicación no está respondiendo correctamente")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar a la aplicación: {e}")
        print("💡 Asegúrate de que la aplicación esté ejecutándose en http://localhost:8000")
        return False
    
    # Por ahora, vamos a usar el script de limpieza directo
    print("📊 Ejecutando limpieza directa...")
    
    # Crear script de limpieza temporal
    cleanup_script = """
import sys
sys.path.append('/app/src')

from app.core.database import get_database_url
from sqlalchemy import create_engine, text

# Obtener conexión
database_url = get_database_url()
engine = create_engine(database_url)

# Tablas a limpiar en orden correcto
tables = [
    'file_uploads',
    'messages', 
    'package_history',
    'package_announcements_new',
    'packages',
    'customers'
]

total_deleted = 0

with engine.connect() as conn:
    for table in tables:
        try:
            # Contar registros
            result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.scalar()
            
            if count > 0:
                # Eliminar registros
                result = conn.execute(text(f'DELETE FROM {table}'))
                deleted = result.rowcount
                total_deleted += deleted
                print(f'🗑️ {table}: {deleted} registros eliminados')
            else:
                print(f'✅ {table}: Ya está vacía')
                
        except Exception as e:
            print(f'❌ Error en {table}: {e}')
    
    conn.commit()
    print(f'🎉 Total eliminado: {total_deleted} registros')
"""
    
    # Escribir script temporal
    with open('/tmp/cleanup_temp.py', 'w') as f:
        f.write(cleanup_script)
    
    # Ejecutar script en el contenedor
    import subprocess
    result = subprocess.run([
        'docker', 'exec', 'paqueteria_v40_app', 
        'python3', '/tmp/cleanup_temp.py'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errores:", result.stderr)
    
    return result.returncode == 0

def main():
    """Función principal"""
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar desde la raíz del proyecto")
        sys.exit(1)
    
    success = cleanup_via_api()
    
    if success:
        print("\n✅ Limpieza completada exitosamente")
    else:
        print("\n❌ Error durante la limpieza")
        sys.exit(1)

if __name__ == "__main__":
    main()
