#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la diferencia entre código de guía y código de consulta
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.package import Package
from app.models.announcement_new import PackageAnnouncementNew

def main():
    """Verificar diferencia entre códigos"""
    
    print("=" * 80)
    print("DIFERENCIA ENTRE CÓDIGO DE GUÍA Y CÓDIGO DE CONSULTA")
    print("=" * 80)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        print(f"\n🔍 CONCEPTOS:")
        print("=" * 50)
        print(f"📋 CÓDIGO DE GUÍA (guide_number):")
        print(f"   • Es el número que usa el transportador internamente")
        print(f"   • Puede ser largo y complejo")
        print(f"   • Ejemplo: 'SDDSCVZD', 'TEST123456789'")
        
        print(f"\n🔍 CÓDIGO DE CONSULTA (consult_code):")
        print(f"   • Es el código que el cliente usa para consultar")
        print(f"   • Debe ser corto y fácil de recordar")
        print(f"   • Ejemplo: '8PEX', '9B6W', 'LTEM'")
        
        # Revisar anuncios (donde SÍ son diferentes)
        print(f"\n📋 ANUNCIOS (FUNCIONAN CORRECTAMENTE):")
        print("=" * 50)
        
        announcements = db.query(PackageAnnouncementNew).limit(3).all()
        
        for i, announcement in enumerate(announcements, 1):
            print(f"\n{i}. Anuncio ID: {announcement.id}")
            print(f"   📦 guide_number (guía transportador): '{announcement.guide_number}'")
            print(f"   🔍 tracking_code (consulta cliente): '{announcement.tracking_code}'")
            print(f"   ✅ ¿Son diferentes? {'SÍ' if announcement.guide_number != announcement.tracking_code else 'NO'}")
            
            if announcement.guide_number != announcement.tracking_code:
                print(f"   💡 Plantilla correcta: 'Paquete guía {announcement.guide_number} código {announcement.tracking_code}'")
            else:
                print(f"   ⚠️  Ambos códigos son iguales")
        
        # Revisar paquetes (donde pueden ser iguales)
        print(f"\n📦 PAQUETES (PROBLEMA IDENTIFICADO):")
        print("=" * 50)
        
        packages = db.query(Package).limit(5).all()
        
        for i, package in enumerate(packages, 1):
            print(f"\n{i}. Paquete ID: {package.id}")
            print(f"   📦 guide_number: '{package.guide_number}'")
            print(f"   🔍 tracking_number: '{package.tracking_number}'")
            print(f"   ✅ ¿Son diferentes? {'SÍ' if package.guide_number != package.tracking_number else 'NO'}")
            
            if package.guide_number == package.tracking_number:
                print(f"   ⚠️  PROBLEMA: Ambos códigos son iguales = '{package.guide_number}'")
                print(f"   💡 En SMS aparecería: 'Paquete guía {package.guide_number} código {package.tracking_number}'")
                print(f"   📱 Resultado: 'Paquete guía LTEM código LTEM' (DUPLICADO)")
        
        print(f"\n" + "=" * 80)
        print("ANÁLISIS DEL PROBLEMA")
        print("=" * 80)
        
        print(f"\n🎯 PROBLEMA IDENTIFICADO:")
        print(f"   En los PAQUETES, guide_number y tracking_number son iguales")
        print(f"   Esto causa duplicación en los SMS")
        
        print(f"\n💡 SOLUCIONES POSIBLES:")
        print(f"\n1️⃣ OPCIÓN 1: Usar solo un código en la plantilla")
        print(f"   Plantilla: 'PAQUETEX: Su paquete {{guide_number}} esta {{status_text}}'")
        print(f"   Resultado: 'PAQUETEX: Su paquete LTEM esta ENTREGADO'")
        
        print(f"\n2️⃣ OPCIÓN 2: Generar códigos de consulta diferentes")
        print(f"   - Mantener guide_number como está")
        print(f"   - Generar tracking_number diferente y más corto")
        print(f"   - Plantilla: 'PAQUETEX: Paquete guía {{guide_number}} código {{consult_code}}'")
        
        print(f"\n3️⃣ OPCIÓN 3: Plantilla inteligente")
        print(f"   - Si son iguales: usar solo uno")
        print(f"   - Si son diferentes: usar ambos")
        
        print(f"\n📱 RECOMENDACIÓN:")
        print(f"   Para evitar confusión, usar OPCIÓN 1 (un solo código)")
        print(f"   Es más simple y evita duplicación")
        
        # Mostrar ejemplos de plantillas
        print(f"\n📋 EJEMPLOS DE PLANTILLAS SIN DUPLICACIÓN:")
        print("=" * 50)
        
        plantillas = [
            "PAQUETEX: Su paquete {guide_number} esta {status_text}",
            "PAQUETEX: Paquete {guide_number} esta {status_text}",
            "PAQUETEX: Su envío {guide_number} esta {status_text}"
        ]
        
        for i, plantilla in enumerate(plantillas, 1):
            print(f"\n{i}. {plantilla}")
            ejemplo = plantilla.format(guide_number="LTEM", status_text="ENTREGADO")
            print(f"   📱 Ejemplo: \"{ejemplo}\"")
            print(f"   📏 Longitud: {len(ejemplo)} caracteres")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()