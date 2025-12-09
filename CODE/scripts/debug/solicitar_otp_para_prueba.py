#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para solicitar OTP sin verificarlo
Esto simula lo que hace el botón "Solicitar código" en el navegador
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from app.database import SessionLocal
from app.services.customer_portal_service import CustomerPortalService
from app.schemas.customer_portal import OTPRequest

PHONE = '3002596319'

print("\n" + "="*70)
print("📱 SOLICITAR OTP PARA PRUEBA")
print("="*70)

db = SessionLocal()

try:
    service = CustomerPortalService()
    
    print(f"\n1. Solicitando OTP para: {PHONE}")
    
    # Crear request
    request = OTPRequest(phone=PHONE)
    
    # Solicitar OTP (esto crea el código y lo envía por SMS)
    response = asyncio.run(service.request_otp(db, request))
    
    print(f"\n✅ OTP SOLICITADO")
    print(f"="*70)
    print(f"Success: {response.success}")
    print(f"Message: {response.message}")
    print(f"Expira en: {response.expires_in_seconds} segundos")
    print(f"="*70)
    
    # Buscar el código en la BD (para mostrártelo)
    print(f"\n2. Buscando código en BD...")
    
    from app.models.customer_otp import CustomerOTP
    from app.utils.phone_utils import normalize_phone
    from sqlalchemy import desc
    
    phone_normalized = normalize_phone(PHONE)
    otp = db.query(CustomerOTP).filter(
        CustomerOTP.customer_phone == phone_normalized,
        CustomerOTP.is_expired == False,
        CustomerOTP.is_verified == False
    ).order_by(desc(CustomerOTP.created_at)).first()
    
    if otp:
        print(f"\n✅ CÓDIGO GENERADO:")
        print(f"="*70)
        print(f"Código: {otp.otp_code}")
        print(f"Válido por: 5 minutos")
        print(f"Intentos disponibles: 3")
        print(f"="*70)
        print(f"\n🌐 AHORA PRUEBA EN EL NAVEGADOR:")
        print(f"   1. Ve a la página de login")
        print(f"   2. Ingresa teléfono: {PHONE}")
        print(f"   3. Ingresa código: {otp.otp_code}")
        print(f"   4. Haz clic en Verificar")
        print(f"\n⚠️  NO uses este código en pruebas de Python")
        print(f"   Solo úsalo en el navegador")
        print(f"="*70)
    else:
        print(f"\n❌ No se encontró el código")
    
except Exception as e:
    print(f"\n❌ ERROR")
    print(f"="*70)
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensaje: {e}")
    print(f"="*70)
    
    import traceback
    traceback.print_exc()

db.close()

print("\n")
