#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba de cache con autenticación
Versión: 1.0.0
Fecha: 2024-12-18
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "https://staging.jemavi.co"
# BASE_URL = "http://localhost:8000"

# Credenciales de prueba (cambiar según tu usuario)
USERNAME = "admin"  # o el usuario que tengas
PASSWORD = "tu_password_aqui"  # CAMBIAR

def print_header(text):
    """Imprimir header decorado"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_section(text):
    """Imprimir sección"""
    print(f"\n{text}")
    print("-" * 80)

def login(username, password):
    """Hacer login y obtener token"""
    print_section("🔐 Autenticación")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print(f"✅ Login exitoso")
            print(f"   Token: {token[:50]}...")
            return token
        else:
            print(f"❌ Login fallido: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_endpoint_with_cache(url, headers, test_name):
    """Probar endpoint con cache (2 llamadas)"""
    print_section(f"📊 Test: {test_name}")
    
    # Primera llamada (cache miss)
    print("Primera llamada (CACHE MISS):")
    start = time.time()
    try:
        response = requests.get(url, headers=headers, timeout=10)
        time_miss = (time.time() - start) * 1000
        
        print(f"  Status: {response.status_code}")
        print(f"  Tiempo: {time_miss:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                print(f"  Datos: {len(data)} campos")
            elif isinstance(data, list):
                print(f"  Datos: {len(data)} items")
        else:
            print(f"  Error: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return
    
    # Esperar un poco
    time.sleep(0.5)
    
    # Segunda llamada (cache hit esperado)
    print("\nSegunda llamada (CACHE HIT esperado):")
    start = time.time()
    try:
        response = requests.get(url, headers=headers, timeout=10)
        time_hit = (time.time() - start) * 1000
        
        print(f"  Status: {response.status_code}")
        print(f"  Tiempo: {time_hit:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                print(f"  Datos: {len(data)} campos")
            elif isinstance(data, list):
                print(f"  Datos: {len(data)} items")
        
        # Calcular mejora
        if time_miss > 0:
            improvement = ((time_miss - time_hit) / time_miss) * 100
            print(f"\n🚀 Mejora: {improvement:.1f}%")
            
            if improvement > 80:
                print("   ✅ EXCELENTE: Cache funcionando óptimamente")
            elif improvement > 50:
                print("   ✅ BUENO: Cache funcionando bien")
            elif improvement > 20:
                print("   ⚠️  ACEPTABLE: Cache funcionando")
            else:
                print("   ❌ PROBLEMA: Cache no está mejorando significativamente")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    """Función principal"""
    print_header("🧪 TEST DE CACHE CON AUTENTICACIÓN")
    print(f"URL Base: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login
    token = login(USERNAME, PASSWORD)
    
    if not token:
        print("\n❌ No se pudo obtener token. Verifica las credenciales.")
        print("\nPara usar este script:")
        print("1. Edita el archivo y cambia USERNAME y PASSWORD")
        print("2. O usa variables de entorno:")
        print("   export TEST_USERNAME='tu_usuario'")
        print("   export TEST_PASSWORD='tu_password'")
        return
    
    # Headers con autenticación
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Búsqueda de paquetes
    test_endpoint_with_cache(
        f"{BASE_URL}/api/packages?limit=10",
        headers,
        "Búsqueda de paquetes"
    )
    
    # Test 2: Estadísticas de dashboard
    test_endpoint_with_cache(
        f"{BASE_URL}/api/admin/dashboard",
        headers,
        "Estadísticas de dashboard"
    )
    
    # Test 3: Lista de clientes
    test_endpoint_with_cache(
        f"{BASE_URL}/api/admin/customers?limit=10",
        headers,
        "Lista de clientes"
    )
    
    # Test 4: Lista de usuarios
    test_endpoint_with_cache(
        f"{BASE_URL}/api/admin/users?limit=10",
        headers,
        "Lista de usuarios"
    )
    
    # Resumen final
    print_header("✅ PRUEBAS COMPLETADAS")
    print("\n💡 Notas:")
    print("   - Cache HIT debe ser significativamente más rápido que MISS")
    print("   - Mejora esperada: >80%")
    print("   - Si no hay mejora, verificar Redis y logs")
    print()

if __name__ == "__main__":
    import sys
    import os
    
    # Permitir credenciales por variables de entorno
    USERNAME = os.getenv("TEST_USERNAME", USERNAME)
    PASSWORD = os.getenv("TEST_PASSWORD", PASSWORD)
    
    if PASSWORD == "tu_password_aqui":
        print("=" * 80)
        print("⚠️  ADVERTENCIA: Debes configurar las credenciales")
        print("=" * 80)
        print("\nOpciones:")
        print("\n1. Editar el archivo y cambiar USERNAME y PASSWORD")
        print("\n2. Usar variables de entorno:")
        print("   export TEST_USERNAME='tu_usuario'")
        print("   export TEST_PASSWORD='tu_password'")
        print("   python3 test_cache_with_auth.py")
        print("\n3. Pasar como argumentos:")
        print("   python3 test_cache_with_auth.py usuario password")
        print()
        
        if len(sys.argv) >= 3:
            USERNAME = sys.argv[1]
            PASSWORD = sys.argv[2]
            print(f"✅ Usando credenciales de argumentos: {USERNAME}")
            main()
        else:
            sys.exit(1)
    else:
        main()
