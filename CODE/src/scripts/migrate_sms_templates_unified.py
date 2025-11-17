#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migración: Unificación de Plantillas SMS
Versión: 1.0.0
Fecha: 2025-01-24

Este script migra las plantillas SMS antiguas (separadas por evento)
a las nuevas plantillas unificadas (similar al patrón de EmailService).

Uso:
    python -m src.scripts.migrate_sms_templates_unified
"""

import sys
import json
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.notification import SMSMessageTemplate, NotificationEvent
from app.services.sms_service import SMSService
from app.utils.datetime_utils import get_colombia_now


def migrate_templates(db: Session):
    """Migra plantillas SMS a formato unificado"""
    
    print("=" * 70)
    print("MIGRACIÓN DE PLANTILLAS SMS A FORMATO UNIFICADO")
    print("=" * 70)
    print()
    
    # 1. Verificar plantillas existentes
    print("📋 Verificando plantillas existentes...")
    existing_templates = db.query(SMSMessageTemplate).all()
    print(f"   Encontradas: {len(existing_templates)} plantillas")
    
    for template in existing_templates:
        print(f"   - {template.template_id}: {template.name} ({template.event_type.value})")
    
    print()
    
    # 2. Desactivar plantillas antiguas (no eliminar por historial)
    print("🔄 Desactivando plantillas antiguas...")
    old_template_ids = [
        "package_announced",
        "package_received", 
        "package_delivered",
        "package_cancelled"
    ]
    
    deactivated_count = 0
    for template_id in old_template_ids:
        template = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.template_id == template_id
        ).first()
        
        if template:
            template.is_active = False
            template.is_default = False
            deactivated_count += 1
            print(f"   ✓ Desactivada: {template_id}")
    
    db.commit()
    print(f"   Total desactivadas: {deactivated_count}")
    print()
    
    # 3. Crear nuevas plantillas unificadas
    print("✨ Creando plantillas unificadas...")
    sms_service = SMSService()
    new_templates = sms_service.create_default_templates(db)
    
    print(f"   Total creadas/actualizadas: {len(new_templates)}")
    for template in new_templates:
        print(f"   ✓ {template.template_id}: {template.name}")
        print(f"     Mensaje: {template.message_template[:80]}...")
    
    print()
    
    # 4. Verificar resultado final
    print("🔍 Verificando resultado final...")
    active_templates = db.query(SMSMessageTemplate).filter(
        SMSMessageTemplate.is_active == True
    ).all()
    
    print(f"   Plantillas activas: {len(active_templates)}")
    for template in active_templates:
        status = "✅ ACTIVA" if template.is_active else "❌ INACTIVA"
        default = "⭐ DEFAULT" if template.is_default else ""
        print(f"   {status} {default} {template.template_id}")
        print(f"      Evento: {template.event_type.value}")
        print(f"      Variables: {template.available_variables}")
    
    print()
    
    # 5. Resumen de migración
    print("=" * 70)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print()
    print("📊 RESUMEN:")
    print(f"   • Plantillas desactivadas: {deactivated_count}")
    print(f"   • Plantillas nuevas/actualizadas: {len(new_templates)}")
    print(f"   • Plantillas activas totales: {len(active_templates)}")
    print()
    print("🎯 BENEFICIOS DE LA UNIFICACIÓN:")
    print("   ✓ Mantenimiento simplificado (1 plantilla vs 4)")
    print("   ✓ Consistencia con EmailService")
    print("   ✓ Mensajes más uniformes para usuarios")
    print("   ✓ Fácil personalización del texto de estado")
    print()
    print("📝 PRÓXIMOS PASOS:")
    print("   1. Verificar que las notificaciones SMS funcionen correctamente")
    print("   2. Probar envío de SMS con diferentes eventos")
    print("   3. Ajustar textos de plantillas según necesidades")
    print()
    print("💡 NOTA: Las plantillas antiguas se mantienen inactivas")
    print("   para preservar el historial, pero no se usarán más.")
    print()


def rollback_migration(db: Session):
    """Revierte la migración (reactivar plantillas antiguas)"""
    
    print("=" * 70)
    print("⚠️  ROLLBACK: REVERTIR MIGRACIÓN DE PLANTILLAS SMS")
    print("=" * 70)
    print()
    
    # Reactivar plantillas antiguas
    print("🔄 Reactivando plantillas antiguas...")
    old_template_ids = [
        "package_announced",
        "package_received", 
        "package_delivered",
        "package_cancelled"
    ]
    
    reactivated_count = 0
    for template_id in old_template_ids:
        template = db.query(SMSMessageTemplate).filter(
            SMSMessageTemplate.template_id == template_id
        ).first()
        
        if template:
            template.is_active = True
            template.is_default = True
            reactivated_count += 1
            print(f"   ✓ Reactivada: {template_id}")
    
    # Desactivar plantillas unificadas
    print()
    print("🔄 Desactivando plantillas unificadas...")
    unified_template = db.query(SMSMessageTemplate).filter(
        SMSMessageTemplate.template_id == "status_change_unified"
    ).first()
    
    if unified_template:
        unified_template.is_active = False
        unified_template.is_default = False
        print(f"   ✓ Desactivada: status_change_unified")
    
    db.commit()
    
    print()
    print("✅ ROLLBACK COMPLETADO")
    print(f"   Plantillas antiguas reactivadas: {reactivated_count}")
    print()


def main():
    """Función principal"""
    
    print()
    print("🚀 Iniciando migración de plantillas SMS...")
    print()
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Preguntar confirmación
        print("⚠️  Esta operación modificará las plantillas SMS en la base de datos.")
        print()
        print("Opciones:")
        print("  1. Migrar a plantillas unificadas (recomendado)")
        print("  2. Rollback (revertir a plantillas antiguas)")
        print("  3. Solo ver plantillas actuales")
        print("  4. Cancelar")
        print()
        
        choice = input("Seleccione una opción (1-4): ").strip()
        print()
        
        if choice == "1":
            confirm = input("¿Confirma la migración? (si/no): ").strip().lower()
            if confirm in ["si", "s", "yes", "y"]:
                migrate_templates(db)
            else:
                print("❌ Migración cancelada por el usuario")
        
        elif choice == "2":
            confirm = input("¿Confirma el rollback? (si/no): ").strip().lower()
            if confirm in ["si", "s", "yes", "y"]:
                rollback_migration(db)
            else:
                print("❌ Rollback cancelado por el usuario")
        
        elif choice == "3":
            print("📋 PLANTILLAS ACTUALES:")
            print("=" * 70)
            templates = db.query(SMSMessageTemplate).all()
            for template in templates:
                status = "✅ ACTIVA" if template.is_active else "❌ INACTIVA"
                default = "⭐ DEFAULT" if template.is_default else ""
                print(f"{status} {default} {template.template_id}")
                print(f"   Nombre: {template.name}")
                print(f"   Evento: {template.event_type.value}")
                print(f"   Mensaje: {template.message_template[:80]}...")
                print()
        
        else:
            print("❌ Operación cancelada")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()
    
    print()
    print("👋 Migración finalizada")
    print()


if __name__ == "__main__":
    main()
