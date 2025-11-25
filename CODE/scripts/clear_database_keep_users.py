#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar la base de datos manteniendo usuarios y configuración SMS
Versión: 1.1.0
Fecha: 2025-11-25

Este script elimina todos los datos excepto:
- Usuarios autenticados (tabla users)
- Configuración SMS de LIWA (tabla sms_configuration)
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models import (
    Package, Customer, Message, FileUpload, Notification,
    SMSMessageTemplate, SMSConfiguration, Rate, Report,
    ReportTemplate, DashboardMetric, ReportSchedule,
    PackageAnnouncementNew, PackageEvent, UserPreferences,
    CustomerPreferences
)
from app.models.package_history import PackageHistory

def clear_database_keep_users():
    """
    Elimina todos los datos de la base de datos excepto los usuarios
    """
    db = SessionLocal()
    
    try:
        print("🗑️  Iniciando limpieza de base de datos...")
        print("⚠️  ADVERTENCIA: Se eliminarán TODOS los datos excepto:")
        print("   - Usuarios autenticados")
        print("   - Configuración SMS (LIWA)")
        print()
        
        # Confirmar acción
        confirm = input("¿Estás seguro? Escribe 'SI' para continuar: ")
        if confirm != "SI":
            print("❌ Operación cancelada")
            return
        
        print()
        print("🔄 Eliminando datos...")
        
        # Orden de eliminación respetando dependencias de claves foráneas
        
        # 1. Eliminar eventos de paquetes
        count = db.query(PackageEvent).delete()
        print(f"   ✓ Eventos de paquetes eliminados: {count}")
        
        # 2. Eliminar anuncios de paquetes
        count = db.query(PackageAnnouncementNew).delete()
        print(f"   ✓ Anuncios de paquetes eliminados: {count}")
        
        # 3. Eliminar notificaciones
        count = db.query(Notification).delete()
        print(f"   ✓ Notificaciones eliminadas: {count}")
        
        # 4. Eliminar archivos subidos
        count = db.query(FileUpload).delete()
        print(f"   ✓ Archivos subidos eliminados: {count}")
        
        # 5. Eliminar mensajes
        count = db.query(Message).delete()
        print(f"   ✓ Mensajes eliminados: {count}")
        
        # 6. Eliminar historial de paquetes
        count = db.query(PackageHistory).delete()
        print(f"   ✓ Historial de paquetes eliminado: {count}")
        
        # 7. Eliminar paquetes
        count = db.query(Package).delete()
        print(f"   ✓ Paquetes eliminados: {count}")
        
        # 8. Eliminar preferencias de clientes
        count = db.query(CustomerPreferences).delete()
        print(f"   ✓ Preferencias de clientes eliminadas: {count}")
        
        # 9. Eliminar clientes
        count = db.query(Customer).delete()
        print(f"   ✓ Clientes eliminados: {count}")
        
        # 10. Eliminar preferencias de usuarios (opcional, puedes comentar si quieres mantenerlas)
        count = db.query(UserPreferences).delete()
        print(f"   ✓ Preferencias de usuarios eliminadas: {count}")
        
        # Commit de las eliminaciones principales
        db.commit()
        print(f"   💾 Cambios guardados")
        
        # 11. Eliminar reportes y métricas (si existen)
        try:
            count = db.query(ReportSchedule).delete()
            print(f"   ✓ Programaciones de reportes eliminadas: {count}")
        except Exception:
            db.rollback()
            print(f"   ⊘ Tabla report_schedules no existe")
        
        try:
            count = db.query(DashboardMetric).delete()
            print(f"   ✓ Métricas de dashboard eliminadas: {count}")
        except Exception:
            db.rollback()
            print(f"   ⊘ Tabla dashboard_metrics no existe")
        
        try:
            count = db.query(Report).delete()
            print(f"   ✓ Reportes eliminados: {count}")
        except Exception:
            db.rollback()
            print(f"   ⊘ Tabla reports no existe")
        
        try:
            count = db.query(ReportTemplate).delete()
            print(f"   ✓ Plantillas de reportes eliminadas: {count}")
        except Exception:
            db.rollback()
            print(f"   ⊘ Tabla report_templates no existe")
        
        # 12. Eliminar tarifas
        count = db.query(Rate).delete()
        print(f"   ✓ Tarifas eliminadas: {count}")
        
        # 13. Eliminar solo plantillas SMS (mantener configuración de LIWA)
        count = db.query(SMSMessageTemplate).delete()
        print(f"   ✓ Plantillas SMS eliminadas: {count}")
        print(f"   ℹ️  Configuración SMS (LIWA) mantenida")
        
        # Commit final
        db.commit()
        print(f"   💾 Cambios finales guardados")
        
        print()
        print("✅ Base de datos limpiada exitosamente")
        print("👥 Los usuarios autenticados se mantuvieron intactos")
        print("📱 La configuración SMS (LIWA) se mantuvo intacta")
        
        # Mostrar usuarios que quedaron
        from app.models import User
        users = db.query(User).all()
        print()
        print(f"📊 Usuarios en el sistema: {len(users)}")
        for user in users:
            print(f"   - {user.username} ({user.role.value}) - {user.email}")
        
        # Mostrar configuración SMS
        sms_configs = db.query(SMSConfiguration).all()
        print()
        print(f"📱 Configuraciones SMS: {len(sms_configs)}")
        for config in sms_configs:
            print(f"   - Proveedor: {config.provider} (Activo: {config.is_active})")
        
    except Exception as e:
        db.rollback()
        print()
        print(f"❌ Error durante la limpieza: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clear_database_keep_users()
