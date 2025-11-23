#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script directo para enviar SMS usando la API de LIWA.co
Basado en la prueba exitosa de Postman
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.config import settings

async def authenticate_liwa():
    """Autentica con LIWA.co y obtiene token"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "account": settings.liwa_account,
                "password": settings.liwa_password
            }
            
            print(f"🔐 Autenticando con cuenta: {settings.liwa_account}")
            
            response = await client.post(
                "https://api.liwa.co/v2/auth/login",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📡 Respuesta de autenticación: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Datos recibidos: {json.dumps(data, indent=2)}")
                
                # LIWA devuelve directamente el token, no un objeto con "success"
                if data.get("token"):
                    return data["token"]
                else:
                    print(f"❌ Error en respuesta: {data}")
                    return None
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return None

async def send_sms_direct(token, number, message):
    """Envía SMS usando exactamente el formato que funcionó en Postman"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "number": f"57{number}" if not number.startswith("57") else number,
                "message": message,
                "type": 1
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "API-KEY": settings.liwa_api_key,
                "Content-Type": "application/json"
            }
            
            print(f"📤 Enviando SMS...")
            print(f"   • URL: https://api.liwa.co/v2/sms/single")
            print(f"   • Número: {payload['number']}")
            print(f"   • Mensaje: {payload['message']}")
            
            response = await client.post(
                "https://api.liwa.co/v2/sms/single",
                json=payload,
                headers=headers
            )
            
            print(f"📡 Respuesta SMS: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta exitosa: {json.dumps(data, indent=2)}")
                return data
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error enviando SMS: {str(e)}")
        return None

async def main():
    """Función principal"""
    
    # Configuración
    NUMERO_DESTINO = "3002596319"
    MENSAJE = "Hola! Este es un mensaje de prueba desde PAQUETEX EL CLUB. Sistema funcionando correctamente."
    
    print("=" * 70)
    print("ENVÍO DIRECTO DE SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    print(f"\n📱 Número destino: {NUMERO_DESTINO}")
    print(f"💬 Mensaje: {MENSAJE}")
    print(f"📏 Longitud: {len(MENSAJE)} caracteres")
    
    # Verificar configuración
    print(f"\n🔧 Configuración:")
    print(f"   • API Key: {settings.liwa_api_key[:20]}...")
    print(f"   • Cuenta: {settings.liwa_account}")
    print(f"   • URL Auth: https://api.liwa.co/v2/auth/login")
    print(f"   • URL SMS: https://api.liwa.co/v2/sms/single")
    
    # Confirmar envío
    print(f"\n⚠️  ATENCIÓN: Este envío consumirá créditos reales")
    print(f"⚠️  Costo estimado: $0.50 COP")
    respuesta = input(f"\n¿Desea continuar con el envío? (s/n): ")
    
    if respuesta.lower() != 's':
        print(f"\n❌ Envío cancelado por el usuario")
        return
    
    # Paso 1: Autenticar
    print(f"\n" + "=" * 50)
    print("PASO 1: AUTENTICACIÓN")
    print("=" * 50)
    
    token = await authenticate_liwa()
    
    if not token:
        print(f"\n❌ No se pudo obtener el token de autenticación")
        return
    
    print(f"\n✅ Token obtenido exitosamente")
    print(f"Token: {token[:50]}...")
    
    # Paso 2: Enviar SMS
    print(f"\n" + "=" * 50)
    print("PASO 2: ENVÍO DE SMS")
    print("=" * 50)
    
    result = await send_sms_direct(token, NUMERO_DESTINO, MENSAJE)
    
    # Mostrar resultado final
    print(f"\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    
    if result and result.get("success"):
        print(f"\n✅ SMS ENVIADO EXITOSAMENTE")
        print(f"\n📋 Detalles:")
        print(f"   • Estado: {result.get('success')}")
        print(f"   • Mensaje ID: {result.get('menssageId', 'N/A')}")
        print(f"   • Respuesta: {result.get('message', 'SMS enviado')}")
        print(f"   • Costo: $0.50 COP")
        print(f"\n💡 El SMS debería llegar en los próximos segundos")
    else:
        print(f"\n❌ ERROR AL ENVIAR SMS")
        if result:
            print(f"   • Error: {result.get('message', 'Error desconocido')}")
        else:
            print(f"   • No se recibió respuesta del servidor")
    
    print(f"\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(main())