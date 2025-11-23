#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico detallado del sistema SMS
"""

import asyncio
import sys
from pathlib import Path
import httpx

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.sms_service import SMSService
from app.config import settings


async def test_liwa_authentication():
    """Probar autenticación con LIWA.co"""
    print("\n" + "=" * 70)
    print("PRUEBA 1: AUTENTICACIÓN CON LIWA.CO")
    print("=" * 70)
    
    print(f"\n🔑 Credenciales:")
    print(f"   • Cuenta: {settings.liwa_account}")
    print(f"   • API Key: {'*' * 20}{settings.liwa_api_key[-10:] if settings.liwa_api_key else 'NO CONFIGURADA'}")
    print(f"   • URL Auth: {settings.liwa_auth_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "account": settings.liwa_account,
                "password": settings.liwa_password
            }
            
            print(f"\n📤 Enviando request de autenticación...")
            response = await client.post(settings.liwa_auth_url, json=payload)
            
            print(f"📥 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta exitosa")
                print(f"   • Respuesta completa: {data}")
                print(f"   • Success: {data.get('success')}")
                
                if data.get("token"):
                    token = data["token"]
                    print(f"   • Token: {token[:20]}...{token[-10:]}")
                    print(f"   • Token length: {len(token)}")
                    return True, token
                else:
                    print(f"   • Mensaje: {data.get('message', 'Sin mensaje')}")
                    return False, None
            else:
                print(f"❌ Error HTTP {response.status_code}")
                print(f"   • Respuesta: {response.text}")
                return False, None
                
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_sms_send(token: str, test_phone: str = "3002596319"):
    """Probar envío de SMS con token"""
    api_url = "https://api.liwa.co/v2/sms/single"
    
    # Asegurar que el número tenga código de país
    phone_number = test_phone
    if not phone_number.startswith("57"):
        phone_number = f"57{phone_number}"
    
    payload = {
        "number": phone_number,
        "message": "Mensaje de prueba desde PAQUETEX EL CLUB - Sistema funcionando!",
        "type": 1
    }
    
    print(f"\n📤 Enviando SMS...")
    print(f"   • URL: {api_url}")
    print(f"   • Número: {payload['number']}")
    print(f"   • Mensaje: {payload['message']}")
    print(f"   • Type: {payload['type']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "API-KEY": settings.liwa_api_key,
                "Content-Type": "application/json"
            }
            
            print(f"   • Headers: Authorization Bearer + API-KEY")
            
            response = await client.post(api_url, json=payload, headers=headers)
            
            print(f"\n📥 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta exitosa")
                print(f"   • Success: {data.get('success')}")
                print(f"   • Message ID: {data.get('menssageId', 'N/A')}")
                print(f"   • Mensaje: {data.get('message', 'N/A')}")
                print(f"   • Número: {data.get('number', 'N/A')}")
                return True
            else:
                print(f"❌ Error HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   • Error: {error_data}")
                except:
                    print(f"   • Respuesta: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_service_configuration():
    """Probar configuración del servicio"""
    print("\n" + "=" * 70)
    print("PRUEBA 3: CONFIGURACIÓN DEL SERVICIO")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        sms_service = SMSService()
        config = sms_service.get_sms_config(db)
        
        print(f"\n🔧 Configuración en BD:")
        print(f"   • Proveedor: {config.provider}")
        print(f"   • Cuenta: {config.account_id}")
        print(f"   • API Key: {'Configurada' if config.api_key else 'NO configurada'}")
        print(f"   • Password: {'Configurado' if config.password else 'NO configurado'}")
        print(f"   • URL Auth: {config.auth_url}")
        print(f"   • URL API: {config.api_url}")
        print(f"   • Remitente: {config.default_sender}")
        print(f"   • Modo prueba: {config.enable_test_mode}")
        print(f"   • Activo: {config.is_active}")
        
        # Verificar que coincida con .env
        print(f"\n🔍 Comparación con .env:")
        print(f"   • Cuenta coincide: {config.account_id == settings.liwa_account}")
        print(f"   • API Key coincide: {config.api_key == settings.liwa_api_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def test_database_connection():
    """Probar conexión a base de datos"""
    print("\n" + "=" * 70)
    print("PRUEBA 4: CONEXIÓN A BASE DE DATOS")
    print("=" * 70)
    
    try:
        db = SessionLocal()
        
        # Probar query simple
        from app.models.notification import Notification
        count = db.query(Notification).count()
        
        print(f"✅ Conexión exitosa")
        print(f"   • Total notificaciones: {count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecutar todas las pruebas"""
    import sys
    
    # Números de prueba
    test_phones = ["3044000678", "3002596319", "3008103849"]
    
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO COMPLETO DEL SISTEMA SMS")
    print("=" * 70)
    print(f"📱 Números de prueba: {', '.join(test_phones)}")
    print("=" * 70)
    
    results = {}
    
    # Prueba 1: Base de datos
    results['database'] = await test_database_connection()
    
    # Prueba 2: Configuración del servicio
    results['service_config'] = await test_service_configuration()
    
    # Prueba 3: Autenticación LIWA
    auth_success, token = await test_liwa_authentication()
    results['authentication'] = auth_success
    
    # Prueba 4: Envío de SMS a múltiples números
    if auth_success and token:
        print("\n" + "=" * 70)
        print("PRUEBA 2: ENVÍO DE SMS A MÚLTIPLES NÚMEROS")
        print("=" * 70)
        
        sms_results = []
        for i, phone in enumerate(test_phones, 1):
            print(f"\n📱 Enviando a número {i}/{len(test_phones)}: {phone}")
            result = await test_sms_send(token, phone)
            sms_results.append({"phone": phone, "success": result})
        
        # Resumen de envíos
        print("\n" + "=" * 70)
        print("RESUMEN DE ENVÍOS")
        print("=" * 70)
        for res in sms_results:
            status = "✅ EXITOSO" if res["success"] else "❌ FALLÓ"
            print(f"{status} - {res['phone']}")
        
        results['sms_send'] = any(r["success"] for r in sms_results)
    else:
        results['sms_send'] = False
        print("\n⚠️  Saltando prueba de envío (autenticación falló)")
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE DIAGNÓSTICO")
    print("=" * 70)
    
    for test_name, success in results.items():
        status = "✅ OK" if success else "❌ FALLÓ"
        print(f"{status:10} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("El sistema está listo para enviar SMS")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("Revisa los errores arriba para más detalles")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
