#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para enviar SMS de prueba
Uso: python enviar_sms_prueba.py
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.sms_service import SMSService
from app.models.notification import NotificationEvent, NotificationPriority


async def main():
    """Enviar SMS de prueba al número 3002596319"""
    
    # Configuración
    NUMERO_DESTINO = "3002596319"
    MENSAJE = "Hola! Este es un mensaje de prueba desde PAQUETEX EL CLUB. Sistema funcionando correctamente."
    
    print("=" * 70)
    print("ENVÍO DE SMS DE PRUEBA - PAQUETEX EL CLUB")
    print("=" * 70)
    print(f"\n📱 Número destino: {NUMERO_DESTINO}")
    print(f"💬 Mensaje: {MENSAJE}")
    print(f"📏 Longitud: {len(MENSAJE)} caracteres")
    
    # Crear sesión de base de datos
    db: Session = SessionLocal()
    
    try:
        # Inicializar servicio SMS
        sms_service = SMSService()
        
        # Obtener configuración
        print("\n🔧 Verificando configuración...")
        config = sms_service.get_sms_config(db)
        print(f"   ✓ Proveedor: {config.provider}")
        print(f"   ✓ Cuenta: {config.account_id}")
        print(f"   ✓ Modo prueba: {'SÍ (sin costo)' if config.enable_test_mode else 'NO (consumirá créditos)'}")
        
        # Confirmar envío
        print("\n" + "=" * 70)
        if not config.enable_test_mode:
            print("⚠️  ATENCIÓN: Este envío consumirá créditos reales de SMS")
            print("⚠️  Costo estimado: $0.50 COP")
            respuesta = input("\n¿Desea continuar con el envío? (s/n): ")
            
            if respuesta.lower() != 's':
                print("\n❌ Envío cancelado por el usuario")
                return
        else:
            print("ℹ️  Modo de prueba activado - No se consumirán créditos")
        
        # Enviar SMS
        print("\n📤 Enviando SMS...")
        resultado = await sms_service.send_sms(
            db=db,
            recipient=NUMERO_DESTINO,
            message=MENSAJE,
            event_type=NotificationEvent.CUSTOM_MESSAGE,
            priority=NotificationPriority.ALTA,
            is_test=config.enable_test_mode
        )
        
        # Mostrar resultado
        print("\n" + "=" * 70)
        print("RESULTADO DEL ENVÍO")
        print("=" * 70)
        
        if resultado.status == "sent":
            print("\n✅ SMS ENVIADO EXITOSAMENTE")
            print(f"\n📋 Detalles:")
            print(f"   • ID Notificación: {resultado.notification_id}")
            print(f"   • Estado: {resultado.status}")
            print(f"   • Mensaje: {resultado.message}")
            print(f"   • Costo: ${resultado.cost_cents / 100:.2f} COP")
            
            if config.enable_test_mode:
                print(f"\n💡 Nota: Este fue un envío de prueba (simulado)")
            else:
                print(f"\n💡 El SMS debería llegar en los próximos segundos")
        else:
            print("\n❌ ERROR AL ENVIAR SMS")
            print(f"\n📋 Detalles:")
            print(f"   • Estado: {resultado.status}")
            print(f"   • Mensaje: {resultado.message}")
            
            # Buscar más detalles del error en la base de datos
            if resultado.notification_id:
                from app.models.notification import Notification
                notif = db.query(Notification).filter(Notification.id == resultado.notification_id).first()
                if notif and notif.error_message:
                    print(f"   • Error detallado: {notif.error_message}")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
