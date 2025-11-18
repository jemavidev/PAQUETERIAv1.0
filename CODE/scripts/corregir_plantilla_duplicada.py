#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir la plantilla SMS que muestra el código duplicado
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate


def main():
    """Corregir plantilla SMS duplicada"""
    
    print("=" * 70)
    print("CORREGIR PLANTILLA SMS DUPLICADA - PAQUETEX EL CLUB")
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
        
        # Plantillas para elegir
        opciones = [
            {
                "num": 1,
                "plantilla": "PAQUETEX: Su paquete {guide_number} esta {status_text}",
                "descripcion": "Solo número de guía, sin código separado"
            },
            {
                "num": 2,
                "plantilla": "PAQUETEX: Su paquete con guia {guide_number} esta {status_text}",
                "descripcion": "Con 'guia' pero sin código duplicado"
            },
            {
                "num": 3,
                "plantilla": "PAQUETEX: Paquete {guide_number} esta {status_text}",
                "descripcion": "Versión más corta"
            }
        ]
        
        print(f"\n📱 PLANTILLA ACTUAL (PROBLEMÁTICA):")
        print(f"   {template.message_template}")
        print(f"   Problema: guide_number y consult_code muestran el mismo valor")
        
        print(f"\n📋 OPCIONES DE CORRECCIÓN:")
        print("=" * 70)
        
        # Mostrar ejemplos de cada opción
        for opcion in opciones:
            print(f"\n{opcion['num']}. {opcion['descripcion']}")
            print(f"   Plantilla: {opcion['plantilla']}")
            
            # Crear plantilla temporal para probar
            template_temp = SMSMessageTemplate(
                template_id="temp",
                name="temp",
                message_template=opcion['plantilla'],
                event_type=template.event_type
            )
            
            # Ejemplos
            ejemplos = [
                {"estado": "ANUNCIADO", "guide": "9B6W"},
                {"estado": "RECIBIDO", "guide": "9B6W"},
                {"estado": "ENTREGADO exitosamente", "guide": "9B6W"}
            ]
            
            for ejemplo in ejemplos:
                try:
                    mensaje = template_temp.render_message({
                        "guide_number": ejemplo["guide"],
                        "status_text": ejemplo["estado"]
                    })
                    print(f"   📱 {ejemplo['estado']}: \"{mensaje}\"")
                    print(f"      Longitud: {len(mensaje)} caracteres")
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
            
            print("-" * 50)
        
        # Seleccionar opción
        while True:
            try:
                seleccion = int(input(f"\nSeleccione la opción (1-3): "))
                if 1 <= seleccion <= 3:
                    break
                else:
                    print("❌ Seleccione un número entre 1 y 3")
            except ValueError:
                print("❌ Ingrese un número válido")
        
        plantilla_nueva = opciones[seleccion - 1]["plantilla"]
        
        print(f"\n📱 PLANTILLA SELECCIONADA:")
        print(f"   {plantilla_nueva}")
        print(f"   Longitud: {len(plantilla_nueva)} caracteres")
        
        # Mostrar vista previa final
        print(f"\n📋 VISTA PREVIA FINAL:")
        template_final = SMSMessageTemplate(
            template_id="temp",
            name="temp",
            message_template=plantilla_nueva,
            event_type=template.event_type
        )
        
        ejemplos_finales = [
            {"estado": "ANUNCIADO", "guide": "ABC123"},
            {"estado": "RECIBIDO en nuestras instalaciones", "guide": "DEF456"},
            {"estado": "ENTREGADO exitosamente", "guide": "GHI789"},
            {"estado": "CANCELADO", "guide": "JKL012"}
        ]
        
        for ejemplo in ejemplos_finales:
            mensaje = template_final.render_message({
                "guide_number": ejemplo["guide"],
                "status_text": ejemplo["estado"]
            })
            print(f"   📱 \"{mensaje}\"")
            print(f"      Longitud: {len(mensaje)} caracteres")
        
        # Confirmar cambio
        print(f"\n" + "=" * 70)
        confirmar = input(f"¿Confirmar actualización? (s/n): ").lower()
        
        if confirmar != 's':
            print(f"\n❌ Operación cancelada")
            return
        
        # Actualizar plantilla
        template.message_template = plantilla_nueva
        db.commit()
        
        print(f"\n✅ PLANTILLA CORREGIDA EXITOSAMENTE")
        print(f"   Nueva plantilla: {template.message_template}")
        print(f"   Problema solucionado: Ya no se duplica el código")
        print(f"\n🎉 Los próximos SMS usarán la plantilla corregida")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()