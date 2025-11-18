#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las plantillas SMS en la base de datos
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate, NotificationEvent
from app.services.sms_service import SMSService


def main():
    """Verificar plantillas SMS"""
    
    print("=" * 70)
    print("VERIFICACIÓN DE PLANTILLAS SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Verificar plantillas existentes
        templates = db.query(SMSMessageTemplate).all()
        
        print(f"\n📋 Plantillas encontradas: {len(templates)}")
        
        if templates:
            for template in templates:
                print(f"\n📱 Plantilla: {template.template_id}")
                print(f"   • Nombre: {template.name}")
                print(f"   • Evento: {template.event_type.value}")
                print(f"   • Activa: {template.is_active}")
                print(f"   • Mensaje: {template.message_template}")
        else:
            print(f"\n❌ No se encontraron plantillas SMS")
            print(f"🔧 Creando plantillas por defecto...")
            
            # Crear plantillas por defecto
            sms_service = SMSService()
            created_templates = sms_service.create_default_templates(db)
            
            print(f"✅ Creadas {len(created_templates)} plantillas por defecto")
            
            for template in created_templates:
                print(f"\n📱 Plantilla creada: {template.template_id}")
                print(f"   • Nombre: {template.name}")
                print(f"   • Evento: {template.event_type.value}")
                print(f"   • Mensaje: {template.message_template}")
        
        # Probar obtener plantilla específica para PACKAGE_DELIVERED
        print(f"\n🔍 Probando obtener plantilla para PACKAGE_DELIVERED...")
        sms_service = SMSService()
        template = sms_service.get_template_by_event(db, NotificationEvent.PACKAGE_DELIVERED)
        
        if template:
            print(f"✅ Plantilla encontrada: {template.template_id}")
            print(f"   • Mensaje: {template.message_template}")
            
            # Probar renderizar mensaje
            variables = {
                "guide_number": "TEST123",
                "status_text": "ENTREGADO exitosamente",
                "consult_code": "TEST123",
                "tracking_url": "https://paquetex.papyrus.com.co/search?auto_search=TEST123"
            }
            
            try:
                rendered_message = template.render_message(variables)
                print(f"✅ Mensaje renderizado: {rendered_message}")
            except Exception as e:
                print(f"❌ Error renderizando mensaje: {str(e)}")
        else:
            print(f"❌ No se encontró plantilla para PACKAGE_DELIVERED")
        
        print(f"\n" + "=" * 70)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()