#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico SMS
Verifica configuración y envío de SMS
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.sms_service import SMSService
from app.models.customer import Customer
from app.config import settings

async def test_sms_config():
    """Verificar configuración SMS"""
    print("\n" + "="*70)
    print("  DIAGNÓSTICO DE CONFIGURACIÓN SMS")
    print("="*70)
    
    print(f"\n📋 Configuración SMS:")
    print(f"   SMS_API_URL: {settings.sms_api_url if hasattr(settings, 'sms_api_url') else 'NO CONFIGURADO'}")
    print(f"   SMS_API_KEY: {'***' + settings.sms_api_key[-4:] if hasattr(settings, 'sms_api_key') and settings.sms_api_key else 'NO CONFIGURADO'}")
    print(f"   SMS_SENDER: {settings.sms_sender if hasattr(settings, 'sms_sender') else 'NO CONFIGURADO'}")
    
    if not hasattr(settings, 'sms_api_url') or not settings.sms_api_url:
        print("\n❌ ERROR: SMS_API_URL no está configurado")
        return False
    
    if not hasattr(settings, 'sms_api_key') or not settings.sms_api_key:
        print("\n❌ ERROR: SMS_API_KEY no está configurado")
        return False
    
    print("\n✅ Configuración SMS parece correcta")
    return True

async def test_sms_send():
    """Probar envío de SMS"""
    print("\n" + "="*70)
    print("  PRUEBA DE ENVÍO SMS")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Buscar cliente de prueba
        phone = "3002596319"
        customer = db.query(Customer).filter(
            Customer.phone == phone,
            Customer.is_active == True
        ).first()
        
        if not customer:
            print(f"\n❌ Cliente con teléfono {phone} no encontrado")
            return False
        
        print(f"\n✅ Cliente encontrado: {customer.full_name}")
        print(f"   ID: {customer.id}")
        print(f"   Teléfono: {customer.phone}")
        print(f"   Email: {customer.email}")
        
        # Intentar enviar SMS
        print(f"\n📱 Intentando enviar SMS de prueba...")
        
        sms_service = SMSService()
        message = "PAQUETEX: Mensaje de prueba del sistema. Código: 123456"
        
        try:
            result = await sms_service.send_sms(
                db=db,
                recipient=phone,
                message=message,
                event_type="CUSTOM_MESSAGE",
                customer_id=str(customer.id),
                is_test=True  # Modo prueba
            )
            
            print(f"\n✅ SMS enviado exitosamente")
            print(f"   Resultado: {result}")
            return True
            
        except Exception as e:
            print(f"\n❌ Error al enviar SMS: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    finally:
        db.close()

async def main():
    print("\n" + "🔍"*35)
    print("  DIAGNÓSTICO COMPLETO DEL SISTEMA SMS")
    print("🔍"*35)
    
    # Paso 1: Verificar configuración
    config_ok = await test_sms_config()
    
    if not config_ok:
        print("\n❌ DIAGNÓSTICO FALLIDO: Configuración incorrecta")
        return
    
    # Paso 2: Probar envío
    send_ok = await test_sms_send()
    
    if not send_ok:
        print("\n❌ DIAGNÓSTICO FALLIDO: No se pudo enviar SMS")
        return
    
    print("\n" + "="*70)
    print("✅ DIAGNÓSTICO COMPLETADO: Sistema SMS funcional")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnóstico cancelado")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
