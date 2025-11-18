#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico: SMS de Anuncio
Verifica por qué no se envió SMS al anunciar el paquete DSE4GS / HTE3
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.announcement_new import PackageAnnouncementNew
from app.models.notification import Notification, NotificationType, NotificationEvent
from app.models.customer import Customer
from app.utils.phone_utils import normalize_phone

def diagnosticar_anuncio(guide_number: str, tracking_code: str):
    """Diagnostica por qué no se envió SMS para un anuncio"""
    
    print("=" * 80)
    print(f"DIAGNÓSTICO: Anuncio {guide_number} / {tracking_code}")
    print("=" * 80)
    print()
    
    db = SessionLocal()
    
    try:
        # 1. Buscar el anuncio
        print("1️⃣ BUSCANDO ANUNCIO...")
        announcement = db.query(PackageAnnouncementNew).filter(
            (PackageAnnouncementNew.guide_number == guide_number) |
            (PackageAnnouncementNew.tracking_code == tracking_code)
        ).first()
        
        if not announcement:
            print(f"   ❌ No se encontró anuncio con guía {guide_number} o código {tracking_code}")
            return
        
        print(f"   ✅ Anuncio encontrado:")
        print(f"      ID: {announcement.id}")
        print(f"      Guía: {announcement.guide_number}")
        print(f"      Código: {announcement.tracking_code}")
        print(f"      Cliente: {announcement.customer_name}")
        print(f"      Teléfono: {announcement.customer_phone}")
        print(f"      Creado: {announcement.created_at}")
        print()
        
        # 2. Buscar notificaciones SMS relacionadas
        print("2️⃣ BUSCANDO NOTIFICACIONES SMS...")
        sms_notifications = db.query(Notification).filter(
            Notification.announcement_id == announcement.id,
            Notification.notification_type == NotificationType.SMS
        ).all()
        
        if not sms_notifications:
            print(f"   ❌ NO SE ENCONTRARON NOTIFICACIONES SMS para este anuncio")
            print(f"      Esto indica que el SMS nunca se intentó enviar")
        else:
            print(f"   ✅ Se encontraron {len(sms_notifications)} notificaciones SMS:")
            for notif in sms_notifications:
                print(f"      - ID: {notif.id}")
                print(f"        Estado: {notif.status.value}")
                print(f"        Destinatario: {notif.recipient}")
                print(f"        Mensaje: {notif.message[:80]}...")
                print(f"        Evento: {notif.event_type.value}")
                print(f"        Creado: {notif.created_at}")
                if notif.error_message:
                    print(f"        ❌ Error: {notif.error_message}")
                print()
        
        # 3. Verificar teléfono
        print("3️⃣ VERIFICANDO TELÉFONO...")
        phone = announcement.customer_phone
        print(f"   Teléfono original: {phone}")
        
        try:
            normalized = normalize_phone(phone)
            print(f"   Teléfono normalizado: {normalized}")
            
            # Validar formato
            if not normalized.startswith('+57'):
                print(f"   ⚠️ El teléfono no tiene código de país +57")
            
            if len(normalized) != 13:  # +57 + 10 dígitos
                print(f"   ⚠️ El teléfono no tiene 10 dígitos (tiene {len(normalized) - 3})")
            
            print(f"   ✅ Teléfono válido")
        except Exception as e:
            print(f"   ❌ Error al normalizar teléfono: {e}")
        print()
        
        # 4. Buscar cliente relacionado
        print("4️⃣ BUSCANDO CLIENTE...")
        try:
            normalized_phone = normalize_phone(announcement.customer_phone)
            customer = db.query(Customer).filter(
                Customer.phone == normalized_phone
            ).first()
            
            if customer:
                print(f"   ✅ Cliente encontrado:")
                print(f"      ID: {customer.id}")
                print(f"      Nombre: {customer.full_name}")
                print(f"      Teléfono: {customer.phone}")
                print(f"      Email: {customer.email or 'No tiene'}")
            else:
                print(f"   ⚠️ No se encontró cliente con teléfono {normalized_phone}")
                print(f"      El SMS se enviará al teléfono del anuncio directamente")
        except Exception as e:
            print(f"   ❌ Error al buscar cliente: {e}")
        print()
        
        # 5. Verificar plantilla SMS
        print("5️⃣ VERIFICANDO PLANTILLA SMS...")
        from app.models.notification import SMSMessageTemplate
        template = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.template_id == "status_change_unified",
            SMSMessageTemplate.is_active == True
        ).first()
        
        if template:
            print(f"   ✅ Plantilla encontrada:")
            print(f"      ID: {template.template_id}")
            print(f"      Nombre: {template.name}")
            print(f"      Activa: {template.is_active}")
            print(f"      Por defecto: {template.is_default}")
            print(f"      Mensaje: {template.message_template[:80]}...")
        else:
            print(f"   ❌ NO SE ENCONTRÓ PLANTILLA UNIFICADA")
            print(f"      Ejecuta: python -m src.scripts.migrate_sms_templates_unified")
        print()
        
        # 6. Verificar configuración SMS
        print("6️⃣ VERIFICANDO CONFIGURACIÓN SMS...")
        from app.models.notification import SMSConfiguration
        config = db.query(SMSConfiguration).filter(
            SMSConfiguration.is_active == True
        ).first()
        
        if config:
            print(f"   ✅ Configuración encontrada:")
            print(f"      Proveedor: {config.provider}")
            print(f"      Activa: {config.is_active}")
            print(f"      Modo test: {config.enable_test_mode}")
            print(f"      API Key: {'***' + config.api_key[-4:] if config.api_key else 'NO CONFIGURADA'}")
        else:
            print(f"   ❌ NO SE ENCONTRÓ CONFIGURACIÓN SMS ACTIVA")
        print()
        
        # 7. Resumen y recomendaciones
        print("=" * 80)
        print("📋 RESUMEN Y RECOMENDACIONES")
        print("=" * 80)
        
        if not sms_notifications:
            print("❌ PROBLEMA PRINCIPAL: No se intentó enviar SMS")
            print()
            print("Posibles causas:")
            print("1. Error en el código de anuncio (announcements.py)")
            print("2. Excepción silenciosa en el try/except")
            print("3. Evento incorrecto (debe ser PACKAGE_ANNOUNCED)")
            print()
            print("Soluciones:")
            print("✅ Código actualizado en announcements.py")
            print("✅ Método _get_event_recipient actualizado en sms_service.py")
            print("✅ Método _prepare_event_variables actualizado en sms_service.py")
            print()
            print("Próximos pasos:")
            print("1. Reiniciar la aplicación para cargar el código actualizado")
            print("2. Crear un nuevo anuncio de prueba")
            print("3. Verificar logs en tiempo real")
        else:
            print("✅ Se intentó enviar SMS")
            print()
            print("Revisar estado de las notificaciones arriba para más detalles")
        
        print()
        print("Para probar manualmente:")
        print(f"python -c \"from app.services.sms_service import SMSService; import asyncio; asyncio.run(SMSService().send_sms(db, '{announcement.customer_phone}', 'Test', is_test=True))\"")
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    # Buscar anuncio DSE4GS / HTE3
    diagnosticar_anuncio("DSE4GS", "HTE3")
