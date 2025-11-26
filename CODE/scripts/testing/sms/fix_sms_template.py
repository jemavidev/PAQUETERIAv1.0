#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la plantilla SMS con el código de consulta
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate

def main():
    """Corregir plantilla SMS"""
    
    print("=" * 80)
    print("CORRECCIÓN DE PLANTILLA SMS")
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
        print(f'   "{template.message_template}"')
        print()
        
        # Nueva plantilla con código de consulta pero sin enlace
        new_template = "PAQUETEX: Su paquete con guia {guide_number} está {status_text}. Su codigo es {consult_code}"
        
        print(f"📋 Nueva Plantilla:")
        print(f'   "{new_template}"')
        print()
        
        # Mostrar ejemplos
        print("=" * 80)
        print("EJEMPLOS CON LA PLANTILLA CORREGIDA")
        print("=" * 80)
        
        guide_number = "ABC123456"
        consult_code = "AESH"
        
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
        respuesta = input("\n¿Desea aplicar esta corrección? (s/n): ")
        
        if respuesta.lower() != 's':
            print("\n❌ Corrección cancelada")
            return 0
        
        # Actualizar la plantilla
        template.message_template = new_template
        db.commit()
        
        print("\n✅ Plantilla corregida exitosamente")
        print()
        print("=" * 80)
        print("PLANTILLA ACTUALIZADA")
        print("=" * 80)
        print()
        print("✅ Incluye el número de guía del transportador: {guide_number}")
        print("✅ Incluye el código de consulta: {consult_code}")
        print("✅ NO incluye enlaces (removido {tracking_url})")
        print("✅ Mensajes cortos y directos")
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
