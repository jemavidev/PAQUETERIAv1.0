#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la plantilla SMS con el nuevo formato
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate


def main():
    """Actualizar plantilla SMS"""
    
    print("=" * 70)
    print("ACTUALIZAR PLANTILLA SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Buscar la plantilla unificada
        template = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.template_id == "status_change_unified"
        ).first()
        
        if not template:
            print(f"\n❌ No se encontró la plantilla unificada")
            return
        
        # Plantilla actual y nueva
        plantilla_actual = template.message_template
        plantilla_nueva = "PAQUETEX: Su paquete con guia {guide_number} esta {status_text}. Codigo {consult_code}"
        
        print(f"\n📱 CAMBIO DE PLANTILLA:")
        print(f"   Actual:  {plantilla_actual}")
        print(f"   Nueva:   {plantilla_nueva}")
        
        print(f"\n📏 LONGITUDES:")
        print(f"   Actual:  {len(plantilla_actual)} caracteres")
        print(f"   Nueva:   {len(plantilla_nueva)} caracteres")
        
        # Probar con ejemplos
        ejemplos = [
            {
                "estado": "ANUNCIADO",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "ANUNCIADO",
                    "consult_code": "XYZ9"
                }
            },
            {
                "estado": "RECIBIDO",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "RECIBIDO en nuestras instalaciones",
                    "consult_code": "XYZ9"
                }
            },
            {
                "estado": "ENTREGADO",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "ENTREGADO exitosamente",
                    "consult_code": "XYZ9"
                }
            },
            {
                "estado": "CANCELADO",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "CANCELADO",
                    "consult_code": "XYZ9"
                }
            }
        ]
        
        print(f"\n📋 VISTA PREVIA DE LOS NUEVOS MENSAJES:")
        print("=" * 70)
        
        # Crear plantilla temporal para probar
        template_temp = SMSMessageTemplate(
            template_id="temp",
            name="temp",
            message_template=plantilla_nueva,
            event_type=template.event_type
        )
        
        for ejemplo in ejemplos:
            try:
                mensaje_actual = template.render_message(ejemplo["variables"])
                mensaje_nuevo = template_temp.render_message(ejemplo["variables"])
                
                print(f"\n📦 {ejemplo['estado']}:")
                print(f"   Actual: {mensaje_actual}")
                print(f"   Nuevo:  {mensaje_nuevo}")
                print(f"   Longitud nueva: {len(mensaje_nuevo)} caracteres")
                
                if len(mensaje_nuevo) > 160:
                    print(f"   ⚠️  ADVERTENCIA: Muy largo")
                else:
                    print(f"   ✅ Longitud adecuada")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        # Confirmar cambio
        print(f"\n" + "=" * 70)
        confirmar = input(f"¿Confirmar actualización de la plantilla? (s/n): ").lower()
        
        if confirmar != 's':
            print(f"\n❌ Operación cancelada")
            return
        
        # Actualizar plantilla
        template.message_template = plantilla_nueva
        db.commit()
        
        print(f"\n✅ PLANTILLA ACTUALIZADA EXITOSAMENTE")
        print(f"   Nueva plantilla: {template.message_template}")
        print(f"   Longitud: {len(template.message_template)} caracteres")
        print(f"\n🎉 Los próximos SMS usarán el nuevo formato automáticamente")
        
        # Mostrar ejemplo final
        ejemplo_final = template.render_message({
            "guide_number": "TEST123",
            "status_text": "ENTREGADO exitosamente",
            "consult_code": "ABC5"
        })
        
        print(f"\n📱 EJEMPLO DE SMS CON NUEVA PLANTILLA:")
        print(f"   \"{ejemplo_final}\"")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()