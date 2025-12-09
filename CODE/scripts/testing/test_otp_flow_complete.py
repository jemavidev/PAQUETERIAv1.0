#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el flujo completo de OTP
Prueba: Solicitar OTP → Verificar → Acceder al dashboard
"""

import requests
import json
import time

# Configuración
BASE_URL = "https://staging.jemavi.co"
# BASE_URL = "http://localhost:8000"

# Teléfono de prueba (debe existir en la base de datos)
TEST_PHONE = "3001234567"  # Cambiar por un teléfono real de prueba

def test_otp_flow():
    """Prueba el flujo completo de OTP"""
    
    print("=" * 60)
    print("PRUEBA DE FLUJO COMPLETO OTP")
    print("=" * 60)
    
    # Paso 1: Solicitar OTP
    print("\n📱 Paso 1: Solicitando contraseña temporal...")
    response = requests.post(
        f"{BASE_URL}/api/customer/preferences-otp/request",
        json={"phone": TEST_PHONE},
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("❌ Error al solicitar OTP")
        return
    
    print("✅ Contraseña temporal enviada")
    
    # Solicitar código al usuario
    print("\n" + "=" * 60)
    otp_code = input("🔑 Ingrese el código OTP recibido por SMS: ").strip()
    
    if not otp_code or len(otp_code) != 6:
        print("❌ Código inválido")
        return
    
    # Paso 2: Verificar OTP
    print("\n🔐 Paso 2: Verificando contraseña temporal...")
    response = requests.post(
        f"{BASE_URL}/api/customer/preferences-otp/verify",
        json={
            "phone": TEST_PHONE,
            "code": otp_code
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("❌ Error al verificar OTP")
        return
    
    data = response.json()
    token = data.get("access_token")
    
    if not token:
        print("❌ No se recibió token")
        return
    
    print("✅ Verificación exitosa")
    print(f"🔑 Token: {token[:20]}...")
    
    # Paso 3: Probar acceso al dashboard (API /me)
    print("\n👤 Paso 3: Obteniendo datos del cliente...")
    response = requests.get(
        f"{BASE_URL}/api/customer-portal/me",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        customer_data = response.json()
        print("✅ Datos del cliente obtenidos:")
        print(f"   - Nombre: {customer_data.get('full_name')}")
        print(f"   - Teléfono: {customer_data.get('phone')}")
        print(f"   - Email: {customer_data.get('email')}")
        print(f"   - Paquetes recibidos: {customer_data.get('total_packages_received', 0)}")
    else:
        print(f"❌ Error al obtener datos: {response.text}")
        return
    
    # Paso 4: Probar acceso a paquetes
    print("\n📦 Paso 4: Obteniendo historial de paquetes...")
    response = requests.get(
        f"{BASE_URL}/api/customer-portal/packages?limit=5",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        packages_data = response.json()
        packages = packages_data.get('packages', [])
        print(f"✅ Paquetes obtenidos: {len(packages)}")
        for i, pkg in enumerate(packages[:3], 1):
            print(f"   {i}. {pkg.get('tracking_number')} - {pkg.get('status')}")
    else:
        print(f"❌ Error al obtener paquetes: {response.text}")
        return
    
    # Paso 5: Probar acceso a preferencias
    print("\n⚙️  Paso 5: Obteniendo preferencias...")
    response = requests.get(
        f"{BASE_URL}/api/customer-portal/preferences/notifications",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        preferences = response.json()
        print("✅ Preferencias obtenidas:")
        print(f"   - SMS: {preferences.get('sms_notifications_enabled')}")
        print(f"   - Email: {preferences.get('email_notifications_enabled')}")
    else:
        print(f"❌ Error al obtener preferencias: {response.text}")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60)
    print(f"\n🌐 Ahora puedes acceder al dashboard en:")
    print(f"   {BASE_URL}/customer-portal/dashboard")
    print(f"\n💡 Guarda este token en localStorage del navegador:")
    print(f"   localStorage.setItem('customer_token', '{token}');")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_otp_flow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
