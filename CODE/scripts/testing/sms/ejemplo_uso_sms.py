#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplos de uso del servicio SMS
Muestra diferentes formas de enviar SMS
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
from app.schemas.notification import SMSTestRequest, SMSByEventRequest


# ========================================
# EJEMPLO 1: Envío Simple
# ========================================

async def ejemplo_envio_simple():
    """Envío simple de SMS"""
    print("\n" + "=" * 70)
    print("EJEMPLO 1: ENVÍO SIMPLE DE SMS")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        sms_service = SMSService()
        
        resultado = await sms_service.send_sms(
            db=db,
            recipient="3002596319",
            message="Hola! Este es un mensaje de prueba.",
            event_type=NotificationEvent.CUSTOM_MESSAGE,
            priority=NotificationPriority.MEDIA,
            is_test=True  # Modo prueba
        )
        
        print(f"✅ Estado: {resultado.status}")
        print(f"📋 ID: {resultado.notification_id}")
        print(f"💰 Costo: ${resultado.cost_cents / 100:.2f} COP")
        
    finally:
        db.close()


# ========================================
# EJEMPLO 2: Envío con Plantilla
# ========================================

async def ejemplo_envio_con_plantilla():
    """Envío usando plantilla de evento"""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: ENVÍO CON PLANTILLA")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        sms_service = SMSService()
        
        # Crear request de evento
        event_request = SMSByEventRequest(
            event_type=NotificationEvent.CUSTOM_MESSAGE,
            priority=NotificationPriority.ALTA,
            custom_variables={
                "customer_name": "Juan Pérez",
                "guide_number": "ABC123",
                "tracking_code": "TRK456"
            },
            is_test=True
        )
        
        # Nota: Este ejemplo requiere que exista un customer_id o package_id
        # para determinar el destinatario
        print("ℹ️  Este ejemplo requiere un customer_id o package_id válido")
        print("   Ver ejemplo 1 para envío directo sin plantilla")
        
    finally:
        db.close()


# ========================================
# EJEMPLO 3: Prueba de Configuración
# ========================================

async def ejemplo_prueba_configuracion():
    """Probar configuración SMS"""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: PRUEBA DE CONFIGURACIÓN")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        sms_service = SMSService()
        
        test_request = SMSTestRequest(
            recipient="3002596319",
            message="Prueba de configuración del sistema SMS"
        )
        
        resultado = await sms_service.test_sms_configuration(db, test_request)
        
        print(f"✅ Éxito: {resultado.success}")
        print(f"📋 Mensaje: {resultado.message}")
        
        if resultado.notification_id:
            print(f"🆔 ID: {resultado.notification_id}")
        
        if resultado.error_details:
            print(f"❌ Error: {resultado.error_details}")
        
    finally:
        db.close()


# ========================================
# EJEMPLO 4: Obtener Estadísticas
# ========================================

async def ejemplo_estadisticas():
    """Obtener estadísticas de SMS"""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: ESTADÍSTICAS DE SMS")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        sms_service = SMSService()
        
        # Estadísticas de los últimos 30 días
        stats = sms_service.get_sms_stats(db, days=30)
        
        print(f"\n📊 Últimos 30 días:")
        print(f"   • Total enviados: {stats['total_sent']}")
        print(f"   • Total entregados: {stats['total_delivered']}")
        print(f"   • Total fallidos: {stats['total_failed']}")
        print(f"   • Costo total: ${stats['total_cost_cents'] / 100:.2f} COP")
        print(f"   • Tasa de entrega: {stats['delivery_rate']:.2f}%")
        print(f"   • Costo promedio: ${stats['average_cost_per_sms'] / 100:.2f} COP")
        
    finally:
        db.close()


# ========================================
# EJEMPLO 5: Verificar Configuración
# ========================================

