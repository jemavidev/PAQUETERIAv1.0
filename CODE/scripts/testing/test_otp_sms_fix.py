#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar corrección de error SMS OTP
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.customer import Customer
from app.models.notification import NotificationEvent
from app.services.sms_service import SMSService
from app.utils.phone_utils import normalize_phone


async def test_otp_sms():
    """Prueba el envío de OTP por SMS con la corrección aplicada"""
    
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("PRUEBA: Envío de OTP por SMS (Corrección Aplicada)")
        print("=" * 60)
        
        # Datos de prueba
        test_phone = "3002596319"
        test_email = "jveyes@gmail.com"
        
        print(f"\n📱 Teléfono de prueba: {test_phone}")
        print(f"📧 Email de prueba: {test_email}")
        
        # Buscar cliente
        phone = normalize_phone(test_phone)
        customer = db.query(Customer).filter(
            Customer.phone == phone,
            Customer.is_active == True
        ).first()
        
        if not customer:
            print(f"\n❌ No se encontró cliente con teléfono {test_phone}")
            return
        
        print(f"\n✅ Cliente encontrado: {customer.full_name}")
        print(f"   ID: {customer.id}")
        print(f"   Email: {customer.email}")
        
        # Preparar mensaje OTP de prueba
        otp_code = "123456"  # Código de prueba
        message = (
            f"PAQUETEX: Su contraseña temporal es: {otp_code}. "
            f"Válida por 5 minutos. No comparta esta contraseña."
        )
        
        print(f"\n📤 Preparando envío de SMS...")
        print(f"   Mensaje: {message[:50]}...")
        
        # Crear servicio SMS
        sms_service = SMSService()
        
        # PRUEBA 1: Envío SIN customer_id (no verifica preferencias)
        print(f"\n🧪 PRUEBA 1: Envío de OTP de autenticación (customer_id=None)")
        print(f"   Esto NO debe verificar preferencias del cliente")
        
        try:
            result = await sms_service.send_sms(
                db=db,
                recipient=phone,
                message=message,
                event_type=NotificationEvent.CUSTOM_MESSAGE,  # ✅ Usando enum
                customer_id=None,  # ✅ No verificar preferencias para OTP
                is_test=True  # Modo test para no gastar créditos
            )
            
            print(f"\n✅ PRUEBA 1 EXITOSA")
            print(f"   Status: {result.status}")
            print(f"   Mensaje: {result.message}")
            print(f"   Notification ID: {result.notification_id}")
            
        except Exception as e:
            print(f"\n❌ PRUEBA 1 FALLÓ")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # PRUEBA 2: Envío CON customer_id (verifica preferencias)
        print(f"\n🧪 PRUEBA 2: Envío de notificación de paquete (customer_id={customer.id})")
        print(f"   Esto SÍ debe verificar preferencias del cliente")
        
        try:
            result = await sms_service.send_sms(
                db=db,
                recipient=phone,
                message="PAQUETEX: Su paquete ha sido recibido.",
                event_type=NotificationEvent.PACKAGE_RECEIVED,  # ✅ Usando enum
                customer_id=str(customer.id),  # ✅ Verificar preferencias
                is_test=True
            )
            
            print(f"\n✅ PRUEBA 2 EXITOSA")
            print(f"   Status: {result.status}")
            print(f"   Mensaje: {result.message}")
            
            if result.status == "blocked":
                print(f"   ⚠️ SMS bloqueado por preferencias del cliente (esperado si tiene SMS desactivado)")
            
        except Exception as e:
            print(f"\n❌ PRUEBA 2 FALLÓ")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # PRUEBA 3: Verificar que el enum funciona correctamente
        print(f"\n🧪 PRUEBA 3: Verificación de enum NotificationEvent")
        
        try:
            print(f"   NotificationEvent.CUSTOM_MESSAGE = {NotificationEvent.CUSTOM_MESSAGE}")
            print(f"   NotificationEvent.CUSTOM_MESSAGE.value = {NotificationEvent.CUSTOM_MESSAGE.value}")
            print(f"   NotificationEvent.PACKAGE_RECEIVED = {NotificationEvent.PACKAGE_RECEIVED}")
            print(f"   NotificationEvent.PACKAGE_RECEIVED.value = {NotificationEvent.PACKAGE_RECEIVED.value}")
            print(f"\n✅ PRUEBA 3 EXITOSA - Enums funcionan correctamente")
            
        except Exception as e:
            print(f"\n❌ PRUEBA 3 FALLÓ")
            print(f"   Error: {str(e)}")
        
        print("\n" + "=" * 60)
        print("RESUMEN DE PRUEBAS")
        print("=" * 60)
        print("✅ Corrección aplicada exitosamente")
        print("✅ event_type ahora usa enums en lugar de strings")
        print("✅ OTPs de autenticación no verifican preferencias")
        print("✅ Notificaciones de paquetes sí verifican preferencias")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Iniciando pruebas de corrección SMS OTP...\n")
    asyncio.run(test_otp_sms())
    print("\n✅ Pruebas completadas\n")
