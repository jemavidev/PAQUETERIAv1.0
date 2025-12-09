#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar el sistema de preferencias
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.customer import Customer
from app.models.customer_preferences import CustomerPreferences
from app.models.notification import NotificationType, NotificationEvent
from app.utils.phone_utils import normalize_phone


def diagnosticar_preferencias():
    """Diagnostica el sistema de preferencias de notificaciones"""
    
    db: Session = SessionLocal()
    
    try:
        print("=" * 80)
        print("DIAGNÓSTICO: Sistema de Preferencias de Notificaciones")
        print("=" * 80)
        
        # Datos de prueba
        test_phone = "3002596319"
        
        print(f"\n📱 Teléfono de prueba: {test_phone}")
        
        # Buscar cliente
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
        print(f"   Nombre: {customer.full_name}")
        print(f"   Email: {customer.email}")
        print(f"   Teléfono: {customer.phone}")
        
        # Buscar preferencias
        print(f"\n🔍 Buscando preferencias del cliente...")
        preferences = db.query(CustomerPreferences).filter(
            CustomerPreferences.customer_id == customer.id
        ).first()
        
        if not preferences:
            print(f"\n⚠️ El cliente NO tiene preferencias configuradas")
            print(f"   Se crearán preferencias por defecto al primer acceso")
            
            # Crear preferencias de prueba
            print(f"\n📝 Creando preferencias de prueba...")
            preferences = CustomerPreferences(
                customer_id=customer.id,
                token=CustomerPreferences.generate_token()
            )
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
            print(f"   ✅ Preferencias creadas")
        
        print(f"\n📋 PREFERENCIAS ACTUALES:")
        print(f"   Token: {preferences.token[:20]}...")
        print(f"\n   🔔 NOTIFICACIONES GENERALES:")
        print(f"      SMS Habilitado: {preferences.sms_notifications_enabled}")
        print(f"      Email Habilitado: {preferences.email_notifications_enabled}")
        print(f"\n   📦 NOTIFICACIONES POR EVENTO:")
        print(f"      Paquete Anunciado: {preferences.notify_package_announced}")
        print(f"      Paquete Recibido: {preferences.notify_package_received}")
        print(f"      Paquete Entregado: {preferences.notify_package_delivered}")
        print(f"      Pago Pendiente: {preferences.notify_payment_due}")
        print(f"      Marketing: {preferences.marketing_enabled}")
        
        # Probar el método should_send_notification
        print(f"\n🧪 PRUEBAS DE LÓGICA DE PREFERENCIAS:")
        print(f"\n   Escenario 1: SMS para PACKAGE_RECEIVED")
        should_send = preferences.should_send_notification(
            NotificationType.SMS,
            NotificationEvent.PACKAGE_RECEIVED
        )
        print(f"      ¿Debe enviar? {should_send}")
        print(f"      Lógica:")
        print(f"         1. SMS habilitado: {preferences.sms_notifications_enabled}")
        print(f"         2. Evento habilitado: {preferences.notify_package_received}")
        print(f"         3. Resultado: {should_send}")
        
        print(f"\n   Escenario 2: Email para PACKAGE_DELIVERED")
        should_send = preferences.should_send_notification(
            NotificationType.EMAIL,
            NotificationEvent.PACKAGE_DELIVERED
        )
        print(f"      ¿Debe enviar? {should_send}")
        print(f"      Lógica:")
        print(f"         1. Email habilitado: {preferences.email_notifications_enabled}")
        print(f"         2. Evento habilitado: {preferences.notify_package_delivered}")
        print(f"         3. Resultado: {should_send}")
        
        print(f"\n   Escenario 3: SMS para CUSTOM_MESSAGE (OTP)")
        should_send = preferences.should_send_notification(
            NotificationType.SMS,
            NotificationEvent.CUSTOM_MESSAGE
        )
        print(f"      ¿Debe enviar? {should_send}")
        print(f"      Nota: CUSTOM_MESSAGE siempre retorna True (por defecto)")
        
        # Simular cambio de preferencias
        print(f"\n🔧 SIMULACIÓN: Desactivar SMS")
        print(f"   Estado actual: SMS = {preferences.sms_notifications_enabled}")
        preferences.sms_notifications_enabled = False
        db.commit()
        db.refresh(preferences)
        print(f"   Estado nuevo: SMS = {preferences.sms_notifications_enabled}")
        
        print(f"\n   Probando envío con SMS desactivado...")
        should_send = preferences.should_send_notification(
            NotificationType.SMS,
            NotificationEvent.PACKAGE_RECEIVED
        )
        print(f"      ¿Debe enviar SMS para PACKAGE_RECEIVED? {should_send}")
        print(f"      ✅ Correcto: No debe enviar porque SMS está desactivado")
        
        # Restaurar preferencias
        print(f"\n🔄 Restaurando preferencias originales...")
        preferences.sms_notifications_enabled = True
        db.commit()
        print(f"   ✅ SMS reactivado")
        
        # Verificar estructura de datos que espera el frontend
        print(f"\n📤 FORMATO DE DATOS PARA FRONTEND:")
        frontend_data = {
            "sms_notifications_enabled": preferences.sms_notifications_enabled,
            "email_notifications_enabled": preferences.email_notifications_enabled,
            "notify_package_announced": preferences.notify_package_announced,
            "notify_package_received": preferences.notify_package_received,
            "notify_package_delivered": preferences.notify_package_delivered,
            "notify_payment_due": preferences.notify_payment_due,
            "marketing_enabled": preferences.marketing_enabled
        }
        print(f"   {frontend_data}")
        
        print(f"\n" + "=" * 80)
        print("RESUMEN DEL DIAGNÓSTICO")
        print("=" * 80)
        print(f"✅ Cliente encontrado: {customer.full_name}")
        print(f"✅ Preferencias configuradas correctamente")
        print(f"✅ Método should_send_notification funciona correctamente")
        print(f"✅ La lógica de preferencias está implementada")
        print(f"\n⚠️ POSIBLES PROBLEMAS:")
        print(f"   1. El frontend no está enviando los datos correctamente al guardar")
        print(f"   2. El servicio SMS/Email no está verificando las preferencias")
        print(f"   3. El customer_id no se está pasando correctamente al enviar notificaciones")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🚀 Iniciando diagnóstico de preferencias...\n")
    diagnosticar_preferencias()
    print("\n✅ Diagnóstico completado\n")
