#!/usr/bin/env python3
"""
Prueba exhaustiva final con todas las combinaciones posibles
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from app.config import settings

print("=" * 70)
print("PRUEBA EXHAUSTIVA FINAL - LIWA.CO")
print("=" * 70)
print(f"API Key: {settings.liwa_api_key}")
print(f"Account: {settings.liwa_account}")
print("=" * 70)

# Autenticar
auth_response = requests.post(
    "https://api.liwa.co/v2/auth/login",
    json={
        "account": settings.liwa_account,
        "password": settings.liwa_password
    },
    headers={"Content-Type": "application/json"}
)

if auth_response.status_code != 200:
    print("❌ Error en autenticación")
    sys.exit(1)

token = auth_response.json().get("token")
print(f"\n✅ Token obtenido: {token[:30]}...{token[-20:]}")

# Payload base
base_payload = {
    "to": "3044000678",
    "message": "Prueba desde PAQUETEX EL CLUB",
    "from": "PAQUETES"
}

# Todas las combinaciones posibles
tests = [
    {
        "name": "1. Bearer en Authorization",
        "headers": {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        "payload": base_payload
    },
    {
        "name": "2. Token en Authorization (sin Bearer)",
        "headers": {
            "Authorization": token,
            "Content-Type": "application/json"
        },
        "payload": base_payload
    },
    {
        "name": "3. Token en header X-Auth-Token",
        "headers": {
            "X-Auth-Token": token,
            "Content-Type": "application/json"
        },
        "payload": base_payload
    },
    {
        "name": "4. Token en payload",
        "headers": {
            "Content-Type": "application/json"
        },
        "payload": {**base_payload, "token": token}
    },
    {
        "name": "5. Bearer + API Key en header",
        "headers": {
            "Authorization": f"Bearer {token}",
            "X-API-Key": settings.liwa_api_key,
            "Content-Type": "application/json"
        },
        "payload": base_payload
    },
    {
        "name": "6. Bearer + API Key en payload",
        "headers": {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        "payload": {**base_payload, "apiKey": settings.liwa_api_key}
    },
    {
        "name": "7. Bearer + API Key (snake_case) en payload",
        "headers": {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        "payload": {**base_payload, "api_key": settings.liwa_api_key}
    },
    {
        "name": "8. Token + Account en payload",
        "headers": {
            "Content-Type": "application/json"
        },
        "payload": {
            **base_payload,
            "token": token,
            "account": settings.liwa_account
        }
    },
    {
        "name": "9. Solo API Key en header (sin token)",
        "headers": {
            "X-API-Key": settings.liwa_api_key,
            "Content-Type": "application/json"
        },
        "payload": base_payload
    },
    {
        "name": "10. API Key como Bearer",
        "headers": {
            "Authorization": f"Bearer {settings.liwa_api_key}",
            "Content-Type": "application/json"
        },
        "payload": base_payload
    },
]

for test in tests:
    print(f"\n{test['name']}")
    print(f"   Headers: {list(test['headers'].keys())}")
    print(f"   Payload keys: {list(test['payload'].keys())}")
    
    try:
        response = requests.post(
            "https://api.liwa.co/v2/sms/send",
            json=test['payload'],
            headers=test['headers'],
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ ¡ÉXITO!")
            print(f"   Response: {response.text}")
            break
        else:
            resp_text = response.text[:100] if len(response.text) > 100 else response.text
            print(f"   ❌ {resp_text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
