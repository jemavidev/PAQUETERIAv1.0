#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Script de Limpieza con Autenticación
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo

Este script ejecuta la limpieza de base de datos con autenticación.
"""

import requests
import json
import sys
from pathlib import Path

def login_and_cleanup():
    """Autenticarse y ejecutar limpieza"""
    
    # URL base de la aplicación
    base_url = "http://localhost:8000"
    
    # Credenciales de administrador (necesitamos crearlas o usar las existentes)
    admin_credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    print("🚀 PAQUETES EL CLUB v4.0 - Limpieza con Autenticación")
    print("="*60)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    try:
        # Verificar que la aplicación esté ejecutándose
        health_url = f"{base_url}/health"
        response = session.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Aplicación ejecutándose correctamente")
        else:
            print("❌ La aplicación no está respondiendo correctamente")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar a la aplicación: {e}")
        return False
    
    # Intentar autenticación
    print("\n🔐 Intentando autenticación...")
    
    try:
        # Intentar login
        login_url = f"{base_url}/auth/login"
        login_data = {
            "username": admin_credentials["username"],
            "password": admin_credentials["password"]
        }
        
        response = session.post(login_url, data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Autenticación exitosa")
        else:
            print(f"❌ Error de autenticación: {response.status_code}")
            print("💡 Intentando crear usuario administrador...")
            
            # Intentar crear usuario administrador
            register_url = f"{base_url}/auth/register"
            register_data = {
                "username": admin_credentials["username"],
                "email": "admin@paqueteselclub.com",
                "password": admin_credentials["password"],
                "full_name": "Administrador",
                "phone": "3000000000",
                "role": "ADMIN"
            }
            
            response = session.post(register_url, json=register_data, timeout=10)
            
            if response.status_code == 200 or response.status_code == 201:
                print("✅ Usuario administrador creado")
                # Intentar login nuevamente
                response = session.post(login_url, data=login_data, timeout=10)
                if response.status_code != 200:
                    print("❌ Error al autenticarse después de crear usuario")
                    return False
            else:
                print(f"❌ Error al crear usuario: {response.status_code}")
                return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error durante la autenticación: {e}")
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
    
    # Ejecutar limpieza
    print("\n🧹 Iniciando limpieza...")
    
    try:
        # Hacer la petición POST al endpoint de limpieza
        cleanup_url = f"{base_url}/admin/cleanup-database"
        response = session.post(cleanup_url, timeout=60)
        
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
    
    success = login_and_cleanup()
    
    if success:
        print("\n✅ Limpieza completada exitosamente")
    else:
        print("\n❌ Error durante la limpieza")
        sys.exit(1)

if __name__ == "__main__":
    main()
