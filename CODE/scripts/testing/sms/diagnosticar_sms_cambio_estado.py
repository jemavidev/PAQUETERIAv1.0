#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar específicamente el problema del SMS en cambio de estado
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.package import Package, PackageStatus
from app.models.notification import NotificationEvent, NotificationPriority
from app.services.sms_service import SMSService
from app.schemas.notification import SMSByEventRequest


async def main():
    """Diagnosticar problema específico del SMS"""
    
    print("=" * 70)
    print("DIAGNÓSTICO SMS CAMBIO DE ESTADO - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Buscar un paquete entregado para probar
        package = db.query(Package).filter(
            Package.status == PackageStatus.ENTREGADO
        ).first()
        
        if not package:
            print("❌ No se encontró ningún paquete entregado para probar")
            return
        
        print(f"\n📦 Paquete de prueba:")
        print(f"   • ID: {package.id}")
        print(f"   • Tracking: {package.tracking_number}")
        print(f"   • Estado: {package.status.value}")
        print(f"   • Cliente ID: {package.customer_id}")
        
        # Cargar cliente explícitamente
        if package.customer_id:
            from app.models.customer import Customer
            customer = db.query(Customer).filter(Customer.id == package.customer_id).first()
            if customer:
                print(f"   • Cliente: {customer.full_name}")
                print(f"   • Email: {getattr(customer, 'email', 'NO TIENE')}")
                print(f"   • Teléfono: {getattr(customer, 'phone', 'NO TIENE')}")
            else:
                print(f"   • Cliente: NO ENCONTRADO EN BD")
        else:
            print(f"   • Cliente: NO TIENE customer_id")
        
        # Probar el servicio SMS paso a paso
        print(f"\n🔧 Probando servicio SMS paso a paso...")
        
        sms_service = SMSService()
        
        # 1. Probar obtener plantilla
        print(f"\n1️⃣ Obteniendo plantilla...")
        template = sms_service.get_template_by_event(db, NotificationEvent.PACKAGE_DELIVERED)
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
                event_type=NotificationEvent.PACKAGE_DELIVERED,
                package_id=package.id,
                customer_id=str(package.customer_id) if package.customer_id else None,
                announcement_id=None,
                custom_variables={}
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
                event_type=NotificationEvent.PACKAGE_DELIVERED,
                package_id=package.id,
                customer_id=str(package.customer_id) if package.customer_id else None,
                announcement_id=None
            )
            if recipient:
                print(f"   ✅ Destinatario encontrado: {recipient}")
            else:
                print(f"   ❌ No se pudo determinar destinatario")
                return
        except Exception as e:
            print(f"   ❌ Error obteniendo destinatario: {str(e)}")
            return
        
        # 5. Probar envío completo usando send_sms_by_event
        print(f"\n5️⃣ Probando envío completo...")
        respuesta = input(f"¿Desea enviar SMS real al {recipient}? (s/n): ")
        
        if respuesta.lower() == 's':
            try:
                event_request = SMSByEventRequest(
                    event_type=NotificationEvent.PACKAGE_DELIVERED,
                    package_id=package.id,
                    customer_id=package.customer_id,
                    custom_variables={},
                    priority=NotificationPriority.MEDIA,
                    is_test=False
                )
                
                result = await sms_service.send_sms_by_event(db=db, event_request=event_request)
                
                print(f"   ✅ SMS enviado exitosamente:")
                print(f"      • ID Notificación: {result.notification_id}")
                print(f"      • Estado: {result.status}")
                print(f"      • Mensaje: {result.message}")
                print(f"      • Costo: ${result.cost_cents / 100:.2f} COP")
                
            except Exception as e:
                print(f"   ❌ Error enviando SMS: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ℹ️ Envío cancelado por el usuario")
        
        print(f"\n" + "=" * 70)
        print("DIAGNÓSTICO COMPLETADO")
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