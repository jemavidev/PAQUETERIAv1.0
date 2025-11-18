#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ver las plantillas SMS actuales
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate


def main():
    """Ver plantillas SMS"""
    
    print("=" * 70)
    print("PLANTILLAS SMS ACTUALES - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        templates = db.query(SMSMessageTemplate).all()
        
        if not templates:
            print(f"\n❌ No se encontraron plantillas")
            return
        
        for i, template in enumerate(templates, 1):
            print(f"\n📱 {i}. Plantilla: {template.template_id}")
            print(f"   • Nombre: {template.name}")
            print(f"   • Evento: {template.event_type.value}")
            print(f"   • Activa: {'✅ Sí' if template.is_active else '❌ No'}")
            print(f"   • Mensaje: {template.message_template}")
            print(f"   • Longitud: {len(template.message_template)} caracteres")
            
            if template.available_variables:
                import json
                try:
                    variables = json.loads(template.available_variables)
                    print(f"   • Variables disponibles: {', '.join(['{' + var + '}' for var in variables])}")
                except:
                    print(f"   • Variables: {template.available_variables}")
        
        print(f"\n" + "=" * 70)
        print("INFORMACIÓN SOBRE PLANTILLAS")
        print("=" * 70)
        
        print(f"\n📝 Variables más comunes:")
        print(f"   • {{guide_number}} - Número de guía del paquete")
        print(f"   • {{status_text}} - Estado del paquete (ANUNCIADO, RECIBIDO, etc.)")
        print(f"   • {{consult_code}} - Código de consulta")
        print(f"   • {{customer_name}} - Nombre del cliente")
        print(f"   • {{tracking_url}} - URL de seguimiento")
        print(f"   • {{company_name}} - Nombre de la empresa")
        print(f"   • {{company_phone}} - Teléfono de la empresa")
        
        print(f"\n💡 Ejemplos de mensajes:")
        print(f"   • Corto: PAQUETES: Su paquete {{guide_number}} está {{status_text}}. Código: {{consult_code}}")
        print(f"   • Con URL: PAQUETES: Su paquete {{guide_number}} está {{status_text}}. Ver: {{tracking_url}}")
        print(f"   • Personalizado: {{customer_name}}, su paquete {{guide_number}} está {{status_text}}")
        
        print(f"\n⚠️  Recomendaciones:")
        print(f"   • Máximo 160 caracteres para evitar división en múltiples SMS")
        print(f"   • Usar variables para personalizar mensajes")
        print(f"   • Incluir información esencial: número de guía y estado")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()