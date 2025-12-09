#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico OTP para Staging
Versión: 1.0.0
Fecha: 2025-11-30

Este script ayuda a diagnosticar problemas con OTP en staging
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_section(text):
    print(f"\n{'─'*70}")
    print(f"  {text}")
    print(f"{'─'*70}")

def check_database_connection():
    """Verificar conexión a base de datos"""
    print_section("1. CONEXIÓN A BASE DE DATOS")
    
    try:
        from app.database import SessionLocal, engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), version()"))
            db_info = result.fetchone()
            print(f"✅ Conectado a: {db_info[0]}")
            print(f"✅ PostgreSQL: {db_info[1].split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def check_customer_otps_table():
    """Verificar tabla customer_otps"""
    print_section("2. TABLA CUSTOMER_OTPS")
    
    try:
        from app.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Verificar existencia
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'customer_otps'
            );
        """))
        exists = result.scalar()
        
        if not exists:
            print("❌ La tabla customer_otps NO EXISTE")
            print("\nEjecuta en staging:")
            print("  cd CODE && python3 create_customer_otps_table.py")
            return False
        
        print("✅ Tabla customer_otps existe")
        
        # Contar registros
        result = db.execute(text("SELECT COUNT(*) FROM customer_otps"))
        count = result.scalar()
        print(f"📊 Total de OTPs en BD: {count}")
        
        # Últimos 5 OTPs
        result = db.execute(text("""
            SELECT 
                customer_phone,
                otp_code,
                attempts,
                is_verified,
                is_expired,
                created_at,
                expires_at
            FROM customer_otps
            ORDER BY created_at DESC
            LIMIT 5
        """))
        
        otps = result.fetchall()
        if otps:
            print(f"\n📋 Últimos {len(otps)} OTPs:")
            for otp in otps:
                phone, code, attempts, verified, expired, created, expires = otp
                status = "✅ VERIFICADO" if verified else ("❌ EXPIRADO" if expired else "⏳ PENDIENTE")
                print(f"  {phone} | {code} | Intentos: {attempts} | {status}")
                print(f"    Creado: {created} | Expira: {expires}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_recent_otp_for_phone(phone):
    """Verificar OTP más reciente para un teléfono"""
    print_section(f"3. OTP PARA {phone}")
    
    try:
        from app.database import SessionLocal
        from app.models.customer_otp import CustomerOTP
        from sqlalchemy import desc
        
        db = SessionLocal()
        
        # Buscar OTP más reciente
        otp = db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == phone
        ).order_by(desc(CustomerOTP.created_at)).first()
        
        if not otp:
            print(f"❌ No hay OTPs para {phone}")
            return False
        
        print(f"📱 Teléfono: {otp.customer_phone}")
        print(f"🔢 Código: {otp.otp_code}")
        print(f"📊 Intentos: {otp.attempts}/{otp.max_attempts}")
        print(f"✅ Verificado: {otp.is_verified}")
        print(f"❌ Expirado: {otp.is_expired}")
        print(f"📅 Creado: {otp.created_at}")
        print(f"⏰ Expira: {otp.expires_at}")
        
        # Verificar validez
        print(f"\n🔍 Validación:")
        print(f"  is_valid(): {otp.is_valid()}")
        
        # Verificar timezone
        print(f"\n🌍 Timezone:")
        print(f"  expires_at.tzinfo: {otp.expires_at.tzinfo}")
        
        from app.utils.datetime_utils import get_colombia_now
        now = get_colombia_now()
        print(f"  Hora actual: {now}")
        print(f"  now.tzinfo: {now.tzinfo}")
        
        if otp.expires_at.tzinfo is None:
            print(f"  ⚠️  expires_at NO tiene timezone!")
        
        # Comparar tiempos
        try:
            if otp.expires_at.tzinfo is None:
                import pytz
                colombia_tz = pytz.timezone('America/Bogota')
                expires_at_local = colombia_tz.localize(otp.expires_at)
            else:
                expires_at_local = otp.expires_at
            
            time_diff = (expires_at_local - now).total_seconds()
            print(f"  Tiempo restante: {time_diff:.0f} segundos")
            
            if time_diff > 0:
                print(f"  ✅ OTP aún válido")
            else:
                print(f"  ❌ OTP expirado por tiempo")
        except Exception as e:
            print(f"  ❌ Error comparando tiempos: {e}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_otp_verification(phone, code):
    """Probar verificación de OTP"""
    print_section(f"4. PROBAR VERIFICACIÓN: {phone} con código {code}")
    
    try:
        from app.database import SessionLocal
        from app.models.customer_otp import CustomerOTP
        from sqlalchemy import desc
        
        db = SessionLocal()
        
        # Buscar OTP
        otp = db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == phone,
            CustomerOTP.is_expired == False,
            CustomerOTP.is_verified == False
        ).order_by(desc(CustomerOTP.created_at)).first()
        
        if not otp:
            print("❌ No se encontró OTP válido")
            return False
        
        print(f"📋 OTP encontrado:")
        print(f"  Código esperado: '{otp.otp_code}'")
        print(f"  Código recibido: '{code}'")
        print(f"  Coinciden: {otp.otp_code == code}")
        print(f"  is_valid(): {otp.is_valid()}")
        
        # Intentar verificar
        result = otp.verify(code)
        print(f"\n🔍 Resultado de verify(): {result}")
        print(f"  Intentos después: {otp.attempts}")
        print(f"  is_verified: {otp.is_verified}")
        print(f"  is_expired: {otp.is_expired}")
        
        db.commit()
        db.close()
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_customer_exists(phone):
    """Verificar que el cliente existe"""
    print_section(f"5. VERIFICAR CLIENTE: {phone}")
    
    try:
        from app.database import SessionLocal
        from app.models.customer import Customer
        
        db = SessionLocal()
        
        customer = db.query(Customer).filter(
            Customer.phone == phone,
            Customer.is_active == True
        ).first()
        
        if not customer:
            print(f"❌ No existe cliente activo con teléfono {phone}")
            return False
        
        print(f"✅ Cliente encontrado:")
        print(f"  ID: {customer.id}")
        print(f"  Nombre: {customer.full_name}")
        print(f"  Teléfono: {customer.phone}")
        print(f"  Email: {customer.email}")
        print(f"  Activo: {customer.is_active}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_logs():
    """Revisar logs recientes"""
    print_section("6. LOGS RECIENTES")
    
    log_files = [
        'logs/app.log',
        'logs/error.log',
        '/var/log/paquetex/app.log',
        '/var/log/paquetex/error.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📄 {log_file}:")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Últimas 20 líneas que contengan "OTP" o "verify"
                    relevant = [l for l in lines[-100:] if 'OTP' in l or 'verify' in l or 'customer_portal' in l]
                    if relevant:
                        for line in relevant[-20:]:
                            print(f"  {line.strip()}")
                    else:
                        print("  (No hay logs relevantes)")
            except Exception as e:
                print(f"  Error leyendo log: {e}")
        else:
            print(f"❌ {log_file} no existe")

def main():
    print_header("🔍 DIAGNÓSTICO OTP - STAGING")
    
    # 1. Conexión
    if not check_database_connection():
        print("\n❌ No se pudo conectar a la base de datos")
        return 1
    
    # 2. Tabla
    if not check_customer_otps_table():
        print("\n❌ Problema con la tabla customer_otps")
        return 1
    
    # 3. Solicitar teléfono para diagnosticar
    print_section("DIAGNÓSTICO ESPECÍFICO")
    print("\nIngresa el teléfono del cliente que está teniendo problemas:")
    print("(Ejemplo: +573001234567)")
    phone = input("Teléfono: ").strip()
    
    if not phone:
        print("❌ Teléfono no proporcionado")
        return 1
    
    # Normalizar teléfono
    from app.utils.phone_utils import normalize_phone
    phone = normalize_phone(phone)
    print(f"📱 Teléfono normalizado: {phone}")
    
    # 4. Verificar cliente
    if not check_customer_exists(phone):
        print("\n❌ El cliente no existe o no está activo")
        return 1
    
    # 5. Verificar OTP
    check_recent_otp_for_phone(phone)
    
    # 6. Probar verificación (opcional)
    print("\n¿Quieres probar la verificación de un código? (s/n)")
    test = input().strip().lower()
    
    if test == 's':
        print("Ingresa el código OTP:")
        code = input("Código: ").strip()
        test_otp_verification(phone, code)
    
    # 7. Logs
    check_logs()
    
    print_header("✅ DIAGNÓSTICO COMPLETADO")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
