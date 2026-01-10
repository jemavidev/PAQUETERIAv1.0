#!/usr/bin/env python3
"""
Script de prueba para verificar el endpoint /api/packages/
"""

import requests
import sys

def test_packages_endpoint(base_url: str = "http://localhost:8000"):
    """Probar el endpoint de packages"""
    
    print(f"\n🔍 Probando endpoint de packages en {base_url}")
    print("=" * 60)
    
    # 1. Probar endpoint de debug
    print("\n1. Probando /api/packages/debug/status...")
    try:
        response = requests.get(f"{base_url}/api/packages/debug/status", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Probar endpoint principal sin autenticación
    print("\n2. Probando /api/packages/ sin autenticación...")
    try:
        response = requests.get(f"{base_url}/api/packages/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ⚠️ Requiere autenticación (esperado)")
        else:
            data = response.json()
            print(f"   Packages: {len(data.get('packages', []))}")
            print(f"   Pagination: {data.get('pagination', {})}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Probar endpoint con no_cache
    print("\n3. Probando /api/packages/?no_cache=true...")
    try:
        response = requests.get(f"{base_url}/api/packages/?no_cache=true", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ⚠️ Requiere autenticación (esperado)")
        else:
            data = response.json()
            print(f"   Packages: {len(data.get('packages', []))}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_packages_endpoint(base_url)
