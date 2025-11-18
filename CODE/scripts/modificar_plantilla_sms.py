#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para modificar una plantilla SMS específica
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate


def main():
    """Modificar plantilla SMS"""
    
    print("=" * 70)
    print("MODIFICAR PLANTILLA SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Buscar la plantilla unificada (la más importante)
        template = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.template_id == "status_change_unified"
        ).first()
        
        if not template:
            print(f"\n❌ No se encontró la plantilla unificada")
            return
        
        print(f"\n📱 Plantilla actual: {template.name}")
        print(f"   • Evento: {template.event_type.value}")
        print(f"   • Mensaje actual: {template.message_template}")
        print(f"   • Longitud actual: {len(template.message_template)} caracteres")
        
        print(f"\n📝 Variables disponibles:")
        print(f"   • {{guide_number}} - Número de guía (ej: ABC123)")
        print(f"   • {{status_text}} - Estado (ANUNCIADO, RECIBIDO, ENTREGADO, CANCELADO)")
        print(f"   • {{consult_code}} - Código de consulta (ej: XYZ9)")
        print(f"   • {{customer_name}} - Nombre del cliente")
        print(f"   • {{tracking_url}} - URL de seguimiento")
        print(f"   • {{company_name}} - PAQUETEX EL CLUB")
        print(f"   • {{company_phone}} - 3334004007")
        
        print(f"\n💡 Ejemplos de plantillas:")
        print(f"   1. Actual: {template.message_template}")
        print(f"   2. Con nombre: {{customer_name}}, su paquete {{guide_number}} está {{status_text}}")
        print(f"   3. Con URL: PAQUETES: Su paquete {{guide_number}} está {{status_text}}. Ver: {{tracking_url}}")
        print(f"   4. Completa: Hola {{customer_name}}, su paquete {{guide_number}} está {{status_text}}. Código: {{consult_code}}")
        print(f"   5. Simple: Paquete {{guide_number}}: {{status_text}}")
        
        print(f"\n⚠️  Recomendación: Máximo 160 caracteres para evitar división del SMS")
        
        nuevo_mensaje = input(f"\nIngrese el nuevo mensaje (Enter para cancelar): ").strip()
        
        if not nuevo_mensaje:
            print(f"\n❌ Operación cancelada")
            return
        
        print(f"\n📋 Nuevo mensaje: {nuevo_mensaje}")
        print(f"📏 Longitud: {len(nuevo_mensaje)} caracteres")
        
        if len(nuevo_mensaje) > 160:
            print(f"⚠️  ADVERTENCIA: El mensaje es muy largo ({len(nuevo_mensaje)} caracteres)")
            print(f"   Esto puede dividirse en múltiples SMS y aumentar el costo")
            confirmar = input(f"¿Continuar de todas formas? (s/n): ").lower()
            if confirmar != 's':
                print(f"\n❌ Operación cancelada")
                return
        
        # Probar renderizado con datos de ejemplo
        variables_ejemplo = {
            "guide_number": "ABC123",
            "status_text": "ENTREGADO exitosamente",
            "consult_code": "XYZ9",
            "customer_name": "JUAN PÉREZ",
            "tracking_url": "https://paquetex.papyrus.com.co/search?auto_search=XYZ9",
            "company_name": "PAQUETEX EL CLUB",
            "company_phone": "3334004007"
        }
        
        try:
            # Crear plantilla temporal para probar
            template_temp = SMSMessageTemplate(
                template_id="temp",
                name="temp",
                message_template=nuevo_mensaje,
                event_type=template.event_type
            )
            
            mensaje_renderizado = template_temp.render_message(variables_ejemplo)
            print(f"\n✅ Vista previa del mensaje renderizado:")
            print(f"   📱 {mensaje_renderizado}")
            print(f"   📏 Longitud renderizada: {len(mensaje_renderizado)} caracteres")
            
        except Exception as e:
            print(f"\n❌ Error en la plantilla: {str(e)}")
            print(f"   Verifique que las variables estén escritas correctamente")
            return
        
        confirmar_final = input(f"\n¿Confirmar cambio de plantilla? (s/n): ").lower()
        if confirmar_final != 's':
            print(f"\n❌ Operación cancelada")
            return
        
        # Actualizar plantilla
        template.message_template = nuevo_mensaje
        db.commit()
        
        print(f"\n✅ PLANTILLA ACTUALIZADA EXITOSAMENTE")
        print(f"   • Nueva plantilla: {template.message_template}")
        print(f"   • Nueva longitud: {len(template.message_template)} caracteres")
        print(f"\n🎉 Los próximos SMS usarán la nueva plantilla automáticamente")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()