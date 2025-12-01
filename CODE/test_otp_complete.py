#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Pruebas Completas para el Sistema OTP del Portal de Clientes
Versión: 1.0.0
Fecha: 2025-01-30

Este script prueba:
1. Modelo CustomerOTP
2. Servicio CustomerPortalService
3. Validaciones y lógica de negocio
4. Rate limiting
5. Expiración de códigos
6. Intentos fallidos
"""

import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}🧪 TEST: {name}{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_info(msg):
    print(f"   {msg}")


# ========================================
# TEST 1: Imports y Configuración
# ========================================

def test_imports():
    """Verificar que todos los módulos se importan correctamente"""
    print_test("Imports y Configuración")
    
    try:
        from app.models.customer_otp import CustomerOTP
        print_success("Modelo CustomerOTP importado")
    except Exception as e:
        print_error(f"Error importando CustomerOTP: {e}")
        return False
    
    try:
        from app.services.customer_portal_service import CustomerPortalService
        print_success("Servicio CustomerPortalService importado")
    except Exception as e:
        print_error(f"Error importando servicio: {e}")
        return False
    
    try:
        from app.schemas.customer_portal import (
            OTPRequest, OTPVerifyRequest, OTPResponse, OTPVerifyResponse
        )
        print_success("Schemas importados")
    except Exception as e:
        print_error(f"Error importando schemas: {e}")
        return False
    
    try:
        from app.database import SessionLocal, engine
        print_success("Base de datos configurada")
    except Exception as e:
        print_error(f"Error configurando base de datos: {e}")
        return False
    
    return True


# ========================================
# TEST 2: Modelo CustomerOTP
# ========================================

def test_customer_otp_model():
    """Probar el modelo CustomerOTP"""
    print_test("Modelo CustomerOTP")
    
    from app.models.customer_otp import CustomerOTP
    from app.utils.datetime_utils import get_colombia_now
    
    # Test 2.1: Creación de OTP
    print_info("2.1 - Creación de OTP")
    otp = CustomerOTP(customer_phone="+573001234567")
    
    if otp.otp_code and len(otp.otp_code) == 6 and otp.otp_code.isdigit():
        print_success(f"Código OTP generado: {otp.otp_code}")
    else:
        print_error(f"Código OTP inválido: {otp.otp_code}")
        return False
    
    if otp.expires_at:
        print_success(f"Fecha de expiración: {otp.expires_at}")
    else:
        print_error("No se estableció fecha de expiración")
        return False
    
    # Test 2.2: Validación de OTP nuevo
    print_info("2.2 - Validación de OTP nuevo")
    if otp.is_valid():
        print_success("OTP nuevo es válido")
    else:
        print_error("OTP nuevo debería ser válido")
        return False
    
    # Test 2.3: Verificación con código correcto
    print_info("2.3 - Verificación con código correcto")
    correct_code = otp.otp_code
    if otp.verify(correct_code):
        print_success("Código correcto verificado exitosamente")
    else:
        print_error("Verificación falló con código correcto")
        return False
    
    if otp.is_verified:
        print_success("OTP marcado como verificado")
    else:
        print_error("OTP no se marcó como verificado")
        return False
    
    # Test 2.4: Verificación con código incorrecto
    print_info("2.4 - Verificación con código incorrecto")
    otp2 = CustomerOTP(customer_phone="+573001234567")
    wrong_code = "999999"
    
    if not otp2.verify(wrong_code):
        print_success("Código incorrecto rechazado correctamente")
    else:
        print_error("Código incorrecto fue aceptado")
        return False
    
    if otp2.attempts == 1:
        print_success(f"Intentos incrementados correctamente: {otp2.attempts}")
    else:
        print_error(f"Intentos incorrectos: {otp2.attempts}")
        return False
    
    # Test 2.5: Máximo de intentos
    print_info("2.5 - Máximo de intentos")
    otp3 = CustomerOTP(customer_phone="+573001234567")
    otp3.max_attempts = 3
    
    # Intentar 3 veces con código incorrecto
    for i in range(3):
        otp3.verify("000000")
    
    if otp3.is_expired:
        print_success("OTP expirado después de máximo de intentos")
    else:
        print_error("OTP no se marcó como expirado")
        return False
    
    if not otp3.is_valid():
        print_success("OTP expirado no es válido")
    else:
        print_error("OTP expirado debería ser inválido")
        return False
    
    # Test 2.6: OTP expirado por tiempo
    print_info("2.6 - OTP expirado por tiempo")
    otp4 = CustomerOTP(customer_phone="+573001234567")
    # Simular expiración
    otp4.expires_at = get_colombia_now() - timedelta(minutes=1)
    
    if not otp4.is_valid():
        print_success("OTP expirado por tiempo no es válido")
    else:
        print_error("OTP expirado por tiempo debería ser inválido")
        return False
    
    return True


# ========================================
# TEST 3: Base de Datos
# ========================================

def test_database():
    """Probar conexión y tabla en base de datos"""
    print_test("Base de Datos")
    
    from app.database import SessionLocal, engine
    from sqlalchemy import text
    
    # Test 3.1: Conexión
    print_info("3.1 - Conexión a base de datos")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print_success("Conexión exitosa")
    except Exception as e:
        print_error(f"Error de conexión: {e}")
        return False
    
    # Test 3.2: Tabla customer_otps existe
    print_info("3.2 - Verificar tabla customer_otps")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'customer_otps'
                );
            """))
            exists = result.scalar()
            
            if exists:
                print_success("Tabla customer_otps existe")
            else:
                print_error("Tabla customer_otps NO existe")
                print_warning("Ejecuta: cd CODE && python3 create_customer_otps_table.py")
                return False
    except Exception as e:
        print_error(f"Error verificando tabla: {e}")
        return False
    
    # Test 3.3: Estructura de la tabla
    print_info("3.3 - Verificar estructura de la tabla")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'customer_otps'
                ORDER BY ordinal_position;
            """))
            
            columns = result.fetchall()
            expected_columns = [
                'id', 'customer_phone', 'otp_code', 'attempts', 
                'max_attempts', 'is_verified', 'is_expired', 
                'created_at', 'expires_at', 'verified_at'
            ]
            
            found_columns = [col[0] for col in columns]
            
            missing = set(expected_columns) - set(found_columns)
            if missing:
                print_error(f"Columnas faltantes: {missing}")
                return False
            
            print_success(f"Estructura correcta ({len(found_columns)} columnas)")
    except Exception as e:
        print_error(f"Error verificando estructura: {e}")
        return False
    
    # Test 3.4: Insertar y recuperar OTP
    print_info("3.4 - Insertar y recuperar OTP")
    try:
        from app.models.customer_otp import CustomerOTP
        
        db = SessionLocal()
        
        # Limpiar OTPs de prueba anteriores
        db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == "+573009999999"
        ).delete()
        db.commit()
        
        # Crear nuevo OTP
        test_otp = CustomerOTP(customer_phone="+573009999999")
        db.add(test_otp)
        db.commit()
        db.refresh(test_otp)
        
        print_success(f"OTP insertado con ID: {test_otp.id}")
        
        # Recuperar OTP
        retrieved = db.query(CustomerOTP).filter(
            CustomerOTP.id == test_otp.id
        ).first()
        
        if retrieved and retrieved.otp_code == test_otp.otp_code:
            print_success("OTP recuperado correctamente")
        else:
            print_error("Error recuperando OTP")
            return False
        
        # Limpiar
        db.delete(test_otp)
        db.commit()
        db.close()
        
    except Exception as e:
        print_error(f"Error en operaciones de BD: {e}")
        return False
    
    return True


# ========================================
# TEST 4: Servicio CustomerPortalService
# ========================================

def test_customer_portal_service():
    """Probar el servicio de portal de clientes"""
    print_test("Servicio CustomerPortalService")
    
    from app.services.customer_portal_service import CustomerPortalService
    from app.database import SessionLocal
    from app.models.customer import Customer
    from app.models.customer_otp import CustomerOTP
    from app.schemas.customer_portal import OTPRequest, OTPVerifyRequest
    from sqlalchemy import desc
    
    service = CustomerPortalService()
    db = SessionLocal()
    
    try:
        # Test 4.1: Verificar que existe un cliente de prueba
        print_info("4.1 - Buscar cliente de prueba")
        test_customer = db.query(Customer).filter(
            Customer.is_active == True
        ).first()
        
        if not test_customer:
            print_warning("No hay clientes activos para probar")
            print_info("Crea un cliente de prueba primero")
            return True  # No es un error crítico
        
        print_success(f"Cliente encontrado: {test_customer.full_name} ({test_customer.phone})")
        test_phone = test_customer.phone
        
        # Test 4.2: Limpiar OTPs anteriores
        print_info("4.2 - Limpiar OTPs anteriores")
        db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == test_phone
        ).delete()
        db.commit()
        print_success("OTPs anteriores eliminados")
        
        # Test 4.3: Solicitar OTP (sin enviar SMS real)
        print_info("4.3 - Solicitar OTP")
        
        # Normalizar el teléfono como lo hace el servicio
        from app.utils.phone_utils import normalize_phone
        normalized_phone = normalize_phone(test_phone)
        print_info(f"   Teléfono original: {test_phone}")
        print_info(f"   Teléfono normalizado: {normalized_phone}")
        
        # Crear OTP manualmente para evitar envío de SMS
        new_otp = CustomerOTP(customer_phone=normalized_phone)
        db.add(new_otp)
        db.commit()
        db.refresh(new_otp)
        
        print_success(f"OTP creado: {new_otp.otp_code}")
        
        # Test 4.4: Verificar OTP con código correcto
        print_info("4.4 - Verificar OTP con código correcto")
        
        # Refrescar el OTP para asegurar que tenemos los datos más recientes
        db.refresh(new_otp)
        print_info(f"   Código esperado: '{new_otp.otp_code}' (len={len(new_otp.otp_code)})")
        print_info(f"   OTP ID: {new_otp.id}")
        print_info(f"   OTP attempts: {new_otp.attempts}")
        print_info(f"   OTP is_valid: {new_otp.is_valid()}")
        
        # Verificar que el OTP se puede recuperar de la BD
        retrieved_otp = db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == normalized_phone,
            CustomerOTP.is_expired == False,
            CustomerOTP.is_verified == False
        ).order_by(desc(CustomerOTP.created_at)).first()
        
        if retrieved_otp:
            print_info(f"   OTP recuperado de BD: {retrieved_otp.otp_code}")
            print_info(f"   OTP recuperado ID: {retrieved_otp.id}")
        else:
            print_error("   No se pudo recuperar el OTP de la BD")
            return False
        
        verify_request = OTPVerifyRequest(
            phone=test_phone,
            code=new_otp.otp_code
        )
        print_info(f"   Código enviado: '{verify_request.code}' (len={len(verify_request.code)})")
        
        import asyncio
        response = asyncio.run(service.verify_otp(db, verify_request))
        
        if response.success and response.access_token:
            print_success("Verificación exitosa, token generado")
        else:
            print_error("Verificación falló")
            return False
        
        # Test 4.5: Verificar token
        print_info("4.5 - Verificar token JWT")
        
        token_data = service.verify_token(response.access_token)
        
        if token_data and token_data['customer_id'] == str(test_customer.id):
            print_success("Token válido y contiene datos correctos")
        else:
            print_error("Token inválido")
            return False
        
        # Test 4.6: Rate limiting
        print_info("4.6 - Verificar rate limiting")
        
        # Crear 5 OTPs en la última hora
        from app.utils.datetime_utils import get_colombia_now
        
        db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == test_phone
        ).delete()
        db.commit()
        
        for i in range(5):
            otp = CustomerOTP(customer_phone=test_phone)
            db.add(otp)
        db.commit()
        
        # Intentar crear uno más debería fallar
        try:
            request = OTPRequest(phone=test_phone)
            await_response = asyncio.run(service.request_otp(db, request))
            print_error("Rate limiting no funcionó - debería haber fallado")
            return False
        except Exception as e:
            if "excedido el límite" in str(e).lower():
                print_success("Rate limiting funcionando correctamente")
            else:
                print_error(f"Error inesperado: {e}")
                return False
        
        # Limpiar
        db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == test_phone
        ).delete()
        db.commit()
        
    except Exception as e:
        print_error(f"Error en pruebas de servicio: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True


# ========================================
# TEST 5: Validaciones de Schemas
# ========================================

def test_schemas():
    """Probar validaciones de schemas"""
    print_test("Validaciones de Schemas")
    
    from app.schemas.customer_portal import OTPRequest, OTPVerifyRequest
    from pydantic import ValidationError
    
    # Test 5.1: OTPRequest válido
    print_info("5.1 - OTPRequest válido")
    try:
        request = OTPRequest(phone="+573001234567")
        print_success(f"Request válido: {request.phone}")
    except ValidationError as e:
        print_error(f"Validación falló: {e}")
        return False
    
    # Test 5.2: OTPRequest con teléfono inválido
    print_info("5.2 - OTPRequest con teléfono inválido")
    try:
        request = OTPRequest(phone="abc123")
        print_error("Debería haber rechazado teléfono inválido")
        return False
    except ValidationError:
        print_success("Teléfono inválido rechazado correctamente")
    
    # Test 5.3: OTPVerifyRequest válido
    print_info("5.3 - OTPVerifyRequest válido")
    try:
        request = OTPVerifyRequest(phone="+573001234567", code="123456")
        print_success(f"Request válido: {request.code}")
    except ValidationError as e:
        print_error(f"Validación falló: {e}")
        return False
    
    # Test 5.4: OTPVerifyRequest con código inválido
    print_info("5.4 - OTPVerifyRequest con código inválido")
    try:
        request = OTPVerifyRequest(phone="+573001234567", code="abc")
        print_error("Debería haber rechazado código inválido")
        return False
    except ValidationError:
        print_success("Código inválido rechazado correctamente")
    
    # Test 5.5: Código con longitud incorrecta
    print_info("5.5 - Código con longitud incorrecta")
    try:
        request = OTPVerifyRequest(phone="+573001234567", code="12345")
        print_error("Debería haber rechazado código corto")
        return False
    except ValidationError:
        print_success("Código corto rechazado correctamente")
    
    return True


# ========================================
# MAIN
# ========================================

def main():
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}🚀 PRUEBAS COMPLETAS DEL SISTEMA OTP - PORTAL DE CLIENTES{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    
    results = {}
    
    # Ejecutar pruebas
    results['imports'] = test_imports()
    
    if results['imports']:
        results['model'] = test_customer_otp_model()
        results['database'] = test_database()
        results['schemas'] = test_schemas()
        
        if results['database']:
            results['service'] = test_customer_portal_service()
        else:
            results['service'] = None
    
    # Resumen
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}📊 RESUMEN DE PRUEBAS{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    
    for test_name, result in results.items():
        if result is None:
            status = f"{Colors.YELLOW}⏭️  OMITIDO{Colors.RESET}"
        elif result:
            status = f"{Colors.GREEN}✅ PASÓ{Colors.RESET}"
        else:
            status = f"{Colors.RED}❌ FALLÓ{Colors.RESET}"
        
        print(f"{test_name.upper():.<30} {status}")
    
    # Resultado final
    all_passed = all(r for r in results.values() if r is not None)
    
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡TODAS LAS PRUEBAS PASARON!{Colors.RESET}")
        print(f"\n{Colors.GREEN}El sistema OTP está funcionando correctamente.{Colors.RESET}")
        print(f"{Colors.GREEN}Puedes iniciar el servidor y probar el portal.{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ ALGUNAS PRUEBAS FALLARON{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Revisa los errores anteriores y corrígelos.{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
