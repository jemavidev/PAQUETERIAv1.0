#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para restaurar la plantilla completa con ambos códigos
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import SMSMessageTemplate, NotificationEvent

def main():
    """Restaurar plantilla completa"""
    
    print("=" * 80)
    print("RESTAURAR PLANTILLA COMPLETA CON AMBOS CÓDIGOS")
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
        
        print(f"\n🎯 PROBLEMA IDENTIFICADO:")
        print(f"   La plantilla actual solo usa guide_number")
        print(f"   Pero ahora sabemos que guide_number y consult_code SON DIFERENTES")
        print(f"   Deberíamos mostrar ambos para dar información completa")
        
        # Opciones de plantilla completa
        opciones = [
            {
                "num": 1,
                "plantilla": "PAQUETEX: Paquete guía {guide_number} código {consult_code} esta {status_text}",
                "descripcion": "Información completa (guía + código)"
            },
            {
                "num": 2,
                "plantilla": "PAQUETEX: Su paquete {consult_code} (guía {guide_number}) esta {status_text}",
                "descripcion": "Código principal + guía entre paréntesis"
            },
            {
                "num": 3,
                "plantilla": "PAQUETEX: Su paquete {consult_code} esta {status_text}. Guía: {guide_number}",
                "descripcion": "Código principal + guía al final"
            },
            {
                "num": 4,
                "plantilla": "PAQUETEX: Su paquete {guide_number} esta {status_text}",
                "descripcion": "Solo código de guía (actual)"
            }
        ]
        
        print(f"\n📋 OPCIONES DE PLANTILLA:")
        print("=" * 80)
        
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
            
            # Ejemplos con datos reales
            ejemplos = [
                {
                    "tipo": "Anuncio",
                    "estado": "ANUNCIADO", 
                    "guia": "SDGWERT", 
                    "codigo": "I1CG"
                },
                {
                    "tipo": "Paquete",
                    "estado": "RECIBIDO", 
                    "guia": "HDIE8R73GDJG", 
                    "codigo": "9B6W"
                },
                {
                    "tipo": "Paquete",
                    "estado": "ENTREGADO exitosamente", 
                    "guia": "99446622", 
                    "codigo": "75VA"
                }
            ]
            
            for ejemplo in ejemplos:
                try:
                    mensaje = template_temp.render_message({
                        "guide_number": ejemplo["guia"],
                        "consult_code": ejemplo["codigo"],
                        "status_text": ejemplo["estado"]
                    })
                    print(f"   📱 {ejemplo['tipo']} {ejemplo['estado']}: \"{mensaje}\"")
                    print(f"      📏 Longitud: {len(mensaje)} caracteres")
                    
                    # Verificar si excede 160 caracteres
                    if len(mensaje) > 160:
                        print(f"      ⚠️  EXCEDE 160 caracteres (costo doble)")
                    else:
                        print(f"      ✅ Dentro del límite SMS")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
            
            print("-" * 60)
        
        # Seleccionar opción
        while True:
            try:
                seleccion = int(input(f"\nSeleccione la opción (1-4): "))
                if 1 <= seleccion <= 4:
                    break
                else:
                    print("❌ Seleccione un número entre 1 y 4")
            except ValueError:
                print("❌ Ingrese un número válido")
        
        plantilla_nueva = opciones[seleccion - 1]["plantilla"]
        
        print(f"\n📱 PLANTILLA SELECCIONADA:")
        print(f"   {plantilla_nueva}")
        
        # Mostrar vista previa final
        print(f"\n📋 VISTA PREVIA FINAL:")
        template_final = SMSMessageTemplate(
            template_id="temp",
            name="temp",
            message_template=plantilla_nueva,
            event_type=template.event_type
        )
        
        casos_finales = [
            {"tipo": "Anuncio", "estado": "ANUNCIADO", "guia": "SDGWERT", "codigo": "I1CG"},
            {"tipo": "Paquete", "estado": "RECIBIDO", "guia": "HDIE8R73GDJG", "codigo": "9B6W"},
            {"tipo": "Paquete", "estado": "ENTREGADO exitosamente", "guia": "99446622", "codigo": "75VA"},
            {"tipo": "Paquete", "estado": "CANCELADO", "guia": "8YEFS377º", "codigo": "UQCY"}
        ]
        
        for caso in casos_finales:
            mensaje = template_final.render_message({
                "guide_number": caso["guia"],
                "consult_code": caso["codigo"],
                "status_text": caso["estado"]
            })
            print(f"   📱 {caso['tipo']} {caso['estado']}: \"{mensaje}\"")
            print(f"      📏 {len(mensaje)} caracteres")
        
        # Confirmar cambio
        print(f"\n" + "=" * 80)
        confirmar = input(f"¿Confirmar actualización? (s/n): ").lower()
        
        if confirmar != 's':
            print(f"\n❌ Operación cancelada")
            return
        
        # Actualizar plantilla
        template.message_template = plantilla_nueva
        db.commit()
        
        print(f"\n✅ PLANTILLA ACTUALIZADA EXITOSAMENTE")
        print(f"   Nueva plantilla: {template.message_template}")
        print(f"   ✅ Ahora muestra información completa")
        print(f"   ✅ Diferencia entre código de guía y código de consulta")
        print(f"\n🎉 Los SMS ahora tendrán información completa y útil")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()