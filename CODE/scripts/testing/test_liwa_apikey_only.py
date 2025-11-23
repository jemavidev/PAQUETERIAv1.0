#!/usr/bin/env python3
"""
Prueba usando solo API Key sin autenticación previa
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from app.config import settings

print("=" * 70)
print("PRUEBA CON API KEY DIRECTO (SIN AUTH) - LIWA.CO")
print("=" * 70)

# Probar diferentes combinaciones
tests = [
    {
        "name": "1. Solo API Key en header",
        "headers": {
            "Content-Type": "application/json",
            "X-API-Key": settings.liwa_api_key
        },
        "payload": {
            "to": "3044000678",
            "message": "Prueba desde PAQUETEX EL CLUB",
            "from": "PAQUETES"
        }
    },
    {
        "name": "2. API Key + Account en headers",
        "headers": {
            "Content-Type": "application/json",
            "X-API-Key": settings.liwa_api_key,
            "X-Account": settings.liwa_account
        },
        "payload": {
            "to": "3044000678",
            "message": "Prueba desde PAQUETEX EL CLUB",
            "from": "PAQUETES"
        }
    },
    {
        "name": "3. API Key en payload",
        "headers": {
            "Content-Type": "application/json"
        },
        "payload": {
            "to": "3044000678",
            "message": "Prueba desde PAQUETEX EL CLUB",
            "from": "PAQUETES",
            "api_key": settings.liwa_api_key
        }
    },
    {
        "name": "4. API Key + Account en payload",
        "headers": {
            "Content-Type": "application/json"
        },
        "payload": {
            "to": "3044000678",
            "message": "Prueba desde PAQUETEX EL CLUB",
            "from": "PAQUETES",
            "api_key": settings.liwa_api_key,
            "account": settings.liwa_account
        }
    },
    {
        "name": "5. Autenticación Basic",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": f"Basic {settings.liwa_api_key}"
        },
        "payload": {
            "to": "3044000678",
            "message": "Prueba desde PAQUETEX EL CLUB",
            "from": "PAQUETES"
        }
    }
]

for test in tests:
    print(f"\n{test['name']}")
    print(f"Headers: {list(test['headers'].keys())}")
    print(f"Payload keys: {list(test['payload'].keys())}")
    
    try:
        response = requests.post(
            "https://api.liwa.co/v2/sms/send",
            json=test['payload'],
            headers=test['headers'],
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Respuesta: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ ¡ÉXITO!")
            break
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 70)
