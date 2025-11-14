#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de limpieza de base de datos
Elimina todos los datos excepto:
- Usuarios (users)
- Configuración de SMS (sms_configurations, sms_message_templates)
- Preferencias de usuario (user_preferences)
"""

import sys
import os
import argparse

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text
from app.database import get_db, engine
from app.models import (
    Package, Customer, Message, FileUpload, Notification,
    Report, ReportTemplate, DashboardMetric, ReportSchedule,
    Rate, PackageAnnouncementNew, PackageEvent
)

def cleanup_database(skip_confirmation=False):
    """Limpiar la base de datos manteniendo usuarios y configuración"""
    
    print("=" * 80)
    print("🧹 LIMPIEZA DE BASE DE DATOS - PAQUETERÍA v1.0")
    print("=" * 80)
    print()
    print("⚠️  ADVERTENCIA: Esta operación eliminará los siguientes datos:")
    print()
    print("  ❌ Paquetes (packages)")
    print("  ❌ Clientes (customers)")
    print("  ❌ Mensajes (messages)")
    print("  ❌ Archivos subidos (file_uploads)")
    print("  ❌ Notificaciones (notifications)")
    print("  ❌ Reportes (reports, report_templates, dashboard_metrics, report_schedules)")
    print("  ❌ Tarifas (rates)")
    print("  ❌ Anuncios (package_announcements_new)")
    print("  ❌ Eventos de paquetes (package_events)")
    print("  ❌ Historial de paquetes (package_history)")
    print()
    print("✅ SE MANTENDRÁN:")
    print("  ✓ Usuarios (users)")
    print("  ✓ Configuración SMS (sms_configurations, sms_message_templates)")
    print("  ✓ Preferencias de usuario (user_preferences)")
    print()
    print("=" * 80)
    
    if not skip_confirmation:
        response = input("\n¿Está seguro de continuar? (escriba 'SI' para confirmar): ")
        
        if response.strip().upper() != 'SI':
            print("\n❌ Operación cancelada por el usuario.")
            return
    else:
        print("\n⚠️  Modo automático: Saltando confirmación...")
        print()
    
    print("\n🔄 Iniciando limpieza de base de datos...")
    print()
    
    db = next(get_db())
    
    try:
        # Orden de eliminación respetando las foreign keys
        # IMPORTANTE: El orden es crítico para evitar errores de FK
        tables_to_clean = [
            # 1. Tablas de historial y eventos (dependen de packages)
            ("package_events", "Eventos de paquetes"),
            ("package_history", "Historial de paquetes"),
            
            # 2. Archivos y notificaciones
            ("file_uploads", "Archivos subidos"),
            ("notifications", "Notificaciones"),
            
            # 3. Mensajes (puede referenciar packages y customers)
            ("messages", "Mensajes"),
            
            # 4. Reportes (si existen)
            ("report_schedules", "Programación de reportes"),
            ("dashboard_metrics", "Métricas de dashboard"),
            ("report_templates", "Plantillas de reportes"),
            ("reports", "Reportes"),
            
            # 5. Tarifas
            ("rates", "Tarifas"),
            
            # 6. ⚠️ ANUNCIOS PRIMERO (tiene FK a packages, debe ir antes)
            ("package_announcements_new", "Anuncios de paquetes"),
            
            # 7. Paquetes (depende de customers, pero anuncios depende de packages)
            ("packages", "Paquetes"),
            
            # 8. FINALMENTE clientes (al final porque packages y anuncios dependen de ellos)
            ("customers", "Clientes"),
        ]
        
        total_deleted = 0
        
        for table_name, description in tables_to_clean:
            try:
                # Contar registros antes
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                count = db.execute(count_query).scalar()
                
                if count > 0:
                    # Eliminar registros
                    delete_query = text(f"DELETE FROM {table_name}")
                    db.execute(delete_query)
                    db.commit()
                    
                    print(f"  ✅ {description:.<50} {count:>6} registros eliminados")
                    total_deleted += count
                else:
                    print(f"  ⚪ {description:.<50} {count:>6} registros (ya vacía)")
                    
            except Exception as e:
                print(f"  ⚠️  Error al limpiar {description}: {str(e)}")
                db.rollback()
        
        print()
        print("=" * 80)
        print(f"✅ LIMPIEZA COMPLETADA: {total_deleted} registros eliminados")
        print("=" * 80)
        print()
        print("📊 DATOS CONSERVADOS:")
        
        # Mostrar estadísticas de lo que se mantuvo
        preserved_tables = [
            ("users", "Usuarios"),
            ("sms_configurations", "Configuraciones SMS"),
            ("sms_message_templates", "Plantillas SMS"),
            ("user_preferences", "Preferencias de usuario"),
        ]
        
        for table_name, description in preserved_tables:
            try:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                count = db.execute(count_query).scalar()
                print(f"  ✓ {description:.<50} {count:>6} registros")
            except Exception as e:
                print(f"  ⚠️  Error al contar {description}: {str(e)}")
        
        print()
        print("🎉 Base de datos limpia y lista para usar")
        
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Limpieza de base de datos')
    parser.add_argument('--yes', '-y', action='store_true', 
                        help='Saltar confirmación y ejecutar automáticamente')
    args = parser.parse_args()
    
    cleanup_database(skip_confirmation=args.yes)

