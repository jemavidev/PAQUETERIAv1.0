#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar cómo se ve una plantilla SMS con datos reales
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate


def main():
    """Probar plantilla SMS"""
    
    print("=" * 70)
    print("PROBAR PLANTILLA SMS - PAQUETEX EL CLUB")
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
        
        print(f"\n📱 Plantilla actual: {template.name}")
        print(f"   • Mensaje: {template.message_template}")
        print(f"   • Longitud: {len(template.message_template)} caracteres")
        
        # Diferentes escenarios de prueba
        escenarios = [
            {
                "nombre": "ANUNCIO",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "ANUNCIADO",
                    "consult_code": "XYZ9",
                    "customer_name": "MARÍA GONZÁLEZ",
                    "tracking_url": "https://paquetex.papyrus.com.co/search?auto_search=XYZ9",
                    "company_name": "PAQUETEX EL CLUB",
                    "company_phone": "3334004007"
                }
            },
            {
                "nombre": "RECIBIDO",
                "variables": {
                    "guide_number": "DEF789012",
                    "status_text": "RECIBIDO en nuestras instalaciones",
                    "consult_code": "ABC5",
                    "customer_name": "CARLOS RODRÍGUEZ",
                    "tracking_url": "https://paquetex.papyrus.com.co/search/seguimiento/DEF789012",
                    "company_name": "PAQUETEX EL CLUB",
                    "company_phone": "3334004007"
                }
            },
            {
                "nombre": "ENTREGADO",
                "variables": {
                    "guide_number": "GHI345678",
                    "status_text": "ENTREGADO exitosamente",
                    "consult_code": "DEF2",
                    "customer_name": "ANA MARTÍNEZ",
                    "tracking_url": "https://paquetex.papyrus.com.co/search/seguimiento/GHI345678",
                    "company_name": "PAQUETEX EL CLUB",
                    "company_phone": "3334004007"
                }
            },
            {
                "nombre": "CANCELADO",
                "variables": {
                    "guide_number": "JKL901234",
                    "status_text": "CANCELADO",
                    "consult_code": "GHI8",
                    "customer_name": "LUIS HERNÁNDEZ",
                    "tracking_url": "https://paquetex.papyrus.com.co/search/seguimiento/JKL901234",
                    "company_name": "PAQUETEX EL CLUB",
                    "company_phone": "3334004007"
                }
            }
        ]
        
        print(f"\n📋 VISTA PREVIA EN DIFERENTES ESCENARIOS:")
        print("=" * 70)
        
        for escenario in escenarios:
            try:
                mensaje_renderizado = template.render_message(escenario["variables"])
                print(f"\n📱 {escenario['nombre']}:")
                print(f"   📱 {mensaje_renderizado}")
                print(f"   📏 Longitud: {len(mensaje_renderizado)} caracteres")
                
                if len(mensaje_renderizado) > 160:
                    print(f"   ⚠️  ADVERTENCIA: Muy largo (se dividirá en múltiples SMS)")
                else:
                    print(f"   ✅ Longitud adecuada")
                    
            except Exception as e:
                print(f"\n❌ Error renderizando {escenario['nombre']}: {str(e)}")
        
        print(f"\n" + "=" * 70)
        print("INFORMACIÓN ADICIONAL")
        print("=" * 70)
        
        print(f"\n💰 Costos de SMS:")
        print(f"   • 1-160 caracteres: 1 SMS = $0.50 COP")
        print(f"   • 161-320 caracteres: 2 SMS = $1.00 COP")
        print(f"   • 321-480 caracteres: 3 SMS = $1.50 COP")
        
        print(f"\n📝 Variables disponibles en la plantilla:")
        if template.available_variables:
            import json
            try:
                variables = json.loads(template.available_variables)
                for var in variables:
                    print(f"   • {{{var}}}")
            except:
                print(f"   • {template.available_variables}")
        
        print(f"\n💡 Para modificar la plantilla, ejecute:")
        print(f"   python3 scripts/modificar_plantilla_sms.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()