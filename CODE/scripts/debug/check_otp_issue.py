#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script rápido para verificar problema de OTP en staging
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.models.customer_otp import CustomerOTP
from sqlalchemy import desc, text

print("\n" + "="*70)
print("🔍 VERIFICACIÓN RÁPIDA DE OTP")
print("="*70)

db = SessionLocal()

# 1. Verificar tabla existe
print("\n1. Verificando tabla customer_otps...")
try:
    result = db.execute(text("SELECT COUNT(*) FROM customer_otps"))
    count = result.scalar()
    print(f"✅ Tabla existe con {count} registros")
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nLa tabla no existe. Ejecuta:")
    print("  python3 create_customer_otps_table.py")
    sys.exit(1)

# 2. Mostrar últimos OTPs
print("\n2. Últimos 10 OTPs creados:")
print("-" * 70)

result = db.execute(text("""
    SELECT 
        customer_phone,
        otp_code,
        attempts,
        max_attempts,
        is_verified,
        is_expired,
        created_at,
        expires_at,
        CASE 
            WHEN expires_at > NOW() THEN 'VIGENTE'
            ELSE 'EXPIRADO'
        END as estado_tiempo
    FROM customer_otps
    ORDER BY created_at DESC
    LIMIT 10
"""))

for row in result:
    phone, code, attempts, max_att, verified, expired, created, expires, estado = row
    
    status = "✅ VERIFICADO" if verified else ("❌ EXPIRADO" if expired else f"⏳ {estado}")
    print(f"\n📱 {phone}")
    print(f"   Código: {code} | Intentos: {attempts}/{max_att} | {status}")
    print(f"   Creado: {created}")
    print(f"   Expira: {expires}")

# 3. Verificar OTPs pendientes
print("\n" + "="*70)
print("3. OTPs pendientes de verificar:")
print("-" * 70)

result = db.execute(text("""
    SELECT 
        customer_phone,
        otp_code,
        attempts,
        max_attempts,
        created_at,
        expires_at,
        EXTRACT(EPOCH FROM (expires_at - NOW())) as segundos_restantes
    FROM customer_otps
    WHERE is_verified = FALSE 
      AND is_expired = FALSE
    ORDER BY created_at DESC
"""))

pending = result.fetchall()

if not pending:
    print("❌ No hay OTPs pendientes")
else:
    for row in pending:
        phone, code, attempts, max_att, created, expires, segundos = row
        
        if segundos and segundos > 0:
            minutos = int(segundos / 60)
            segs = int(segundos % 60)
            tiempo = f"{minutos}m {segs}s"
            estado = "✅ VÁLIDO"
        else:
            tiempo = "EXPIRADO"
            estado = "❌ EXPIRADO POR TIEMPO"
        
        print(f"\n📱 {phone}")
        print(f"   Código: {code}")
        print(f"   Intentos: {attempts}/{max_att}")
        print(f"   Tiempo restante: {tiempo}")
        print(f"   Estado: {estado}")

# 4. Verificar problema de timezone
print("\n" + "="*70)
print("4. Verificación de Timezone:")
print("-" * 70)

result = db.execute(text("""
    SELECT 
        NOW() as hora_servidor,
        CURRENT_TIMESTAMP as timestamp_servidor,
        timezone('America/Bogota', NOW()) as hora_colombia
"""))

row = result.fetchone()
print(f"Hora servidor: {row[0]}")
print(f"Timestamp: {row[1]}")
print(f"Hora Colombia: {row[2]}")

# 5. Probar modelo CustomerOTP
print("\n" + "="*70)
print("5. Prueba de Modelo CustomerOTP:")
print("-" * 70)

# Crear OTP de prueba
test_otp = CustomerOTP(customer_phone="+573009999999")
print(f"✅ OTP creado: {test_otp.otp_code}")
print(f"   Intentos: {test_otp.attempts}")
print(f"   Max intentos: {test_otp.max_attempts}")
print(f"   is_verified: {test_otp.is_verified}")
print(f"   is_expired: {test_otp.is_expired}")
print(f"   expires_at: {test_otp.expires_at}")
print(f"   is_valid(): {test_otp.is_valid()}")

# Probar verificación
correct_code = test_otp.otp_code
result = test_otp.verify(correct_code)
print(f"\n🔍 Verificación con código correcto: {result}")
print(f"   is_verified después: {test_otp.is_verified}")

db.close()

print("\n" + "="*70)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*70)
print("\nSi ves OTPs pendientes pero no puedes verificarlos, revisa:")
print("1. Que el código sea exactamente el mismo (sin espacios)")
print("2. Que no haya expirado (5 minutos)")
print("3. Que no se hayan agotado los intentos (3 máximo)")
print("4. Los logs del servidor para ver errores específicos")
print("\nPara ver logs:")
print("  tail -f logs/app.log | grep -i otp")
print("="*70 + "\n")
