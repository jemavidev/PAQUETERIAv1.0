#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para ver el error específico del SMS fallido
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import Notification


def main():
    """Ver error específico del SMS"""
    
    print("=" * 70)
    print("ERROR ESPECÍFICO SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Buscar la notificación más reciente fallida
        notification = db.query(Notification).filter(
            Notification.id == 124  # ID de la notificación que falló
        ).first()
        
        if notification:
            print(f"\n📱 Notificación SMS ID: {notification.id}")
            print(f"   • Destinatario: {notification.recipient}")
            print(f"   • Estado: {notification.status.value}")
            print(f"   • Mensaje: {notification.message}")
            print(f"   • Error: {notification.error_message}")
            print(f"   • Código error: {notification.error_code}")
            print(f"   • Respuesta proveedor: {notification.provider_response}")
            print(f"   • Creado: {notification.created_at}")
            print(f"   • Intentos: {notification.retry_count}")
        else:
            print(f"❌ No se encontró la notificación ID 124")
        
        # Buscar las últimas 5 notificaciones SMS fallidas
        print(f"\n📋 Últimas 5 notificaciones SMS fallidas:")
        from app.models.notification import NotificationType, NotificationStatus
        failed_notifications = db.query(Notification).filter(
            Notification.notification_type == NotificationType.SMS,
            Notification.status == NotificationStatus.FAILED
        ).order_by(Notification.created_at.desc()).limit(5).all()
        
        for notif in failed_notifications:
            print(f"\n📱 ID: {notif.id}")
            print(f"   • Destinatario: {notif.recipient}")
            print(f"   • Error: {notif.error_message}")
            print(f"   • Creado: {notif.created_at}")
        
        print(f"\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()