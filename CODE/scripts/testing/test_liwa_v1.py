#!/usr/bin/env python3
"""
Prueba con API v1 de Liwa.co
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from app.config import settings

print("=" * 70)
print("PRUEBA CON API v1 - LIWA.CO")
print("=" * 70)

# Probar con v1
tests = [
    {
        "name": "1. v1 con autenticación",
        "auth_url": "https://api.liwa.co/v1/auth/login",
        "sms_url": "https://api.liwa.co/v1/sms/send"
    },
    {
        "name": "2. v2 con token en query params",
        "auth_url": "https://api.liwa.co/v2/auth/login",
        "sms_url": "https://api.liwa.co/v2/sms/send"
    }
]

for test in tests:
    print(f"\n{test['name']}")
    print(f"Auth URL: {test['auth_url']}")
    print(f"SMS URL: {test['sms_url']}")
    
    # Autenticar
    try:
        auth_response = requests.post(
            test['auth_url'],
            json={
                "account": settings.liwa_account,
                "password": settings.liwa_password
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Auth Status: {auth_response.status_code}")
        
        if auth_response.status_code != 200:
            print(f"❌ Autenticación falló: {auth_response.text[:100]}")
            continue
            
        token = auth_response.json().get("token")
        if not token:
            print("❌ No se obtuvo token")
            continue
            
        print(f"✅ Token obtenido: {token[:20]}...{token[-10:]}")
        
        # Enviar SMS
        payload = {
            "to": "3044000678",
            "message": "Prueba desde PAQUETEX EL CLUB",
            "from": "PAQUETES"
        }
        
        # Probar con token en URL
        if "query" in test['name']:
            sms_response = requests.post(
                f"{test['sms_url']}?token={token}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        else:
            sms_response = requests.post(
                test['sms_url'],
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                timeout=10
            )
        
        print(f"SMS Status: {sms_response.status_code}")
        print(f"SMS Response: {sms_response.text[:200]}")
        
        if sms_response.status_code == 200:
            print("✅ ¡ÉXITO!")
            break
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Probar endpoint de información de cuenta
print("\n" + "=" * 70)
print("PRUEBA: Información de cuenta")
print("=" * 70)

try:
    # Primero autenticar
    auth_response = requests.post(
        "https://api.liwa.co/v2/auth/login",
        json={
            "account": settings.liwa_account,
            "password": settings.liwa_password
        },
        headers={"Content-Type": "application/json"}
    )
    
    if auth_response.status_code == 200:
        token = auth_response.json().get("token")
        
        # Probar endpoint de cuenta/info
        endpoints = [
            "https://api.liwa.co/v2/account",
            "https://api.liwa.co/v2/account/info",
            "https://api.liwa.co/v2/user",
            "https://api.liwa.co/v2/balance"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    timeout=5
                )
                print(f"\n{endpoint}")
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"Response: {response.text[:200]}")
            except:
                pass
                
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
