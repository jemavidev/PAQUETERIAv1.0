#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar las plantillas SMS configuradas
"""

import sys
from pathlib import Path
import json

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate

def main():
    """Mostrar plantillas SMS"""
    
    print("=" * 80)
    print("PLANTILLAS SMS CONFIGURADAS - PAQUETEX EL CLUB")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        templates = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.is_active == True
        ).all()
        
        if not templates:
            print("\n⚠️  No hay plantillas SMS activas")
            return 1
        
        print(f"\n📋 Total de plantillas activas: {len(templates)}\n")
        
        for i, template in enumerate(templates, 1):
            print("=" * 80)
            print(f"PLANTILLA #{i}: {template.name}")
            print("=" * 80)
            
            print(f"\n📌 Información General:")
            print(f"   • ID de Plantilla: {template.template_id}")
            print(f"   • Evento: {template.event_type}")
            print(f"   • Idioma: {template.language}")
            print(f"   • Estado: {'✅ Activa' if template.is_active else '❌ Inactiva'}")
            print(f"   • Por defecto: {'Sí' if template.is_default else 'No'}")
            
            print(f"\n💬 Mensaje de la Plantilla:")
            print(f"   {template.message_template}")
            
            print(f"\n📝 Descripción:")
            print(f"   {template.description or 'Sin descripción'}")
            
            # Parsear variables disponibles
            try:
                variables = json.loads(template.available_variables) if template.available_variables else []
                print(f"\n🔧 Variables Disponibles ({len(variables)}):")
                for var in variables:
                    print(f"   • {{{var}}}")
            except:
                print(f"\n🔧 Variables Disponibles:")
                print(f"   {template.available_variables}")
            
            # Mostrar ejemplo con variables de muestra
            print(f"\n📤 Ejemplo de Mensaje Enviado:")
            example_message = template.message_template
            
            # Variables de ejemplo
            example_vars = {
                'guide_number': 'ABC123456',
                'consult_code': 'PAP20251126ABCD',
                'tracking_code': 'PAP20251126ABCD',
                'status_text': 'RECIBIDO en nuestras instalaciones',
                'customer_name': 'Juan Pérez',
                'tracking_url': 'https://paquetex.papyrus.com.co/search?auto_search=PAP20251126ABCD',
                'company_name': 'PAQUETEX EL CLUB',
                'company_phone': '3334004007',
                'amount': '5000',
                'due_date': '30/11/2025',
                'message': 'Su paquete está listo para recoger'
            }
            
            # Reemplazar variables en el mensaje
            for var, value in example_vars.items():
                example_message = example_message.replace(f'{{{var}}}', str(value))
            
            print(f"   \"{example_message}\"")
            print(f"\n   📏 Longitud: {len(example_message)} caracteres")
            
            # Advertencia si es muy largo
            if len(example_message) > 160:
                segments = (len(example_message) + 159) // 160
                print(f"   ⚠️  Mensaje largo: {segments} segmentos SMS (${segments * 0.50:.2f} COP)")
            else:
                print(f"   ✅ Mensaje corto: 1 segmento SMS ($0.50 COP)")
            
            print()
        
        print("=" * 80)
        print("✅ PLANTILLAS MOSTRADAS EXITOSAMENTE")
        print("=" * 80)
        
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
