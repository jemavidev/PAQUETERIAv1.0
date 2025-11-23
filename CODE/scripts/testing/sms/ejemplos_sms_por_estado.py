#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar ejemplos específicos de SMS por cada estado de paquete
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate


def main():
    """Mostrar ejemplos de SMS por estado"""
    
    print("=" * 80)
    print("EJEMPLOS DE SMS POR ESTADO DE PAQUETE - PAQUETEX EL CLUB")
    print("=" * 80)
    
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
        
        print(f"\n📱 PLANTILLA ACTUAL:")
        print(f"   {template.message_template}")
        print(f"   Longitud: {len(template.message_template)} caracteres")
        
        # Ejemplos por cada estado
        estados = [
            {
                "estado": "📦 ANUNCIADO",
                "descripcion": "Cuando el cliente anuncia un paquete",
                "cuando": "Al crear un anuncio desde la web",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "ANUNCIADO",
                    "consult_code": "XYZ9"
                }
            },
            {
                "estado": "📥 RECIBIDO",
                "descripcion": "Cuando el paquete llega a las instalaciones",
                "cuando": "Al cambiar estado de ANUNCIADO → RECIBIDO",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "RECIBIDO en nuestras instalaciones",
                    "consult_code": "XYZ9"
                }
            },
            {
                "estado": "✅ ENTREGADO",
                "descripcion": "Cuando se entrega el paquete al cliente",
                "cuando": "Al cambiar estado de RECIBIDO → ENTREGADO",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "ENTREGADO exitosamente",
                    "consult_code": "XYZ9"
                }
            },
            {
                "estado": "❌ CANCELADO",
                "descripcion": "Cuando se cancela un paquete",
                "cuando": "Al cambiar estado a CANCELADO",
                "variables": {
                    "guide_number": "ABC123456",
                    "status_text": "CANCELADO",
                    "consult_code": "XYZ9"
                }
            }
        ]
        
        print(f"\n🎯 EJEMPLOS DE SMS POR ESTADO:")
        print("=" * 80)
        
        for estado in estados:
            print(f"\n{estado['estado']}")
            print(f"📋 {estado['descripcion']}")
            print(f"⏰ Cuándo se envía: {estado['cuando']}")
            
            try:
                mensaje = template.render_message(estado["variables"])
                print(f"📱 SMS que recibe el cliente:")
                print(f"   \"{mensaje}\"")
                print(f"📏 Longitud: {len(mensaje)} caracteres")
                
                if len(mensaje) > 160:
                    print(f"⚠️  Se dividirá en múltiples SMS")
                else:
                    print(f"✅ SMS único - $0.50 COP")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            print("-" * 60)
        
        # Otros tipos de SMS
        print(f"\n🔔 OTROS TIPOS DE SMS:")
        print("=" * 80)
        
        otros_sms = [
            {
                "tipo": "💰 RECORDATORIO DE PAGO",
                "ejemplo": "PAQUETES: Tiene un pago pendiente de $15000 COP para el paquete ABC123456. Realice el pago para continuar con la entrega.",
                "cuando": "Cuando hay pagos pendientes"
            },
            {
                "tipo": "📝 MENSAJE PERSONALIZADO",
                "ejemplo": "PAQUETES: Su paquete está listo para recoger en nuestras oficinas",
                "cuando": "Mensajes administrativos manuales"
            }
        ]
        
        for sms in otros_sms:
            print(f"\n{sms['tipo']}")
            print(f"📱 Ejemplo: \"{sms['ejemplo']}\"")
            print(f"⏰ Cuándo: {sms['cuando']}")
            print(f"📏 Longitud: {len(sms['ejemplo'])} caracteres")
        
        print(f"\n" + "=" * 80)
        print("INFORMACIÓN TÉCNICA")
        print("=" * 80)
        
        print(f"\n🔧 CONFIGURACIÓN ACTUAL:")
        print(f"• Plantilla principal: {template.name}")
        print(f"• ID: {template.template_id}")
        print(f"• Activa: {'✅ Sí' if template.is_active else '❌ No'}")
        print(f"• Mensaje base: {template.message_template}")
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"• Longitud plantilla: {len(template.message_template)} caracteres")
        print(f"• Variables usadas: 3 (guide_number, status_text, consult_code)")
        print(f"• Costo por SMS: $0.50 COP")
        print(f"• Proveedor: LIWA.co")
        
        print(f"\n🎨 PERSONALIZACIÓN:")
        print(f"• Para modificar: python3 scripts/modificar_plantilla_sms.py")
        print(f"• Variables disponibles: guide_number, status_text, consult_code, customer_name, tracking_url")
        print(f"• Recomendación: Máximo 160 caracteres")
        
        print(f"\n🚀 FLUJO AUTOMÁTICO:")
        print(f"1. Cliente anuncia → SMS automático")
        print(f"2. Operador recibe → SMS automático")
        print(f"3. Operador entrega → SMS automático")
        print(f"4. Si cancela → SMS automático")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()