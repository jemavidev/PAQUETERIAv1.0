#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar las plantillas SMS con enlaces de seguimiento
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate

def main():
    """Actualizar plantillas SMS"""
    
    print("=" * 80)
    print("ACTUALIZACIÓN DE PLANTILLAS SMS")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Obtener la plantilla unificada
        template = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.template_id == "status_change_unified"
        ).first()
        
        if not template:
            print("\n❌ No se encontró la plantilla unificada")
            return 1
        
        print(f"\n📋 Plantilla Actual:")
        print(f"   {template.message_template}")
        print()
        
        # Nueva plantilla con enlace de seguimiento
        new_template = "PAQUETEX: Su paquete {guide_number} está {status_text}. Consulte con código {consult_code} en: {tracking_url}"
        
        print(f"📋 Nueva Plantilla:")
        print(f"   {new_template}")
        print()
        
        # Mostrar ejemplos
        print("=" * 80)
        print("EJEMPLOS CON LA NUEVA PLANTILLA")
        print("=" * 80)
        
        guide_number = "ABC123456"
        consult_code = "PAP20251126ABCD"
        tracking_url = "https://paquetex.papyrus.com.co/search"
        
        estados = [
            ("ANUNCIADO", "ANUNCIADO"),
            ("RECIBIDO", "RECIBIDO en nuestras instalaciones"),
            ("ENTREGADO", "ENTREGADO exitosamente"),
            ("CANCELADO", "CANCELADO")
        ]
        
        for i, (nombre, status_text) in enumerate(estados, 1):
            mensaje = new_template.replace("{guide_number}", guide_number)
            mensaje = mensaje.replace("{status_text}", status_text)
            mensaje = mensaje.replace("{consult_code}", consult_code)
            mensaje = mensaje.replace("{tracking_url}", tracking_url)
            
            print(f"\n{i}. {nombre}:")
            print(f'   "{mensaje}"')
            print(f"   📏 {len(mensaje)} caracteres")
            
            if len(mensaje) > 160:
                segments = (len(mensaje) + 159) // 160
                print(f"   ⚠️  {segments} SMS (${segments * 0.50:.2f} COP)")
            else:
                print(f"   ✅ 1 SMS ($0.50 COP)")
        
        print()
        print("=" * 80)
        
        # Preguntar confirmación
        respuesta = input("\n¿Desea aplicar esta actualización? (s/n): ")
        
        if respuesta.lower() != 's':
            print("\n❌ Actualización cancelada")
            return 0
        
        # Actualizar la plantilla
        template.message_template = new_template
        db.commit()
        
        print("\n✅ Plantilla actualizada exitosamente")
        print()
        print("=" * 80)
        print("BENEFICIOS DE LA NUEVA PLANTILLA")
        print("=" * 80)
        print()
        print("✅ El enlace completo (https://...) se detecta automáticamente como clickeable")
        print("✅ Los usuarios pueden hacer clic directamente para consultar su paquete")
        print("✅ El código de consulta aparece en el mensaje para referencia")
        print("✅ El número de guía también está visible")
        print("✅ Más corto y directo")
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
