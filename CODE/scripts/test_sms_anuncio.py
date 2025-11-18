#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar específicamente el SMS de anuncios
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.announcement_new import PackageAnnouncementNew
from app.models.notification import NotificationEvent, NotificationPriority
from app.services.sms_service import SMSService
from app.schemas.notification import SMSByEventRequest


async def main():
    """Probar SMS de anuncio"""
    
    print("=" * 70)
    print("TEST SMS ANUNCIO - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Buscar un anuncio reciente
        announcement = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.is_processed == False
        ).first()
        
        if not announcement:
            print("❌ No se encontró ningún anuncio sin procesar")
            return
        
        print(f"\n📦 Anuncio encontrado:")
        print(f"   • ID: {announcement.id}")
        print(f"   • Guía: {announcement.guide_number}")
        print(f"   • Tracking: {announcement.tracking_code}")
        print(f"   • Cliente: {announcement.customer_name}")
        print(f"   • Teléfono: {announcement.customer_phone}")
        print(f"   • Procesado: {announcement.is_processed}")
        
        # Probar el servicio SMS paso a paso
        print(f"\n🔧 Probando servicio SMS para anuncio...")
        
        sms_service = SMSService()
        
        # 1. Probar obtener plantilla
        print(f"\n1️⃣ Obteniendo plantilla...")
        template = sms_service.get_template_by_event(db, NotificationEvent.PACKAGE_ANNOUNCED)
        if template:
            print(f"   ✅ Plantilla encontrada: {template.template_id}")
        else:
            print(f"   ❌ No se encontró plantilla")
            return
        
        # 2. Probar preparar variables
        print(f"\n2️⃣ Preparando variables...")
        try:
            variables = await sms_service._prepare_event_variables(
                db=db,
                event_type=NotificationEvent.PACKAGE_ANNOUNCED,
                package_id=None,
                customer_id=None,
                announcement_id=str(announcement.id),
                custom_variables={
                    "guide_number": announcement.guide_number,
                    "tracking_code": announcement.tracking_code,
                    "customer_name": announcement.customer_name
                }
            )
            print(f"   ✅ Variables preparadas:")
            for key, value in variables.items():
                print(f"      • {key}: {value}")
        except Exception as e:
            print(f"   ❌ Error preparando variables: {str(e)}")
            return
        
        # 3. Probar renderizar mensaje
        print(f"\n3️⃣ Renderizando mensaje...")
        try:
            message = template.render_message(variables)
            print(f"   ✅ Mensaje renderizado: {message}")
        except Exception as e:
            print(f"   ❌ Error renderizando mensaje: {str(e)}")
            return
        
        # 4. Probar obtener destinatario
        print(f"\n4️⃣ Obteniendo destinatario...")
        try:
            recipient = await sms_service._get_event_recipient(
                db=db,
                event_type=NotificationEvent.PACKAGE_ANNOUNCED,
                package_id=None,
                customer_id=None,
                announcement_id=str(announcement.id)
            )
            if recipient:
                print(f"   ✅ Destinatario encontrado: {recipient}")
            else:
                print(f"   ❌ No se pudo determinar destinatario")
                return
        except Exception as e:
            print(f"   ❌ Error obteniendo destinatario: {str(e)}")
            return
        
        # 5. Probar envío completo
        print(f"\n5️⃣ Probando envío completo...")
        try:
            event_request = SMSByEventRequest(
                event_type=NotificationEvent.PACKAGE_ANNOUNCED,
                package_id=None,
                customer_id=None,
                announcement_id=announcement.id,
                custom_variables={
                    "guide_number": announcement.guide_number,
                    "tracking_code": announcement.tracking_code,
                    "customer_name": announcement.customer_name
                },
                priority=NotificationPriority.ALTA,
                is_test=False
            )
            
            result = await sms_service.send_sms_by_event(db=db, event_request=event_request)
            
            print(f"   📋 Resultado del envío:")
            print(f"      • ID Notificación: {result.notification_id}")
            print(f"      • Estado: {result.status}")
            print(f"      • Mensaje: {result.message}")
            print(f"      • Costo: ${result.cost_cents / 100:.2f} COP")
            
            if result.status == "sent":
                print(f"\n✅ SMS DE ANUNCIO ENVIADO EXITOSAMENTE")
            else:
                print(f"\n❌ SMS DE ANUNCIO FALLÓ")
                
        except Exception as e:
            print(f"   ❌ Error enviando SMS: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"\n" + "=" * 70)
        print("TEST COMPLETADO")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())