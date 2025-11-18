#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la plantilla SMS y hacerla más corta
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate


def main():
    """Corregir plantilla SMS"""
    
    print("=" * 70)
    print("CORRECCIÓN DE PLANTILLA SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Buscar la plantilla unificada
        template = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.template_id == "status_change_unified"
        ).first()
        
        if template:
            print(f"\n📱 Plantilla actual:")
            print(f"   • Mensaje: {template.message_template}")
            print(f"   • Longitud: {len(template.message_template)} caracteres")
            
            # Nueva plantilla más corta
            new_template = "PAQUETES: Su paquete {guide_number} está {status_text}. Código: {consult_code}"
            
            print(f"\n📱 Nueva plantilla:")
            print(f"   • Mensaje: {new_template}")
            print(f"   • Longitud: {len(new_template)} caracteres")
            
            # Actualizar plantilla
            template.message_template = new_template
            db.commit()
            
            print(f"\n✅ Plantilla actualizada exitosamente")
            
            # Probar renderizar con datos de ejemplo
            variables = {
                "guide_number": "LTEM",
                "status_text": "ENTREGADO exitosamente",
                "consult_code": "LTEM"
            }
            
            rendered = template.render_message(variables)
            print(f"\n📋 Mensaje renderizado de ejemplo:")
            print(f"   • Mensaje: {rendered}")
            print(f"   • Longitud: {len(rendered)} caracteres")
            
        else:
            print(f"\n❌ No se encontró la plantilla status_change_unified")
        
        print(f"\n" + "=" * 70)
        print("CORRECCIÓN COMPLETADA")
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