#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Script de Limpieza Automática
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script ejecuta la limpieza de base de datos automáticamente.
"""

import requests
import json
import sys
from pathlib import Path

def cleanup_via_endpoint():
    """Ejecutar limpieza a través del endpoint de la aplicación"""
    
    # URL base de la aplicación
    base_url = "http://localhost:8000"
    
    # Endpoint de limpieza
    cleanup_url = f"{base_url}/admin/cleanup-database"
    
    print("🚀 PAQUETES EL CLUB v1.0 - Limpieza Automática")
    print("="*60)
    
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
    
    # Ejecutar limpieza automáticamente
    print("\n🧹 Iniciando limpieza automática...")
    
    try:
        # Hacer la petición POST al endpoint
        response = requests.post(cleanup_url, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Limpieza completada exitosamente")
            print(f"📊 Total de registros eliminados: {result.get('total_deleted', 0)}")
            print(f"⏰ Timestamp: {result.get('timestamp', 'N/A')}")
            
            # Mostrar resultados detallados
            print("\n📋 Resultados detallados:")
            results = result.get('results', {})
            for table, data in results.items():
                if 'error' in data:
                    print(f"❌ {table}: Error - {data['error']}")
                else:
                    before = data.get('before', 0)
                    deleted = data.get('deleted', 0)
                    after = data.get('after', 0)
                    print(f"📊 {table}: {before} → {deleted} eliminados → {after} restantes")
            
            return True
            
        elif response.status_code == 403:
            print("❌ Error: No tienes permisos de administrador")
            print("💡 Asegúrate de estar logueado como administrador")
            return False
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"💡 Detalle: {error_data.get('detail', 'Error desconocido')}")
            except:
                print(f"💡 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error durante la petición: {e}")
        return False

def main():
    """Función principal"""
    if not (Path.cwd() / "CODE" / "LOCAL").exists():
        print("❌ Error: Ejecutar desde la raíz del proyecto")
        sys.exit(1)
    
    success = cleanup_via_endpoint()
    
    if success:
        print("\n✅ Limpieza completada exitosamente")
    else:
        print("\n❌ Error durante la limpieza")
        sys.exit(1)

if __name__ == "__main__":
    main()
