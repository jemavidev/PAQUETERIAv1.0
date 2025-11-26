#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar ejemplos reales de SMS para cada estado de paquete
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate

def main():
    """Mostrar ejemplos de SMS para cada estado"""
    
    print("=" * 80)
    print("EJEMPLOS DE SMS POR ESTADO DE PAQUETE")
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
        
        print(f"\n📋 Plantilla Base:")
        print(f"   {template.message_template}")
        print()
        
        # Datos de ejemplo
        guide_number = "ABC123456"
        consult_code = "PAP20251126ABCD"
        
        # Definir los 4 estados con sus textos
        estados = [
            {
                "nombre": "ANUNCIADO",
                "status_text": "ANUNCIADO",
                "descripcion": "Cuando el cliente anuncia que le llegará un paquete"
            },
            {
                "nombre": "RECIBIDO",
                "status_text": "RECIBIDO en nuestras instalaciones",
                "descripcion": "Cuando el paquete llega a PAQUETEX"
            },
            {
                "nombre": "ENTREGADO",
                "status_text": "ENTREGADO exitosamente",
                "descripcion": "Cuando el paquete es entregado al cliente"
            },
            {
                "nombre": "CANCELADO",
                "status_text": "CANCELADO",
                "descripcion": "Cuando el paquete es cancelado"
            }
        ]
        
        print("=" * 80)
        print("EJEMPLOS DE MENSAJES SMS")
        print("=" * 80)
        
        for i, estado in enumerate(estados, 1):
            print(f"\n{i}. ESTADO: {estado['nombre']}")
            print(f"   Descripción: {estado['descripcion']}")
            print()
            
            # Generar el mensaje
            mensaje = template.message_template.replace("{guide_number}", guide_number)
            mensaje = mensaje.replace("{status_text}", estado['status_text'])
            mensaje = mensaje.replace("{consult_code}", consult_code)
            
            print(f'   "{mensaje}"')
            print()
            print(f"   📏 Longitud: {len(mensaje)} caracteres")
            
            if len(mensaje) > 160:
                segments = (len(mensaje) + 159) // 160
                print(f"   ⚠️  {segments} segmentos SMS (${segments * 0.50:.2f} COP)")
            else:
                print(f"   ✅ 1 segmento SMS ($0.50 COP)")
            
            print()
            print("-" * 80)
        
        print()
        print("=" * 80)
        print("NOTAS IMPORTANTES")
        print("=" * 80)
        print()
        print("• Los mensajes se envían automáticamente cuando cambia el estado del paquete")
        print("• El {guide_number} es el número de guía del transportador (ej: ABC123456)")
        print("• El {consult_code} es el código único de consulta (ej: PAP20251126ABCD)")
        print("• El {status_text} cambia automáticamente según el estado")
        print("• Cada SMS cuesta $0.50 COP")
        print("• Los mensajes de más de 160 caracteres se dividen en múltiples SMS")
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
