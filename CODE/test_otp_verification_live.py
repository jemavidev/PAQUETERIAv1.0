#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar verificación de OTP en vivo
Simula exactamente lo que hace el endpoint
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from app.database import SessionLocal
from app.services.customer_portal_service import CustomerPortalService
from app.schemas.customer_portal import OTPVerifyRequest
from app.models.customer_otp import CustomerOTP
from sqlalchemy import desc

print("\n" + "="*70)
print("🧪 PRUEBA DE VERIFICACIÓN OTP EN VIVO")
print("="*70)

# Solicitar datos
print("\nIngresa el teléfono del cliente:")
phone = input("Teléfono: ").strip()

print("\nIngresa el código OTP que recibió:")
code = input("Código: ").strip()

print("\n" + "-"*70)
print("DIAGNÓSTICO PASO A PASO")
print("-"*70)

db = SessionLocal()

# 1. Normalizar teléfono
from app.utils.phone_utils import normalize_phone
normalized_phone = normalize_phone(phone)
print(f"\n1. Normalización de teléfono:")
print(f"   Original: '{phone}'")
print(f"   Normalizado: '{normalized_phone}'")

# 2. Buscar OTP en BD
print(f"\n2. Buscando OTP en base de datos...")

otp = db.query(CustomerOTP).filter(
    CustomerOTP.customer_phone == normalized_phone,
    CustomerOTP.is_expired == False,
    CustomerOTP.is_verified == False
).order_by(desc(CustomerOTP.created_at)).first()

if not otp:
    print("   ❌ No se encontró OTP válido")
    print("\n   Posibles causas:")
    print("   - El OTP ya fue verificado")
    print("   - El OTP está marcado como expirado")
    print("   - No se ha solicitado un OTP para este teléfono")
    
    # Buscar cualquier OTP para este teléfono
    any_otp = db.query(CustomerOTP).filter(
        CustomerOTP.customer_phone == normalized_phone
    ).order_by(desc(CustomerOTP.created_at)).first()
    
    if any_otp:
        print(f"\n   Último OTP encontrado:")
        print(f"   - Código: {any_otp.otp_code}")
        print(f"   - Verificado: {any_otp.is_verified}")
        print(f"   - Expirado: {any_otp.is_expired}")
        print(f"   - Intentos: {any_otp.attempts}/{any_otp.max_attempts}")
        print(f"   - Creado: {any_otp.created_at}")
        print(f"   - Expira: {any_otp.expires_at}")
    
    db.close()
    sys.exit(1)

print(f"   ✅ OTP encontrado")
print(f"   - ID: {otp.id}")
print(f"   - Código en BD: '{otp.otp_code}'")
print(f"   - Intentos: {otp.attempts}/{otp.max_attempts}")
print(f"   - Creado: {otp.created_at}")
print(f"   - Expira: {otp.expires_at}")

# 3. Verificar validez
print(f"\n3. Verificando validez del OTP...")
is_valid = otp.is_valid()
print(f"   is_valid(): {is_valid}")

if not is_valid:
    print("   ❌ OTP no es válido")
    print(f"   - is_verified: {otp.is_verified}")
    print(f"   - is_expired: {otp.is_expired}")
    print(f"   - attempts < max_attempts: {otp.attempts < otp.max_attempts}")
    
    from app.utils.datetime_utils import get_colombia_now
    now = get_colombia_now()
    print(f"   - Hora actual: {now}")
    print(f"   - Expira en: {otp.expires_at}")
    
    try:
        import pytz
        expires_at = otp.expires_at
        if expires_at.tzinfo is None:
            colombia_tz = pytz.timezone('America/Bogota')
            expires_at = colombia_tz.localize(expires_at)
        
        time_diff = (expires_at - now).total_seconds()
        print(f"   - Tiempo restante: {time_diff:.0f} segundos")
        print(f"   - now < expires_at: {now < expires_at}")
    except Exception as e:
        print(f"   - Error comparando tiempos: {e}")
    
    db.close()
    sys.exit(1)

print(f"   ✅ OTP es válido")

# 4. Comparar códigos
print(f"\n4. Comparando códigos...")
print(f"   Código esperado: '{otp.otp_code}' (len={len(otp.otp_code)}, type={type(otp.otp_code)})")
print(f"   Código recibido: '{code}' (len={len(code)}, type={type(code)})")
print(f"   Coinciden: {otp.otp_code == code}")

# Mostrar bytes para detectar caracteres invisibles
print(f"\n   Bytes del código esperado: {otp.otp_code.encode('utf-8')}")
print(f"   Bytes del código recibido: {code.encode('utf-8')}")

if otp.otp_code != code:
    print("\n   ❌ Los códigos NO coinciden")
    
    # Intentar limpiar el código
    code_cleaned = code.strip().replace(' ', '').replace('-', '')
    print(f"\n   Código limpiado: '{code_cleaned}'")
    print(f"   Coincide después de limpiar: {otp.otp_code == code_cleaned}")
    
    if otp.otp_code == code_cleaned:
        print("\n   ⚠️  El código tiene espacios o caracteres extra")
        print("   Usa el código limpiado para continuar")
        code = code_cleaned
    else:
        db.close()
        sys.exit(1)

print(f"   ✅ Los códigos coinciden")

# 5. Ejecutar verify()
print(f"\n5. Ejecutando verify()...")
result = otp.verify(code)
print(f"   Resultado: {result}")
print(f"   is_verified después: {otp.is_verified}")
print(f"   is_expired después: {otp.is_expired}")
print(f"   attempts después: {otp.attempts}")

db.commit()

if not result:
    print("\n   ❌ verify() retornó False")
    db.close()
    sys.exit(1)

print(f"   ✅ verify() exitoso")

# 6. Probar el servicio completo
print(f"\n6. Probando servicio completo...")

try:
    service = CustomerPortalService()
    request = OTPVerifyRequest(phone=phone, code=code)
    
    response = asyncio.run(service.verify_otp(db, request))
    
    print(f"   ✅ Servicio exitoso")
    print(f"   - success: {response.success}")
    print(f"   - message: {response.message}")
    print(f"   - token: {response.access_token[:50]}...")
    
except Exception as e:
    print(f"   ❌ Error en servicio: {e}")
    import traceback
    traceback.print_exc()

db.close()

print("\n" + "="*70)
print("✅ PRUEBA COMPLETADA")
print("="*70 + "\n")
