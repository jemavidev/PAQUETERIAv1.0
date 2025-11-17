#!/usr/bin/env python3
"""
Prueba directa con requests para comparar con httpx
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from app.config import settings

print("=" * 70)
print("PRUEBA DIRECTA CON REQUESTS - LIWA.CO")
print("=" * 70)

# 1. Autenticación
print("\n1. Autenticación...")
auth_payload = {
    "account": settings.liwa_account,
    "password": settings.liwa_password
}

auth_response = requests.post(
    settings.liwa_auth_url,
    json=auth_payload,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {auth_response.status_code}")
print(f"Respuesta: {auth_response.json()}")

if auth_response.status_code != 200:
    print("❌ Error en autenticación")
    sys.exit(1)

token = auth_response.json().get("token")
if not token:
    print("❌ No se obtuvo token")
    sys.exit(1)

print(f"✅ Token obtenido: {token[:20]}...{token[-10:]}")

# 2. Enviar SMS - Solo Bearer
print("\n2. Enviando SMS con Bearer Token...")
sms_payload = {
    "to": "3044000678",
    "message": "Prueba desde PAQUETEX EL CLUB",
    "from": "PAQUETES"
}

sms_response = requests.post(
    "https://api.liwa.co/v2/sms/send",
    json=sms_payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
)

print(f"Status: {sms_response.status_code}")
print(f"Respuesta: {sms_response.text}")

# 3. Enviar SMS - Bearer + API Key en header
print("\n3. Enviando SMS con Bearer + X-API-Key...")
sms_response2 = requests.post(
    "https://api.liwa.co/v2/sms/send",
    json=sms_payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "X-API-Key": settings.liwa_api_key
    }
)

print(f"Status: {sms_response2.status_code}")
print(f"Respuesta: {sms_response2.text}")

# 4. Enviar SMS - Bearer + API Key en payload
print("\n4. Enviando SMS con Bearer + api_key en payload...")
sms_payload_with_key = {
    **sms_payload,
    "api_key": settings.liwa_api_key
}

sms_response3 = requests.post(
    "https://api.liwa.co/v2/sms/send",
    json=sms_payload_with_key,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
)

print(f"Status: {sms_response3.status_code}")
print(f"Respuesta: {sms_response3.text}")

print("\n" + "=" * 70)
