#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la plantilla SMS al formato final deseado
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate, NotificationEvent

def main():
    """Actualizar plantilla al formato final"""
    
    print("=" * 80)
    print("ACTUALIZAR PLANTILLA SMS AL FORMATO FINAL")
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
        
        print(f"\n🎯 FORMATO DESEADO:")
        print(f"   PAQUETEX: Paquete con guia {{guide_number}} fue {{status_text}}. Codigo {{consult_code}}")
        
        print(f"\n📋 EJEMPLOS DEL FORMATO DESEADO:")
        ejemplos_deseados = [
            "PAQUETEX: Paquete con guia SDGWERT fue ANUNCIADO exitosamente. Codigo I1CG",
            "PAQUETEX: Paquete con guia HDIE8R73GDJG fue RECIBIDO exitosamente. Codigo 9B6W",
            "PAQUETEX: Paquete con guia 99446622 fue ENTREGADO exitosamente. Codigo 75VA",
            "PAQUETEX: Paquete con guia 99446622 fue CANCELADO. Codigo 75VA"
        ]
        
        for i, ejemplo in enumerate(ejemplos_deseados, 1):
            print(f"   {i}. {ejemplo}")
            print(f"      📏 Longitud: {len(ejemplo)} caracteres")
        
        # Nueva plantilla
        plantilla_nueva = "PAQUETEX: Paquete con guia {guide_number} fue {status_text}. Codigo {consult_code}"
        
        print(f"\n📱 NUEVA PLANTILLA:")
        print(f"   {plantilla_nueva}")
        print(f"   📏 Longitud base: {len(plantilla_nueva)} caracteres")
        
        # Crear plantilla temporal para probar
        template_temp = SMSMessageTemplate(
            template_id="temp",
            name="temp",
            message_template=plantilla_nueva,
            event_type=template.event_type
        )
        
        print(f"\n🧪 PRUEBAS CON DATOS REALES:")
        print("=" * 50)
        
        # Casos de prueba
        casos_prueba = [
            {
                "tipo": "Anuncio",
                "guia": "SDGWERT",
                "estado": "ANUNCIADO exitosamente",
                "codigo": "I1CG"
            },
            {
                "tipo": "Paquete",
                "guia": "HDIE8R73GDJG",
                "estado": "RECIBIDO exitosamente",
                "codigo": "9B6W"
            },
            {
                "tipo": "Paquete",
                "guia": "99446622",
                "estado": "ENTREGADO exitosamente",
                "codigo": "75VA"
            },
            {
                "tipo": "Paquete",
                "guia": "99446622",
                "estado": "CANCELADO",
                "codigo": "75VA"
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            mensaje = template_temp.render_message({
                "guide_number": caso["guia"],
                "status_text": caso["estado"],
                "consult_code": caso["codigo"]
            })
            
            print(f"\n{i}. {caso['tipo']} {caso['estado']}:")
            print(f"   📱 \"{mensaje}\"")
            print(f"   📏 {len(mensaje)} caracteres")
            
            # Verificar si coincide con el formato deseado
            if i <= len(ejemplos_deseados):
                if mensaje == ejemplos_deseados[i-1]:
                    print(f"   ✅ Coincide exactamente con el formato deseado")
                else:
                    print(f"   ⚠️  Diferencia detectada:")
                    print(f"      Esperado: \"{ejemplos_deseados[i-1]}\"")
                    print(f"      Obtenido: \"{mensaje}\"")
        
        # Confirmar actualización
        print(f"\n" + "=" * 80)
        print("COMPARACIÓN FINAL")
        print("=" * 80)
        
        print(f"\n📱 PLANTILLA ANTERIOR:")
        print(f"   {template.message_template}")
        
        print(f"\n📱 PLANTILLA NUEVA:")
        print(f"   {plantilla_nueva}")
        
        print(f"\n🔄 CAMBIOS:")
        print(f"   • 'Su paquete' → 'Paquete'")
        print(f"   • 'esta' → 'fue'")
        print(f"   • Mantiene estructura: guía + estado + código")
        
        confirmar = input(f"\n¿Confirmar actualización? (s/n): ").lower()
        
        if confirmar != 's':
            print(f"\n❌ Operación cancelada")
            return
        
        # Actualizar plantilla
        template.message_template = plantilla_nueva
        db.commit()
        
        print(f"\n✅ PLANTILLA ACTUALIZADA EXITOSAMENTE")
        print(f"   Nueva plantilla: {template.message_template}")
        print(f"\n🎉 Los mensajes SMS ahora seguirán el formato deseado:")
        print(f"   'PAQUETEX: Paquete con guia XXX fue ESTADO. Codigo YYY'")
        
        # Reiniciar servicio para aplicar cambios
        print(f"\n🔄 Reiniciando servicio para aplicar cambios...")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()