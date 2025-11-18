#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar todos los tipos de SMS posibles del sistema
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate, NotificationEvent


def main():
    """Mostrar todos los SMS posibles"""
    
    print("=" * 80)
    print("TODOS LOS MENSAJES SMS POSIBLES - PAQUETEX EL CLUB")
    print("=" * 80)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Obtener todas las plantillas
        templates = db.query(SMSMessageTemplate).all()
        
        if not templates:
            print(f"\n❌ No se encontraron plantillas")
            return
        
        # Definir todos los escenarios posibles
        escenarios = {
            NotificationEvent.PACKAGE_ANNOUNCED: {
                "nombre": "📦 ANUNCIO DE PAQUETE",
                "descripcion": "Cuando se anuncia un nuevo paquete",
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
            NotificationEvent.PACKAGE_RECEIVED: {
                "nombre": "📥 PAQUETE RECIBIDO",
                "descripcion": "Cuando el paquete llega a las instalaciones",
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
            NotificationEvent.PACKAGE_DELIVERED: {
                "nombre": "✅ PAQUETE ENTREGADO",
                "descripcion": "Cuando el paquete se entrega al cliente",
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
            NotificationEvent.PACKAGE_CANCELLED: {
                "nombre": "❌ PAQUETE CANCELADO",
                "descripcion": "Cuando se cancela un paquete",
                "variables": {
                    "guide_number": "JKL901234",
                    "status_text": "CANCELADO",
                    "consult_code": "GHI8",
                    "customer_name": "LUIS HERNÁNDEZ",
                    "tracking_url": "https://paquetex.papyrus.com.co/search/seguimiento/JKL901234",
                    "company_name": "PAQUETEX EL CLUB",
                    "company_phone": "3334004007"
                }
            },
            NotificationEvent.PAYMENT_DUE: {
                "nombre": "💰 RECORDATORIO DE PAGO",
                "descripcion": "Cuando hay un pago pendiente",
                "variables": {
                    "guide_number": "MNO567890",
                    "consult_code": "JKL3",
                    "amount": "15000",
                    "due_date": "25/11/2025",
                    "customer_name": "SOFÍA LÓPEZ",
                    "company_phone": "3334004007"
                }
            },
            NotificationEvent.CUSTOM_MESSAGE: {
                "nombre": "📝 MENSAJE PERSONALIZADO",
                "descripcion": "Mensajes administrativos personalizados",
                "variables": {
                    "message": "Su paquete está listo para recoger en nuestras oficinas",
                    "customer_name": "PEDRO JIMÉNEZ",
                    "company_phone": "3334004007"
                }
            }
        }
        
        print(f"\n🎯 TIPOS DE SMS AUTOMÁTICOS DEL SISTEMA:")
        print("=" * 80)
        
        # Procesar cada plantilla
        for template in templates:
            if template.event_type in escenarios:
                escenario = escenarios[template.event_type]
                
                print(f"\n{escenario['nombre']}")
                print(f"📋 {escenario['descripcion']}")
                print(f"🔧 Plantilla: {template.name} ({template.template_id})")
                print(f"📝 Código plantilla: {template.message_template}")
                
                try:
                    mensaje_renderizado = template.render_message(escenario["variables"])
                    print(f"📱 MENSAJE FINAL: {mensaje_renderizado}")
                    print(f"📏 Longitud: {len(mensaje_renderizado)} caracteres")
                    
                    if len(mensaje_renderizado) > 160:
                        print(f"⚠️  ADVERTENCIA: Muy largo (se dividirá en múltiples SMS)")
                        costo = ((len(mensaje_renderizado) - 1) // 160 + 1) * 0.5
                        print(f"💰 Costo estimado: ${costo:.2f} COP")
                    else:
                        print(f"✅ Longitud adecuada - Costo: $0.50 COP")
                        
                except Exception as e:
                    print(f"❌ Error renderizando: {str(e)}")
                
                print("-" * 80)
        
        # Mostrar información adicional
        print(f"\n📊 RESUMEN DEL SISTEMA:")
        print("=" * 80)
        
        print(f"\n🔄 FLUJO AUTOMÁTICO DE SMS:")
        print(f"1. Cliente anuncia paquete → SMS: 'Su paquete ABC123 está ANUNCIADO'")
        print(f"2. Paquete llega → SMS: 'Su paquete ABC123 está RECIBIDO en nuestras instalaciones'")
        print(f"3. Paquete se entrega → SMS: 'Su paquete ABC123 está ENTREGADO exitosamente'")
        print(f"4. Si se cancela → SMS: 'Su paquete ABC123 está CANCELADO'")
        
        print(f"\n💰 COSTOS POR SMS:")
        print(f"• 1-160 caracteres: 1 SMS = $0.50 COP")
        print(f"• 161-320 caracteres: 2 SMS = $1.00 COP")
        print(f"• 321-480 caracteres: 3 SMS = $1.50 COP")
        
        print(f"\n📱 NÚMEROS DE DESTINO:")
        print(f"• Se envían automáticamente al teléfono registrado del cliente")
        print(f"• Formato aceptado: +573001234567 o 3001234567")
        print(f"• Solo números colombianos (prefijo 57)")
        
        print(f"\n🎛️ CONFIGURACIÓN ACTUAL:")
        print(f"• Proveedor: LIWA.co")
        print(f"• Cuenta: 00486396309")
        print(f"• Remitente: PAQUETEX EL CLUB")
        print(f"• Estado: ✅ Operacional")
        
        print(f"\n📝 VARIABLES DISPONIBLES:")
        print(f"• {{guide_number}} - Número de guía del paquete")
        print(f"• {{status_text}} - Estado actual (ANUNCIADO, RECIBIDO, etc.)")
        print(f"• {{consult_code}} - Código de consulta público")
        print(f"• {{customer_name}} - Nombre del cliente")
        print(f"• {{tracking_url}} - URL de seguimiento")
        print(f"• {{company_name}} - PAQUETEX EL CLUB")
        print(f"• {{company_phone}} - 3334004007")
        print(f"• {{amount}} - Monto (para pagos)")
        print(f"• {{due_date}} - Fecha límite (para pagos)")
        print(f"• {{message}} - Mensaje personalizado")
        
        print(f"\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()