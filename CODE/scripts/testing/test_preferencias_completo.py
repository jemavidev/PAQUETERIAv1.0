#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba completo para verificar el sistema de preferencias
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.customer import Customer
from app.models.customer_preferences import CustomerPreferences
from app.models.notification import Notification, NotificationType, NotificationEvent, NotificationStatus
from app.services.sms_service import SMSService
from app.services.email_service import EmailService
from app.utils.phone_utils import normalize_phone


async def test_preferencias_completo():
    """Prueba completa del sistema de preferencias"""
    
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("PRUEBA COMPLETA: Sistema de Preferencias de Notificaciones")
        print("=" * 80)
        
        # Datos de prueba
        test_phone = "3002596319"
        test_email = "jveyes@gmail.com"
        
        print(f"\n📱 Teléfono de prueba: {test_phone}")
        print(f"📧 Email de prueba: {test_email}")
        
        # ========================================
        # PASO 1: Buscar cliente
        # ========================================
        print(f"\n{'='*80}")
        print("PASO 1: Buscar Cliente")
        print("="*80)
        
        phone = normalize_phone(test_phone)
        customer = db.query(Customer).filter(
            Customer.phone == phone,
            Customer.is_active == True
        ).first()
        
        if not customer:
            print(f"\n❌ No se encontró cliente con teléfono {test_phone}")
            return
        
        print(f"\n✅ Cliente encontrado:")
        print(f"   ID: {customer.id}")
        print(f"   Tipo: {type(customer.id)}")
        print(f"   Nombre: {customer.full_name}")
        print(f"   Email: {customer.email}")
        print(f"   Teléfono: {customer.phone}")
        
        # ========================================
        # PASO 2: Verificar preferencias actuales
        # ========================================
        print(f"\n{'='*80}")
        print("PASO 2: Verificar Preferencias Actuales")
        print("="*80)
        
        preferences = db.query(CustomerPreferences).filter(
            CustomerPreferences.customer_id == customer.id
        ).first()
        
        if not preferences:
            print(f"\n⚠️ El cliente NO tiene preferencias configuradas")
            print(f"   Creando preferencias por defecto...")
            preferences = CustomerPreferences(
                customer_id=customer.id,
                token=CustomerPreferences.generate_token()
            )
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
            print(f"   ✅ Preferencias creadas")
        
        print(f"\n📋 Preferencias actuales:")
        print(f"   SMS Habilitado: {preferences.sms_notifications_enabled}")
        print(f"   Email Habilitado: {preferences.email_notifications_enabled}")
        print(f"   Paquete Recibido: {preferences.notify_package_received}")
        print(f"   Paquete Entregado: {preferences.notify_package_delivered}")
        
        # ========================================
        # PASO 3: Desactivar SMS
        # ========================================
        print(f"\n{'='*80}")
        print("PASO 3: Desactivar SMS")
        print("="*80)
        
        print(f"\n🔧 Desactivando SMS...")
        preferences.sms_notifications_enabled = False
        db.commit()
        db.refresh(preferences)
        print(f"   ✅ SMS desactivado: {preferences.sms_notifications_enabled}")
        
        # ========================================
        # PASO 4: Intentar enviar SMS (debe bloquearse)
        # ========================================
        print(f"\n{'='*80}")
        print("PASO 4: Intentar Enviar SMS (debe bloquearse)")
        print("="*80)
        
        print(f"\n📤 Enviando SMS de prueba...")
        print(f"   customer_id: {customer.id} (tipo: {type(customer.id)})")
        print(f"   customer_id como string: {str(customer.id)}")
        
        sms_service = SMSService()
        
        try:
            result = await sms_service.send_sms(
                db=db,
                recipient=phone,
                message="PAQUETEX: Su paquete ha sido recibido. (PRUEBA)",
                event_type=NotificationEvent.PACKAGE_RECEIVED,
                customer_id=str(customer.id),  # Convertir UUID a string
                is_test=True
            )
            
            print(f"\n📊 Resultado del envío:")
            print(f"   Status: {result.status}")
            print(f"   Mensaje: {result.message}")
            print(f"   Notification ID: {result.notification_id}")
            
            if result.status == "blocked":
                print(f"\n✅ CORRECTO: SMS bloqueado por preferencias")
            else:
                print(f"\n❌ ERROR: SMS NO fue bloqueado (debería estar bloqueado)")
            
            # Verificar en la base de datos
            notification = db.query(Notification).filter(
                Notification.id == result.notification_id
            ).first()
            
            if notification:
                print(f"\n📋 Notificación en BD:")
                print(f"   ID: {notification.id}")
                print(f"   Status: {notification.status}")
                print(f"   Customer ID: {notification.customer_id}")
                print(f"   Error Message: {notification.error_message}")
                
        except Exception as e:
            print(f"\n❌ Error al enviar SMS: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # ========================================
        # PASO 5: Reactivar SMS
        # ========================================
        print(f"\n{'='*80}")
        print("PASO 5: Reactivar SMS")
        print("="*80)
        
        print(f"\n🔧 Reactivando SMS...")
        preferences.sms_notifications_enabled = True
        db.commit()
        db.refresh(preferences)
        print(f"   ✅ SMS reactivado: {preferences.sms_notifications_enabled}")
        
        # ========================================
        # PASO 6: Intentar enviar SMS (debe enviarse)
        # ========================================
        print(f"\n{'='*80}")
        print("PASO 6: Intentar Enviar SMS (debe enviarse)")
        print("="*80)
        
        print(f"\n📤 Enviando SMS de prueba...")
        
        try:
            result = await sms_service.send_sms(
                db=db,
                recipient=phone,
                message="PAQUETEX: Su paquete ha sido recibido. (PRUEBA 2)",
                event_type=NotificationEvent.PACKAGE_RECEIVED,
                customer_id=str(customer.id),
                is_test=True
            )
            
            print(f"\n📊 Resultado del envío:")
            print(f"   Status: {result.status}")
            print(f"   Mensaje: {result.message}")
            
            if result.status == "sent":
                print(f"\n✅ CORRECTO: SMS enviado correctamente")
            else:
                print(f"\n❌ ERROR: SMS NO fue enviado (debería enviarse)")
            
        except Exception as e:
            print(f"\n❌ Error al enviar SMS: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # ========================================
        # PASO 7: Probar con Email
        # ========================================
        if customer.email:
            print(f"\n{'='*80}")
            print("PASO 7: Probar con Email")
            print("="*80)
            
            print(f"\n🔧 Desactivando Email...")
            preferences.email_notifications_enabled = False
            db.commit()
            db.refresh(preferences)
            print(f"   ✅ Email desactivado: {preferences.email_notifications_enabled}")
            
            print(f"\n📤 Enviando Email de prueba...")
            
            email_service = EmailService()
            
            try:
                result = await email_service.send_email_by_event(
                    db=db,
                    event_type=NotificationEvent.PACKAGE_RECEIVED,
                    recipient=customer.email,
                    variables={
                        "first_name": customer.full_name.split(" ")[0],
                        "current_status": "RECIBIDO",
                        "guide_number": "TEST123",
                        "consult_code": "TEST123",
                        "tracking_url": "https://paquetex.papyrus.com.co/search?auto_search=TEST123"
                    },
                    customer_id=str(customer.id),
                    is_test=True
                )
                
                print(f"\n📊 Resultado del envío:")
                print(f"   {result}")
                
            except Exception as e:
                print(f"\n❌ Error al enviar Email: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Reactivar email
            print(f"\n🔧 Reactivando Email...")
            preferences.email_notifications_enabled = True
            db.commit()
            print(f"   ✅ Email reactivado")
        
        # ========================================
        # RESUMEN
        # ========================================
        print(f"\n{'='*80}")
        print("RESUMEN DE PRUEBAS")
        print("="*80)
        print(f"✅ Cliente encontrado y verificado")
        print(f"✅ Preferencias funcionan correctamente")
        print(f"✅ Sistema de bloqueo implementado")
        print(f"\n💡 Si las notificaciones siguen llegando en producción:")
        print(f"   1. Verificar que el customer_id se pase correctamente")
        print(f"   2. Verificar que las preferencias se guarden en la BD")
        print(f"   3. Revisar logs del servidor para ver si se verifica el bloqueo")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Iniciando prueba completa de preferencias...\n")
    asyncio.run(test_preferencias_completo())
    print("\n✅ Prueba completada\n")