async def ejemplo_verificar_config():
    """Verificar configuración del sistema"""
    print("\n" + "=" * 70)
    print("EJEMPLO 5: VERIFICAR CONFIGURACIÓN")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        sms_service = SMSService()
        
        config = sms_service.get_sms_config(db)
        
        print(f"\n🔧 Configuración actual:")
        print(f"   • Proveedor: {config.provider}")
        print(f"   • Cuenta: {config.account_id}")
        print(f"   • Remitente: {config.default_sender}")
        print(f"   • Modo prueba: {'SÍ' if config.enable_test_mode else 'NO'}")
        print(f"   • Costo por SMS: ${config.cost_per_sms_cents / 100:.2f} COP")
        print(f"   • URL Auth: {config.auth_url}")
        print(f"   • URL API: {config.api_url}")
        
        if config.last_test_at:
            print(f"   • Última prueba: {config.last_test_at}")
            print(f"   • Resultado: {config.last_test_result}")
        
    finally:
        db.close()


# ========================================
# EJEMPLO 6: Validar Número
# ========================================

def ejemplo_validar_numero():
    """Validar formato de número de teléfono"""
    print("\n" + "=" * 70)
    print("EJEMPLO 6: VALIDAR NÚMERO DE TELÉFONO")
    print("=" * 70)
    
    sms_service = SMSService()
    
    numeros_prueba = [
        "3002596319",      # ✅ Válido
        "+573002596319",   # ✅ Válido
        "573002596319",    # ✅ Válido
        "300259631",       # ❌ Inválido (9 dígitos)
        "30025963199",     # ❌ Inválido (11 dígitos)
        "2002596319",      # ❌ Inválido (no empieza con 3)
        "abc1234567",      # ❌ Inválido (letras)
    ]
    
    print("\n📱 Validando números:")
    for numero in numeros_prueba:
        try:
            sms_service._validate_phone_number(numero)
            print(f"   ✅ {numero:20} - Válido")
        except Exception as e:
            print(f"   ❌ {numero:20} - Inválido: {str(e)}")


# ========================================
# EJEMPLO 7: Crear Plantillas por Defecto
# ========================================

async def ejemplo_crear_plantillas():
    """Crear plantillas por defecto"""
    print("\n" + "=" * 70)
    print("EJEMPLO 7: CREAR PLANTILLAS POR DEFECTO")
    print("=" * 70)
    
    db = SessionLocal()
    try:
        sms_service = SMSService()
        
        plantillas = sms_service.create_default_templates(db)
        
        print(f"\n✅ Se crearon {len(plantillas)} plantillas:")
        for plantilla in plantillas:
            print(f"   • {plantilla.name} ({plantilla.event_type.value})")
        
    finally:
        db.close()


# ========================================
# MENÚ PRINCIPAL
# ========================================

async def main():
    """Menú principal de ejemplos"""
    print("\n" + "=" * 70)
    print("EJEMPLOS DE USO DEL SERVICIO SMS")
    print("=" * 70)
    print("\nSeleccione un ejemplo:")
    print("1. Envío simple de SMS")
    print("2. Envío con plantilla")
    print("3. Prueba de configuración")
    print("4. Ver estadísticas")
    print("5. Verificar configuración")
    print("6. Validar números de teléfono")
    print("7. Crear plantillas por defecto")
    print("8. Ejecutar todos los ejemplos")
    print("0. Salir")
    
    opcion = input("\nOpción (0-8): ")
    
    if opcion == "1":
        await ejemplo_envio_simple()
    elif opcion == "2":
        await ejemplo_envio_con_plantilla()
    elif opcion == "3":
        await ejemplo_prueba_configuracion()
    elif opcion == "4":
        await ejemplo_estadisticas()
    elif opcion == "5":
        await ejemplo_verificar_config()
    elif opcion == "6":
        ejemplo_validar_numero()
    elif opcion == "7":
        await ejemplo_crear_plantillas()
    elif opcion == "8":
        print("\n🚀 Ejecutando todos los ejemplos...\n")
        await ejemplo_envio_simple()
        await ejemplo_envio_con_plantilla()
        await ejemplo_prueba_configuracion()
        await ejemplo_estadisticas()
        await ejemplo_verificar_config()
        ejemplo_validar_numero()
        await ejemplo_crear_plantillas()
    elif opcion == "0":
        print("\n👋 Hasta luego!")
        return
    else:
        print("\n❌ Opción inválida")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
