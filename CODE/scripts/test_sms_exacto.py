#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar exactamente el mismo código del servicio SMS
"""

import asyncio
import sys
from pathlib import Path
import httpx
import uuid

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.sms_service import SMSService
from app.config import settings


async def test_sms_service_exact():
    """Probar exactamente el servicio SMS"""
    
    print("=" * 70)
    print("TEST SMS SERVICIO EXACTO - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        sms_service = SMSService()
        config = sms_service.get_sms_config(db)
        
        recipient = "+573002596319"
        message = "PAQUETES: Su paquete LTEM está ENTREGADO exitosamente. Código: LTEM"
        
        print(f"\n📱 Datos del envío:")
        print(f"   • Destinatario: {recipient}")
        print(f"   • Mensaje: {message}")
        print(f"   • Longitud: {len(message)} caracteres")
        
        # Probar paso a paso exactamente como el servicio
        print(f"\n🔧 Probando paso a paso...")
        
        # 1. Obtener token
        print(f"\n1️⃣ Obteniendo token...")
        token = await sms_service.get_valid_token(config)
        print(f"   ✅ Token: {token[:50]}...")
        
        # 2. Preparar payload exactamente igual
        print(f"\n2️⃣ Preparando payload...")
        phone_number = recipient
        # Limpiar el número y asegurar formato correcto
        if phone_number.startswith("+57"):
            phone_number = phone_number[1:]  # Remover el + pero mantener 57
        elif phone_number.startswith("+"):
            phone_number = phone_number[1:]  # Remover solo el +
        elif not phone_number.startswith("57"):
            phone_number = f"57{phone_number}"
        
        payload = {
            "number": phone_number,
            "message": message,
            "type": 1
        }
        print(f"   ✅ Payload: {payload}")
        
        # 3. Preparar headers exactamente igual
        print(f"\n3️⃣ Preparando headers...")
        headers = {
            "Authorization": f"Bearer {token}",
            "API-KEY": config.api_key,
            "Content-Type": "application/json"
        }
        print(f"   ✅ Headers preparados (API-KEY: {config.api_key[:20]}...)")
        
        # 4. Enviar exactamente igual
        print(f"\n4️⃣ Enviando SMS...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            sms_url = "https://api.liwa.co/v2/sms/single"
            print(f"   🌐 URL: {sms_url}")
            
            response = await client.post(sms_url, json=payload, headers=headers)
            print(f"   📡 Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ Error HTTP: {response.text}")
                return
            
            data = response.json()
            print(f"   📋 Respuesta completa: {data}")
            
            if data.get("success"):
                print(f"\n✅ SMS ENVIADO EXITOSAMENTE")
                print(f"   • Mensaje ID: {data.get('menssageId')}")
                print(f"   • Mensaje: {data.get('message')}")
            else:
                print(f"\n❌ SMS FALLÓ")
                print(f"   • Error: {data.get('message')}")
                print(f"   • Datos completos: {data}")
        
        print(f"\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_sms_service_exact())