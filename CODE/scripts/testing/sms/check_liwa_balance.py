#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consultar el saldo de la cuenta LIWA
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
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    print(f"✅ Token obtenido exitosamente")
                    return data["token"]
            
            print(f"❌ Error de autenticación: {response.status_code}")
            return None
                
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return None

async def check_balance_endpoint(token, endpoint, method="GET"):
    """Prueba un endpoint para consultar saldo"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "API-KEY": LIWA_API_KEY,
                "Content-Type": "application/json"
            }
            
            url = f"https://api.liwa.co{endpoint}"
            
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, headers=headers, json={})
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
                
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": "error",
            "success": False,
            "error": str(e)
        }

async def main():
    """Función principal"""
    
    print("=" * 70)
    print("CONSULTA DE SALDO - LIWA.CO")
    print("=" * 70)
    
    # Autenticar
    print("\n🔑 PASO 1: AUTENTICACIÓN")
    print("-" * 70)
    token = await authenticate_liwa()
    
    if not token:
        print("\n❌ No se pudo obtener el token de autenticación")
        return
    
    # Probar diferentes endpoints comunes para consultar saldo
    print("\n📊 PASO 2: PROBANDO ENDPOINTS DE SALDO")
    print("-" * 70)
    
    endpoints_to_try = [
        ("/v2/account/balance", "GET"),
        ("/v2/account/credits", "GET"),
        ("/v2/account/info", "GET"),
        ("/v2/account", "GET"),
        ("/v2/balance", "GET"),
        ("/v2/credits", "GET"),
        ("/v2/user/balance", "GET"),
        ("/v2/user/credits", "GET"),
        ("/v2/user/info", "GET"),
        ("/v2/me", "GET"),
        ("/v2/account/status", "GET"),
    ]
    
    print(f"\nProbando {len(endpoints_to_try)} posibles endpoints...\n")
    
    results = []
    for endpoint, method in endpoints_to_try:
        print(f"Probando: {method} {endpoint}...", end=" ")
        result = await check_balance_endpoint(token, endpoint, method)
        results.append(result)
        
        if result["success"]:
            print(f"✅ {result['status']}")
        else:
            print(f"❌ {result['status']}")
    
    # Mostrar resultados exitosos
    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    
    successful = [r for r in results if r["success"]]
    
    if successful:
        print(f"\n✅ Se encontraron {len(successful)} endpoint(s) funcional(es):\n")
        
        for result in successful:
            print(f"📍 {result['method']} {result['endpoint']}")
            print(f"   Status: {result['status']}")
            print(f"   Respuesta:")
            print(json.dumps(result['data'], indent=4, ensure_ascii=False))
            print()
    else:
        print("\n⚠️  No se encontró un endpoint público para consultar el saldo")
        print("\nPosibles razones:")
        print("   • LIWA no expone un endpoint público de saldo")
        print("   • El saldo solo se puede consultar desde el panel web")
        print("   • Se requiere un endpoint o permiso especial")
        print("\n💡 Alternativas:")
        print("   • Consultar saldo en: https://liwa.co/dashboard")
        print("   • Contactar soporte de LIWA para documentación del API")
        print("   • Llevar control manual de SMS enviados")
        print("\n📊 Según la documentación (17/11/2025):")
        print("   • Saldo: 73,598 créditos")
        print("   • Costo por SMS: $0.50 COP")
        print("   • SMS disponibles: ~147,196 mensajes")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
