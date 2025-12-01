#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simula exactamente lo que hace el frontend al enviar el formulario
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"  # Cambiar si es diferente
API_URL = f"{BASE_URL}/api/customer-portal"

print("\n" + "="*70)
print("🌐 SIMULACIÓN DE FRONTEND - VERIFICACIÓN OTP")
print("="*70)

# Datos de prueba
phone = input("\nIngresa el teléfono (ej: 3002596319): ").strip()
code = input("Ingresa el código OTP: ").strip()

print(f"\n📋 Datos capturados del formulario:")
print(f"   Teléfono: '{phone}' (len={len(phone)})")
print(f"   Código: '{code}' (len={len(code)})")
print(f"   Bytes teléfono: {phone.encode('utf-8')}")
print(f"   Bytes código: {code.encode('utf-8')}")

# Preparar payload exactamente como lo haría el frontend
payload = {
    "phone": phone,
    "code": code
}

print(f"\n📤 Payload JSON:")
print(json.dumps(payload, indent=2))

# Hacer request
print(f"\n🌐 Enviando POST a {API_URL}/verify-otp...")

try:
    response = requests.post(
        f"{API_URL}/verify-otp",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"\n📥 Respuesta del servidor:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    try:
        response_data = response.json()
        print(f"\n   Body:")
        print(json.dumps(response_data, indent=2))
        
        if response.status_code == 200:
            print(f"\n✅ ¡ÉXITO!")
            if response_data.get('access_token'):
                print(f"   Token generado: {response_data['access_token'][:50]}...")
        else:
            print(f"\n❌ ERROR {response.status_code}")
            if 'detail' in response_data:
                print(f"   Mensaje: {response_data['detail']}")
    
    except Exception as e:
        print(f"\n   Body (texto): {response.text}")
        print(f"   Error parseando JSON: {e}")

except requests.exceptions.ConnectionError:
    print(f"\n❌ ERROR: No se pudo conectar al servidor")
    print(f"   ¿Está el servidor corriendo en {BASE_URL}?")
    print(f"\n   Para iniciar el servidor:")
    print(f"   cd CODE/src && uvicorn main:app --reload --host 0.0.0.0 --port 8000")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
