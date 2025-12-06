#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y corregir configuración de SMS
Ejecutar en staging para habilitar envío real de SMS
"""
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.notification import SMSConfiguration
from app.utils.datetime_utils import get_colombia_now

def fix_sms_config():
    """Verifica y corrige la configuración de SMS"""
    db = SessionLocal()
    try:
        # Buscar configuración activa
        config = db.query(SMSConfiguration).filter(
            SMSConfiguration.is_active == True
        ).first()
        
        if not config:
            print("❌ No se encontró configuración de SMS activa")
            print("   Creando configuración por defecto...")
            
            config = SMSConfiguration(
                provider="liwa",
                api_key=os.getenv("LIWA_API_KEY"),
                account_id=os.getenv("LIWA_ACCOUNT"),
                password=os.getenv("LIWA_PASSWORD"),
                auth_url=os.getenv("LIWA_AUTH_URL", "https://api.liwa.co/v2/auth/login"),
                api_url="https://api.liwa.co/v2/sms/single",
                default_sender="PAQUETEX",
                enable_test_mode=False,  # ✅ Desactivar modo de prueba
                cost_per_sms_cents=50
            )
            db.add(config)
            db.commit()
            db.refresh(config)
            print("✅ Configuración creada")
        
        print("\n📋 Configuración actual:")
        print(f"   Provider: {config.provider}")
        print(f"   API Key: {config.api_key[:20] if config.api_key else 'NO CONFIGURADO'}...")
        print(f"   Account: {config.account_id}")
        print(f"   Auth URL: {config.auth_url}")
        print(f"   API URL: {config.api_url}")
        print(f"   Test Mode: {config.enable_test_mode}")
        print(f"   Active: {config.is_active}")
        
        # Verificar si está en modo de prueba
        if config.enable_test_mode:
            print("\n⚠️  MODO DE PRUEBA ACTIVADO")
            print("   Los SMS se están simulando, no se envían realmente")
            
            respuesta = input("\n¿Desactivar modo de prueba para enviar SMS reales? (s/n): ")
            if respuesta.lower() == 's':
                config.enable_test_mode = False
                config.updated_at = get_colombia_now()
                db.commit()
                print("✅ Modo de prueba DESACTIVADO")
                print("   Ahora los SMS se enviarán realmente")
            else:
                print("❌ Modo de prueba sigue ACTIVADO")
        else:
            print("\n✅ Modo de prueba DESACTIVADO")
            print("   Los SMS se están enviando realmente")
        
        # Verificar credenciales
        print("\n🔐 Verificando credenciales:")
        if not config.api_key:
            print("   ❌ API Key no configurado")
        else:
            print(f"   ✅ API Key: {config.api_key[:20]}...")
        
        if not config.account_id:
            print("   ❌ Account ID no configurado")
        else:
            print(f"   ✅ Account ID: {config.account_id}")
        
        if not config.password:
            print("   ❌ Password no configurado")
        else:
            print("   ✅ Password: {'*' * len(config.password)}")
        
        print("\n" + "="*60)
        print("RESUMEN:")
        if config.enable_test_mode:
            print("⚠️  SMS en MODO DE PRUEBA (simulados)")
        else:
            print("✅ SMS en MODO REAL (se envían)")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_sms_config()
