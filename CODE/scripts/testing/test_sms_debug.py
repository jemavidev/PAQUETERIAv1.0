#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para SMS
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.app.services.sms_service import SMSService
from src.app.database import SessionLocal
import asyncio

async def test_sms():
    service = SMSService()
    db = SessionLocal()
    try:
        # Probar autenticación
        config = service.get_sms_config(db)
        print(f'✅ Config obtenida:')
        print(f'   API Key: {config.api_key[:20]}...')
        print(f'   Account: {config.account_id}')
        print(f'   Auth URL: {config.auth_url}')
        print(f'   API URL: {config.api_url}')
        print(f'   Test Mode: {config.enable_test_mode}')
        
        # Probar autenticación
        print(f'\n🔐 Probando autenticación...')
        token = await service.authenticate_liwa(config)
        print(f'✅ Token obtenido: {token[:50]}...')
        
        # Probar envío de SMS
        print(f'\n📱 Probando envío de SMS...')
        result = await service._send_liwa_sms(
            config,
            "+573334004007",  # Número de prueba
            "PAQUETEX: Código de prueba: 123456"
        )
        print(f'📋 Resultado: {result}')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_sms())
