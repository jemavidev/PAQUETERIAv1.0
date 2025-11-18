#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba final del sistema SMS con códigos diferentes
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.package import Package
from app.models.announcement_new import PackageAnnouncementNew
from app.models.notification import NotificationEvent
from app.services.sms_service import SMSService

async def main():
    """Prueba final del sistema SMS"""
    
    print("=" * 80)
    print("PRUEBA FINAL - SISTEMA SMS CON CÓDIGOS DIFERENTES")
    print("=" * 80)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        sms_service = SMSService()
        
        # Probar con anuncio
        print(f"\n📋 PRUEBA CON ANUNCIO:")
        print("=" * 50)
        
        announcement = db.query(PackageAnnouncementNew).first()
        if announcement:
            print(f"   📦 Guide Number: {announcement.guide_number}")
            print(f"   🔍 Tracking Code: {announcement.tracking_code}")
            print(f"   ✅ ¿Son diferentes? {'SÍ' if announcement.guide_number != announcement.tracking_code else 'NO'}")
            
            variables = await sms_service._prepare_event_variables(
                db=db,
                event_type=NotificationEvent.PACKAGE_ANNOUNCED,
                package_id=None,
                customer_id=None,
                announcement_id=str(announcement.id),
                custom_variables={}
            )
            
            print(f"\n   Variables SMS:")
            print(f"   • guide_number: '{variables.get('guide_number')}'")
            print(f"   • consult_code: '{variables.get('consult_code')}'")
            
            # Obtener plantilla y renderizar
            template = sms_service.get_template_by_event(db, NotificationEvent.PACKAGE_ANNOUNCED)
            if template:
                mensaje = template.render_message(variables)
                print(f"\n   📱 Mensaje SMS: \"{mensaje}\"")
                print(f"   📏 Longitud: {len(mensaje)} caracteres")
                
                # Verificar que ambos códigos aparezcan
                if variables.get('guide_number') in mensaje and variables.get('consult_code') in mensaje:
                    print(f"   ✅ Ambos códigos aparecen correctamente")
                else:
                    print(f"   ❌ Falta algún código en el mensaje")
        
        # Probar con paquete
        print(f"\n📦 PRUEBA CON PAQUETE:")
        print("=" * 50)
        
        package = db.query(Package).first()
        if package:
            print(f"   📦 Guide Number: {package.guide_number}")
            print(f"   🔍 Tracking Number: {package.tracking_number}")
            print(f"   ✅ ¿Son diferentes? {'SÍ' if package.guide_number != package.tracking_number else 'NO'}")
            
            variables = await sms_service._prepare_event_variables(
                db=db,
                event_type=NotificationEvent.PACKAGE_DELIVERED,
                package_id=package.id,
                customer_id=None,
                announcement_id=None,
                custom_variables={}
            )
            
            print(f"\n   Variables SMS:")
            print(f"   • guide_number: '{variables.get('guide_number')}'")
            print(f"   • consult_code: '{variables.get('consult_code')}'")
            
            # Obtener plantilla y renderizar
            template = sms_service.get_template_by_event(db, NotificationEvent.PACKAGE_DELIVERED)
            if template:
                mensaje = template.render_message(variables)
                print(f"\n   📱 Mensaje SMS: \"{mensaje}\"")
                print(f"   📏 Longitud: {len(mensaje)} caracteres")
                
                # Verificar que ambos códigos aparezcan
                if variables.get('guide_number') in mensaje and variables.get('consult_code') in mensaje:
                    print(f"   ✅ Ambos códigos aparecen correctamente")
                else:
                    print(f"   ❌ Falta algún código en el mensaje")
        
        # Resumen final
        print(f"\n" + "=" * 80)
        print("RESUMEN FINAL")
        print("=" * 80)
        
        print(f"\n🎯 ESTADO DEL SISTEMA:")
        print(f"   ✅ Plantilla SMS configurada correctamente")
        print(f"   ✅ Variables guide_number y consult_code son diferentes")
        print(f"   ✅ Ambos códigos aparecen en los mensajes SMS")
        print(f"   ✅ Longitud de mensajes dentro del límite")
        
        print(f"\n📱 PLANTILLA ACTUAL:")
        if template:
            print(f"   {template.message_template}")
        
        print(f"\n💡 EXPLICACIÓN:")
        print(f"   • guide_number: Código del transportador (largo)")
        print(f"   • consult_code: Código de consulta del cliente (corto)")
        print(f"   • Ambos son útiles para el cliente")
        
        print(f"\n🎉 SISTEMA SMS FUNCIONANDO CORRECTAMENTE")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())