#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para envío de SMS usando LIWA.co
Uso: python test_sms.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.sms_service import SMSService
from app.schemas.notification import SMSTestRequest
from app.models.notification import NotificationEvent, NotificationPriority


async def test_sms_send():
    """Prueba de envío de SMS"""
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("PRUEBA DE ENVÍO DE SMS - LIWA.CO")
        print("=" * 60)
        
        # Inicializar servicio
        sms_service = SMSService()
        
        # Número de prueba
        test_phone = "3002596319"
        test_message = "Hola! Este es un mensaje de prueba desde PAQUETEX EL CLUB. Sistema funcionando correctamente."
        
        print(f"\n📱 Número destino: {test_phone}")
        print(f"💬 Mensaje: {test_message}")
        print(f"📏 Longitud: {len(test_message)} caracteres")
        
        # Verificar configuración
        print("\n🔧 Verificando configuración...")
        config = sms_service.get_sms_config(db)
        print(f"   ✓ Proveedor: {config.provider}")
        print(f"   ✓ Cuenta: {config.account_id}")
        print(f"   ✓ API Key: {'*' * 20}{config.api_key[-10:] if config.api_key else 'NO CONFIGURADA'}")
        print(f"   ✓ URL Auth: {config.auth_url}")
        print(f"   ✓ URL API: {config.api_url}")
        print(f"   ✓ Modo prueba: {'SÍ' if config.enable_test_mode else 'NO'}")
        
        # Preguntar si continuar
        print("\n⚠️  ATENCIÓN: Este envío consumirá créditos reales de SMS")
        response = input("¿Desea continuar con el envío? (s/n): ")
        
        if response.lower() != 's':
            print("\n❌ Envío cancelado por el usuario")
            return
        
        # Enviar SMS
        print("\n📤 Enviando SMS...")
        result = await sms_service.send_sms(
            db=db,
            recipient=test_phone,
            message=test_message,
            event_type=NotificationEvent.CUSTOM_MESSAGE,
            priority=NotificationPriority.ALTA,
            is_test=False  # Cambiar a True para modo simulación
        )
        
        print("\n" + "=" * 60)
        print("RESULTADO DEL ENVÍO")
        print("=" * 60)
        print(f"Estado: {result.status}")
        print(f"Mensaje: {result.message}")
        print(f"ID Notificación: {result.notification_id}")
        print(f"Costo: ${result.cost_cents / 100:.2f} COP")
        
        if result.status == "sent":
            print("\n✅ SMS ENVIADO EXITOSAMENTE")
        else:
            print("\n❌ ERROR AL ENVIAR SMS")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


async def test_sms_configuration():
    """Prueba solo la configuración sin enviar SMS"""
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("PRUEBA DE CONFIGURACIÓN SMS - LIWA.CO")
        print("=" * 60)
        
        sms_service = SMSService()
        
        # Crear request de prueba
        test_request = SMSTestRequest(
            recipient="3002596319",
            message="Mensaje de prueba - PAQUETEX EL CLUB"
        )
        
        print("\n🔍 Probando configuración...")
        result = await sms_service.test_sms_configuration(db, test_request)
        
        print("\n" + "=" * 60)
        print("RESULTADO DE LA PRUEBA")
        print("=" * 60)
        print(f"Éxito: {'✅ SÍ' if result.success else '❌ NO'}")
        print(f"Mensaje: {result.message}")
        
        if result.notification_id:
            print(f"ID Notificación: {result.notification_id}")
        
        if result.provider_response:
            print(f"Respuesta del proveedor: {result.provider_response}")
        
        if result.error_details:
            print(f"Detalles del error: {result.error_details}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


async def show_sms_stats():
    """Muestra estadísticas de SMS"""
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("ESTADÍSTICAS DE SMS - ÚLTIMOS 30 DÍAS")
        print("=" * 60)
        
        sms_service = SMSService()
        stats = sms_service.get_sms_stats(db, days=30)
        
        print(f"\n📊 Total enviados: {stats['total_sent']}")
        print(f"✅ Total entregados: {stats['total_delivered']}")
        print(f"❌ Total fallidos: {stats['total_failed']}")
        print(f"💰 Costo total: ${stats['total_cost_cents'] / 100:.2f} COP")
        print(f"📈 Tasa de entrega: {stats['delivery_rate']:.2f}%")
        print(f"💵 Costo promedio por SMS: ${stats['average_cost_per_sms'] / 100:.2f} COP")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def main():
    """Menú principal"""
    print("\n" + "=" * 60)
    print("SISTEMA DE PRUEBAS SMS - PAQUETEX EL CLUB")
    print("=" * 60)
    print("\nOpciones:")
    print("1. Enviar SMS de prueba (consume créditos)")
    print("2. Probar configuración (modo simulación)")
    print("3. Ver estadísticas de SMS")
    print("4. Salir")
    
    choice = input("\nSeleccione una opción (1-4): ")
    
    if choice == "1":
        asyncio.run(test_sms_send())
    elif choice == "2":
        asyncio.run(test_sms_configuration())
    elif choice == "3":
        asyncio.run(show_sms_stats())
    elif choice == "4":
        print("\n👋 Hasta luego!")
        sys.exit(0)
    else:
        print("\n❌ Opción inválida")
        main()


if __name__ == "__main__":
    main()
