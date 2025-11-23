#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el cambio de estado de paquetes y verificar envío de SMS
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.package import Package, PackageStatus
from app.services.package_state_service import PackageStateService
from app.utils.datetime_utils import get_colombia_now


async def main():
    """Probar cambio de estado con SMS"""
    
    print("=" * 70)
    print("PRUEBA DE CAMBIO DE ESTADO CON SMS - PAQUETEX EL CLUB")
    print("=" * 70)
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Buscar un paquete en estado RECIBIDO para cambiar a ENTREGADO
        package = db.query(Package).filter(
            Package.status == PackageStatus.RECIBIDO
        ).first()
        
        if not package:
            print("❌ No se encontró ningún paquete en estado RECIBIDO para probar")
            return
        
        print(f"\n📦 Paquete encontrado:")
        print(f"   • ID: {package.id}")
        print(f"   • Tracking: {package.tracking_number}")
        print(f"   • Estado actual: {package.status.value}")
        print(f"   • Cliente ID: {package.customer_id}")
        
        if package.customer:
            print(f"   • Cliente: {package.customer.full_name}")
            print(f"   • Teléfono: {getattr(package.customer, 'phone', 'NO TIENE')}")
        else:
            print(f"   • Cliente: NO CARGADO")
        
        # Confirmar cambio
        respuesta = input(f"\n¿Desea cambiar este paquete a ENTREGADO y enviar SMS? (s/n): ")
        
        if respuesta.lower() != 's':
            print(f"\n❌ Operación cancelada por el usuario")
            return
        
        print(f"\n🔄 Cambiando estado a ENTREGADO...")
        
        # Cambiar estado usando el servicio (esto debería enviar SMS automáticamente)
        history_entry = await PackageStateService.update_package_status(
            db=db,
            package=package,
            new_status=PackageStatus.ENTREGADO,
            changed_by="test_script",
            observations="Prueba de cambio de estado con SMS"
        )
        
        print(f"\n✅ Estado cambiado exitosamente")
        print(f"   • Nuevo estado: {package.status.value}")
        print(f"   • Historial ID: {history_entry.id}")
        print(f"   • Fecha cambio: {history_entry.changed_at}")
        
        # Verificar en la base de datos si se creó la notificación SMS
        from app.models.notification import Notification, NotificationType
        
        # Buscar notificaciones SMS recientes para este paquete
        recent_sms = db.query(Notification).filter(
            Notification.notification_type == NotificationType.SMS,
            Notification.package_id == str(package.id),
            Notification.created_at >= get_colombia_now().replace(hour=0, minute=0, second=0)
        ).order_by(Notification.created_at.desc()).first()
        
        if recent_sms:
            print(f"\n📱 SMS encontrado en base de datos:")
            print(f"   • ID: {recent_sms.id}")
            print(f"   • Destinatario: {recent_sms.recipient}")
            print(f"   • Estado: {recent_sms.status.value}")
            print(f"   • Mensaje: {recent_sms.message}")
            print(f"   • Costo: ${recent_sms.cost_cents / 100:.2f} COP")
            print(f"   • Creado: {recent_sms.created_at}")
            
            if recent_sms.sent_at:
                print(f"   • Enviado: {recent_sms.sent_at}")
            
            if recent_sms.error_message:
                print(f"   • Error: {recent_sms.error_message}")
        else:
            print(f"\n❌ No se encontró notificación SMS en la base de datos")
        
        print(f"\n" + "=" * 70)
        print("PRUEBA COMPLETADA")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())