#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para explorar la API de LIWA y descubrir endpoints disponibles
"""

import asyncio
import httpx
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
            
            response = await client.post(
                LIWA_AUTH_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("token"):
                    return data["token"]
            return None
                
    except Exception as e:
        return None

async def test_endpoint(token, endpoint, method="GET", payload=None):
    """Prueba un endpoint de la API"""
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
            elif method == "POST":
                response = await client.post(url, headers=headers, json=payload or {})
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=payload or {})
            else:
                return None
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status": response.status_code,
                "success": response.status_code in [200, 201],
                "data": response.json() if response.status_code in [200, 201] else None,
                "error": response.text if response.status_code not in [200, 201] else None
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
    
    print("=" * 80)
    print("EXPLORACIÓN DE LA API DE LIWA.CO")
    print("=" * 80)
    
    # Autenticar
    print("\n🔑 Autenticando...")
    token = await authenticate_liwa()
    
    if not token:
        print("❌ No se pudo obtener el token de autenticación")
        return
    
    print("✅ Autenticación exitosa")
    
    # Definir categorías de endpoints a probar
    endpoints_categories = {
        "📊 INFORMACIÓN DE CUENTA": [
            ("/v2/account", "GET"),
            ("/v2/account/info", "GET"),
            ("/v2/account/profile", "GET"),
            ("/v2/account/details", "GET"),
            ("/v2/user", "GET"),
            ("/v2/user/info", "GET"),
            ("/v2/user/profile", "GET"),
            ("/v2/me", "GET"),
            ("/v2/profile", "GET"),
        ],
        
        "💰 SALDO Y CRÉDITOS": [
            ("/v2/account/balance", "GET"),
            ("/v2/account/credits", "GET"),
            ("/v2/balance", "GET"),
            ("/v2/credits", "GET"),
            ("/v2/user/balance", "GET"),
            ("/v2/user/credits", "GET"),
            ("/v2/wallet", "GET"),
            ("/v2/wallet/balance", "GET"),
        ],
        
        "📱 HISTORIAL DE SMS": [
            ("/v2/sms/history", "GET"),
            ("/v2/sms/sent", "GET"),
            ("/v2/sms/list", "GET"),
            ("/v2/messages", "GET"),
            ("/v2/messages/history", "GET"),
            ("/v2/messages/sent", "GET"),
            ("/v2/history", "GET"),
            ("/v2/history/sms", "GET"),
        ],
        
        "📈 ESTADÍSTICAS": [
            ("/v2/stats", "GET"),
            ("/v2/statistics", "GET"),
            ("/v2/sms/stats", "GET"),
            ("/v2/sms/statistics", "GET"),
            ("/v2/reports", "GET"),
            ("/v2/reports/sms", "GET"),
            ("/v2/analytics", "GET"),
        ],
        
        "📋 CAMPAÑAS": [
            ("/v2/campaigns", "GET"),
            ("/v2/campaigns/list", "GET"),
            ("/v2/sms/campaigns", "GET"),
            ("/v2/bulk", "GET"),
            ("/v2/bulk/list", "GET"),
        ],
        
        "📞 CONTACTOS": [
            ("/v2/contacts", "GET"),
            ("/v2/contacts/list", "GET"),
            ("/v2/phonebook", "GET"),
            ("/v2/groups", "GET"),
        ],
        
        "⚙️ CONFIGURACIÓN": [
            ("/v2/settings", "GET"),
            ("/v2/config", "GET"),
            ("/v2/account/settings", "GET"),
            ("/v2/sms/config", "GET"),
        ],
        
        "🔔 WEBHOOKS Y NOTIFICACIONES": [
            ("/v2/webhooks", "GET"),
            ("/v2/notifications", "GET"),
            ("/v2/callbacks", "GET"),
        ],
        
        "📄 PLANTILLAS": [
            ("/v2/templates", "GET"),
            ("/v2/sms/templates", "GET"),
            ("/v2/messages/templates", "GET"),
        ],
    }
    
    all_results = {}
    
    for category, endpoints in endpoints_categories.items():
        print(f"\n{category}")
        print("-" * 80)
        
        category_results = []
        
        for endpoint, method in endpoints:
            result = await test_endpoint(token, endpoint, method)
            
            if result["success"]:
                print(f"✅ {method:4} {endpoint}")
                category_results.append(result)
            else:
                status = result.get("status", "error")
                if status not in [404, 405]:  # No mostrar 404 y 405 para no saturar
                    print(f"❌ {method:4} {endpoint} - {status}")
        
        if category_results:
            all_results[category] = category_results
    
    # Mostrar resultados detallados
    print("\n" + "=" * 80)
    print("ENDPOINTS FUNCIONALES ENCONTRADOS")
    print("=" * 80)
    
    if all_results:
        for category, results in all_results.items():
            print(f"\n{category}")
            print("-" * 80)
            
            for result in results:
                print(f"\n📍 {result['method']} {result['endpoint']}")
                print(f"   Status: {result['status']}")
                
                if result['data']:
                    print(f"   Respuesta:")
                    # Limitar la salida para no saturar
                    data_str = json.dumps(result['data'], indent=4, ensure_ascii=False)
                    lines = data_str.split('\n')
                    if len(lines) > 20:
                        print('\n'.join(lines[:20]))
                        print(f"   ... ({len(lines) - 20} líneas más)")
                    else:
                        print(data_str)
    else:
        print("\n⚠️  No se encontraron endpoints adicionales disponibles")
        print("\nLa API de LIWA parece tener endpoints limitados o requiere")
        print("permisos especiales para acceder a información adicional.")
    
    # Resumen
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    
    total_found = sum(len(results) for results in all_results.values())
    print(f"\n✅ Endpoints funcionales encontrados: {total_found}")
    
    if total_found > 0:
        print("\n💡 Datos que puedes consultar:")
        for category in all_results.keys():
            print(f"   • {category}")
    else:
        print("\n💡 Endpoints conocidos que funcionan:")
        print("   • POST /v2/auth/login - Autenticación")
        print("   • POST /v2/sms/single - Envío individual")
        print("   • POST /v2/sms/multiple - Envío masivo")
        print("\n📚 Para más información:")
        print("   • Documentación: https://api.liwa.co/docs")
        print("   • Panel web: https://liwa.co/dashboard")
        print("   • Soporte: soporte@liwa.co")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
