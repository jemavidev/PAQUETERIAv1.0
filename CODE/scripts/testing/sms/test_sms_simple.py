#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para probar el envío de SMS usando LIWA.co
"""

import asyncio
import httpx
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

# Configuración desde .env
LIWA_API_KEY = os.getenv('LIWA_API_KEY')
LIWA_ACCOUNT = os.getenv('LIWA_ACCOUNT')
LIWA_PASSWORD = os.getenv('LIWA_PASSWORD')
LIWA_AUTH_URL = os.getenv('LIWA_AUTH_URL', 'https://api.liwa.co/v2/auth/login')

async def authenticate_liwa():
    """Autentica con LIWA.co y obtiene token"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "account": LIWA_ACCOUNT,
                "password": LIWA_PASSWORD
            }
            
            print(f"🔐 Autenticando con cuenta: {LIWA_ACCOUNT}")
            
            response = await client.post(
                LIWA_AUTH_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📡 Respuesta de autenticación: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    print(f"✅ Token obtenido exitosamente")
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

async def send_sms(token, number, message):
    """Envía SMS usando la API de LIWA"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Asegurar que el número tenga el código de país
            if not number.startswith("57"):
                number = f"57{number}"
            
            payload = {
                "number": number,
                "message": message,
                "type": 1
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "API-KEY": LIWA_API_KEY,
                "Content-Type": "application/json"
            }
            
            print(f"\n📤 Enviando SMS...")
            print(f"   • Número: {number}")
            print(f"   • Mensaje: {message}")
            print(f"   • Longitud: {len(message)} caracteres")
            
            response = await client.post(
                "https://api.liwa.co/v2/sms/single",
                json=payload,
                headers=headers
            )
            
            print(f"\n📡 Respuesta SMS: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta exitosa:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
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
    NUMERO_DESTINO = "3008103849"
    MENSAJE = "Hola ANGELICA! Este es un mensaje de prueba desde PAQUETEX EL CLUB. Sistema funcionando correctamente."
    
    print("=" * 70)
    print("PRUEBA DE ENVÍO DE SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    print(f"\n📱 Número destino: {NUMERO_DESTINO}")
    print(f"💬 Mensaje: {MENSAJE}")
    
    # Verificar configuración
    print(f"\n🔧 Verificando configuración...")
    if not all([LIWA_API_KEY, LIWA_ACCOUNT, LIWA_PASSWORD]):
        print(f"❌ Error: Faltan credenciales en el archivo .env")
        return
    
    print(f"   ✓ API Key: {LIWA_API_KEY[:20]}...")
    print(f"   ✓ Cuenta: {LIWA_ACCOUNT}")
    print(f"   ✓ URL Auth: {LIWA_AUTH_URL}")
    
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
    
    # Paso 2: Enviar SMS
    print(f"\n" + "=" * 50)
    print("PASO 2: ENVÍO DE SMS")
    print("=" * 50)
    
    result = await send_sms(token, NUMERO_DESTINO, MENSAJE)
    
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
