#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para remover enlaces de las plantillas SMS
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate

def main():
    """Remover enlaces de las plantillas SMS"""
    
    print("=" * 80)
    print("VERIFICACIÓN Y LIMPIEZA DE PLANTILLAS SMS")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Obtener todas las plantillas activas
        templates = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.is_active == True
        ).all()
        
        print(f"\n📋 Revisando {len(templates)} plantillas...\n")
        
        updated_count = 0
        
        for template in templates:
            print(f"Plantilla: {template.name}")
            print(f"Mensaje actual: {template.message_template}")
            
            # Verificar si contiene {tracking_url}
            if "{tracking_url}" in template.message_template:
                print("   ⚠️  Contiene {tracking_url}")
                
                # Remover la parte del enlace
                # Buscar patrones comunes
                new_message = template.message_template
                
                # Remover variaciones comunes de enlaces
                patterns_to_remove = [
                    " Consulte en: {tracking_url}",
                    " Consulte con código {consult_code} en: {tracking_url}",
                    " Ver en: {tracking_url}",
                    " Link: {tracking_url}",
                    " URL: {tracking_url}",
                    ". {tracking_url}",
                    " {tracking_url}"
                ]
                
                for pattern in patterns_to_remove:
                    if pattern in new_message:
                        new_message = new_message.replace(pattern, "")
                
                # Si aún contiene tracking_url, removerlo de forma genérica
                if "{tracking_url}" in new_message:
                    # Buscar y remover desde donde aparece tracking_url hasta el final o punto
                    import re
                    new_message = re.sub(r'\s*[,.]?\s*\{tracking_url\}.*?(?=[.]|$)', '', new_message)
                
                print(f"   ✅ Nuevo mensaje: {new_message}")
                
                # Actualizar
                template.message_template = new_message
                updated_count += 1
            else:
                print("   ✅ No contiene enlaces")
            
            print()
        
        if updated_count > 0:
            respuesta = input(f"\n¿Desea guardar los cambios en {updated_count} plantilla(s)? (s/n): ")
            
            if respuesta.lower() == 's':
                db.commit()
                print(f"\n✅ {updated_count} plantilla(s) actualizada(s) exitosamente")
            else:
                db.rollback()
                print("\n❌ Cambios descartados")
        else:
            print("✅ No se encontraron enlaces en las plantillas")
        
        # Mostrar plantillas finales
        print("\n" + "=" * 80)
        print("PLANTILLAS FINALES")
        print("=" * 80)
        
        db.refresh_all()
        templates = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.is_active == True
        ).all()
        
        for template in templates:
            print(f"\n{template.name}:")
            print(f'   "{template.message_template}"')
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
