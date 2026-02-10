#!/usr/bin/env python3
"""
Test de productos en staging con autenticación
"""
import requests
import json

BASE_URL = "https://staging.jemavi.co"

# Crear sesión para mantener cookies
session = requests.Session()

print("=" * 60)
print("TEST: Productos en Staging")
print("=" * 60)

# 1. Verificar health check
print("\n1. Health Check...")
response = session.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   {response.json()}")

# 2. Intentar acceder a productos SIN autenticación
print("\n2. Intentar acceder a productos SIN autenticación...")
response = session.get(f"{BASE_URL}/api/v2/invoices/productos?skip=0&limit=5")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:200]}")

# 3. Login (necesitas proporcionar credenciales válidas)
print("\n3. Intentar login...")
print("   NOTA: Necesitas credenciales válidas para continuar")
print("   Puedes probar manualmente en: https://staging.jemavi.co/auth/login")

# 4. Verificar si hay cookies de sesión
print("\n4. Cookies actuales:")
for cookie in session.cookies:
    print(f"   {cookie.name}: {cookie.value[:20]}...")

print("\n" + "=" * 60)
print("CONCLUSIÓN:")
print("=" * 60)
print("El endpoint /api/v2/invoices/productos requiere autenticación.")
print("Para verlo funcionar:")
print("1. Accede a https://staging.jemavi.co/auth/login")
print("2. Inicia sesión con tus credenciales")
print("3. Navega a https://staging.jemavi.co/invoices/v2/productos")
print("4. Abre DevTools (F12) y revisa la consola y network")
print("=" * 60)
