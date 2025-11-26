#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear plantillas SMS por defecto
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from app.database import SessionLocal
from app.services.sms_service import SMSService

def main():
    """Crear plantillas SMS por defecto"""
    
    print("=" * 70)
    print("CREACIÓN DE PLANTILLAS SMS POR DEFECTO")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        sms_service = SMSService()
        
        print("\n📝 Creando plantillas SMS...")
        templates = sms_service.create_default_templates(db)
        
        print(f"\n✅ Se crearon/actualizaron {len(templates)} plantillas:")
        for template in templates:
            print(f"\n   • {template.name}")
            print(f"     ID: {template.template_id}")
            print(f"     Evento: {template.event_type}")
            print(f"     Mensaje: {template.message_template[:80]}...")
        
        print("\n" + "=" * 70)
        print("✅ PLANTILLAS CREADAS EXITOSAMENTE")
        print("=" * 70)
        
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
