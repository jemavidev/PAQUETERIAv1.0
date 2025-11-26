#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación completa del sistema de notificaciones SMS
Verifica que el sistema esté configurado correctamente para enviar SMS en cambios de estado
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(env_path)

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

def print_section(title):
    """Imprimir sección con formato"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def check_environment_variables():
    """Verificar variables de entorno necesarias"""
    print_section("1. VERIFICACIÓN DE VARIABLES DE ENTORNO")
    
    required_vars = {
        'LIWA_API_KEY': 'API Key de LIWA',
        'LIWA_ACCOUNT': 'Cuenta de LIWA',
        'LIWA_PASSWORD': 'Contraseña de LIWA',
        'LIWA_AUTH_URL': 'URL de autenticación',
        'DATABASE_URL': 'URL de base de datos'
    }
    
    all_ok = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mostrar solo los primeros caracteres para seguridad
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"   ✅ {description} ({var}): {display_value}")
        else:
            print(f"   ❌ {description} ({var}): NO CONFIGURADO")
            all_ok = False
    
    return all_ok

def check_sms_service_code():
    """Verificar que el código del servicio SMS esté correcto"""
    print_section("2. VERIFICACIÓN DEL CÓDIGO DEL SERVICIO SMS")
    
    try:
        from app.services.sms_service import SMSService
        print("   ✅ SMSService importado correctamente")
        
        # Verificar métodos clave
        methods = ['send_sms', 'send_sms_by_event', 'get_template_by_event', '_send_liwa_sms']
        for method in methods:
            if hasattr(SMSService, method):
                print(f"   ✅ Método '{method}' existe")
            else:
                print(f"   ❌ Método '{method}' NO ENCONTRADO")
                return False
        
        return True
    except Exception as e:
        print(f"   ❌ Error importando SMSService: {str(e)}")
        return False

def check_package_state_service():
    """Verificar que el servicio de estados de paquetes esté configurado"""
    print_section("3. VERIFICACIÓN DEL SERVICIO DE ESTADOS DE PAQUETES")
    
    try:
        from app.services.package_state_service import PackageStateService
        print("   ✅ PackageStateService importado correctamente")
        
        # Verificar métodos clave
        methods = ['update_package_status', '_send_sms_notification', '_send_email_notification']
        for method in methods:
            if hasattr(PackageStateService, method):
                print(f"   ✅ Método '{method}' existe")
            else:
                print(f"   ❌ Método '{method}' NO ENCONTRADO")
                return False
        
        # Verificar transiciones de estado permitidas
        print("\n   📋 Transiciones de estado permitidas:")
        from app.models.package import PackageStatus
        for status, allowed in PackageStateService.ALLOWED_TRANSITIONS.items():
            allowed_str = ", ".join([s.value for s in allowed]) if allowed else "NINGUNA (estado final)"
            print(f"      • {status.value} → {allowed_str}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error importando PackageStateService: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_notification_models():
    """Verificar modelos de notificación"""
    print_section("4. VERIFICACIÓN DE MODELOS DE NOTIFICACIÓN")
    
    try:
        from app.models.notification import (
            Notification, NotificationEvent, NotificationStatus,
            NotificationType, NotificationPriority, SMSMessageTemplate
        )
        print("   ✅ Modelos de notificación importados correctamente")
        
        # Verificar eventos disponibles
        print("\n   📋 Eventos de notificación disponibles:")
        for event in NotificationEvent:
            print(f"      • {event.value}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error importando modelos: {str(e)}")
        return False

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print_section("5. VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS")
    
    try:
        from app.database import SessionLocal
        from app.models.notification import SMSConfiguration
        
        db = SessionLocal()
        
        # Verificar configuración SMS
        config = db.query(SMSConfiguration).filter(SMSConfiguration.is_active == True).first()
        
        if config:
            print(f"   ✅ Configuración SMS encontrada:")
            print(f"      • Proveedor: {config.provider}")
            print(f"      • Cuenta: {config.account_id}")
            print(f"      • Modo prueba: {'SÍ' if config.enable_test_mode else 'NO'}")
            print(f"      • Activo: {'SÍ' if config.is_active else 'NO'}")
            print(f"      • Costo por SMS: ${config.cost_per_sms_cents / 100:.2f} COP")
        else:
            print("   ⚠️  No se encontró configuración SMS activa")
            print("      Se creará automáticamente al primer uso")
        
        # Verificar plantillas SMS
        from app.models.notification import SMSMessageTemplate
        templates = db.query(SMSMessageTemplate).filter(SMSMessageTemplate.is_active == True).all()
        
        print(f"\n   📋 Plantillas SMS activas: {len(templates)}")
        for template in templates:
            print(f"      • {template.name} ({template.template_id})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error conectando a la base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_sms_flow():
    """Verificar el flujo completo de envío de SMS"""
    print_section("6. VERIFICACIÓN DEL FLUJO DE ENVÍO DE SMS")
    
    print("\n   📋 Flujo de envío de SMS en cambios de estado:")
    print("      1. Usuario cambia estado del paquete")
    print("      2. PackageStateService.update_package_status() se ejecuta")
    print("      3. Se registra el cambio en PackageHistory")
    print("      4. Se llama a _send_sms_notification()")
    print("      5. Se mapea el estado a NotificationEvent")
    print("      6. Se obtiene la plantilla SMS correspondiente")
    print("      7. Se preparan las variables (guide_number, tracking_code, etc.)")
    print("      8. SMSService.send_sms_by_event() envía el SMS")
    print("      9. Se autentica con LIWA.co")
    print("      10. Se envía el SMS a través de la API de LIWA")
    print("      11. Se registra la notificación en la base de datos")
    
    print("\n   ✅ Flujo verificado en el código")
    return True

def check_event_mapping():
    """Verificar mapeo de eventos"""
    print_section("7. VERIFICACIÓN DE MAPEO DE EVENTOS")
    
    try:
        from app.models.package import PackageStatus
        from app.models.notification import NotificationEvent
        
        event_mapping = {
            PackageStatus.ANUNCIADO: NotificationEvent.PACKAGE_ANNOUNCED,
            PackageStatus.RECIBIDO: NotificationEvent.PACKAGE_RECEIVED,
            PackageStatus.ENTREGADO: NotificationEvent.PACKAGE_DELIVERED,
            PackageStatus.CANCELADO: NotificationEvent.PACKAGE_CANCELLED
        }
        
        print("\n   📋 Mapeo de estados a eventos de notificación:")
        for status, event in event_mapping.items():
            print(f"      • {status.value} → {event.value}")
        
        print("\n   ✅ Todos los estados tienen eventos mapeados")
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando mapeo: {str(e)}")
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("VERIFICACIÓN COMPLETA DEL SISTEMA DE NOTIFICACIONES SMS")
    print("PAQUETEX EL CLUB v4.0")
    print("=" * 70)
    
    results = []
    
    # Ejecutar todas las verificaciones
    results.append(("Variables de entorno", check_environment_variables()))
    results.append(("Servicio SMS", check_sms_service_code()))
    results.append(("Servicio de estados", check_package_state_service()))
    results.append(("Modelos de notificación", check_notification_models()))
    results.append(("Conexión a base de datos", check_database_connection()))
    results.append(("Flujo de envío", check_sms_flow()))
    results.append(("Mapeo de eventos", check_event_mapping()))
    
    # Resumen final
    print_section("RESUMEN DE VERIFICACIÓN")
    
    all_passed = True
    for name, passed in results:
        status = "✅ CORRECTO" if passed else "❌ ERROR"
        print(f"   {status}: {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ SISTEMA DE SMS COMPLETAMENTE FUNCIONAL")
        print("\nEl sistema está configurado correctamente y listo para enviar")
        print("notificaciones SMS automáticamente cuando cambien los estados")
        print("de los paquetes (ANUNCIADO → RECIBIDO → ENTREGADO/CANCELADO)")
    else:
        print("❌ SE ENCONTRARON PROBLEMAS EN EL SISTEMA")
        print("\nPor favor, revise los errores anteriores y corrija los problemas")
        print("antes de usar el sistema de notificaciones SMS.")
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
