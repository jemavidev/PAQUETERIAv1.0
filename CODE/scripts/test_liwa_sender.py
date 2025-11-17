#!/usr/bin/env python3
"""
Prueba con diferentes remitentes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
from app.config import settings

print("=" * 70)
print("PRUEBA CON DIFERENTES REMITENTES - LIWA.CO")
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
print(f"✅ Token obtenido: {token[:20]}...{token[-10:]}")

# Probar diferentes remitentes
senders = [
    "PAQUETES",
    "PAPYRUS",
    "PAQUETEX",
    "INFO",
    "SMS",
    None,  # Sin remitente
    "",    # Remitente vacío
    "00486396309",  # Número de cuenta
]

for sender in senders:
    print(f"\n{'=' * 70}")
    print(f"Probando remitente: {repr(sender)}")
    
    payload = {
        "to": "3044000678",
        "message": "Prueba desde PAQUETEX EL CLUB"
    }
    
    if sender is not None:
        payload["from"] = sender
    
    try:
        response = requests.post(
            "https://api.liwa.co/v2/sms/send",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ ¡ÉXITO! Este remitente funciona")
            break
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 70)
