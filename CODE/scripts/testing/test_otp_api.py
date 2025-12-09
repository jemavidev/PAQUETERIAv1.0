#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Pruebas de API para el Portal de Clientes
Versión: 1.0.0
Fecha: 2025-11-30

Este script prueba los endpoints de la API REST del portal de clientes.
Requiere que el servidor esté corriendo.
"""

import requests
import sys
import os
import time

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


# Configuración
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/customer-portal"


def check_server():
    """Verificar que el servidor está corriendo"""
    print_test("Verificar Servidor")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Servidor está corriendo")
            return True
    except requests.exceptions.ConnectionError:
        print_error("Servidor no está corriendo")
        print_warning("Inicia el servidor con:")
        print_info("cd CODE/src && uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print_error(f"Error conectando al servidor: {e}")
        return False


def get_test_phone():
    """Obtener un teléfono de cliente de prueba"""
    print_test("Obtener Cliente de Prueba")
    
    try:
        from app.database import SessionLocal
        from app.models.customer import Customer
        
        db = SessionLocal()
        customer = db.query(Customer).filter(Customer.is_active == True).first()
        db.close()
        
        if customer:
            print_success(f"Cliente: {customer.full_name}")
            print_info(f"Teléfono: {customer.phone}")
            return customer.phone
        else:
            print_error("No hay clientes activos")
            return None
    except Exception as e:
        print_error(f"Error obteniendo cliente: {e}")
        return None


def test_request_otp(phone):
    """Probar solicitud de OTP"""
    print_test("POST /api/customer-portal/request-otp")
    
    payload = {"phone": phone}
    
    try:
        response = requests.post(
            f"{API_URL}/request-otp",
            json=payload,
            timeout=10
        )
        
        print_info(f"Status: {response.status_code}")
        print_info(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_success("OTP solicitado exitosamente")
                return True
            else:
                print_error("Respuesta indica fallo")
                return False
        else:
            print_error(f"Error HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en request: {e}")
        return False


def get_otp_from_db(phone):
    """Obtener el código OTP más reciente de la BD"""
    print_test("Obtener OTP de la Base de Datos")
    
    try:
        from app.database import SessionLocal
        from app.models.customer_otp import CustomerOTP
        from sqlalchemy import desc
        
        db = SessionLocal()
        otp = db.query(CustomerOTP).filter(
            CustomerOTP.customer_phone == phone,
            CustomerOTP.is_expired == False,
            CustomerOTP.is_verified == False
        ).order_by(desc(CustomerOTP.created_at)).first()
        
        db.close()
        
        if otp:
            print_success(f"OTP encontrado: {otp.otp_code}")
            return otp.otp_code
        else:
            print_error("No se encontró OTP")
            return None
            
    except Exception as e:
        print_error(f"Error obteniendo OTP: {e}")
        return None


def test_verify_otp(phone, code):
    """Probar verificación de OTP"""
    print_test("POST /api/customer-portal/verify-otp")
    
    payload = {
        "phone": phone,
        "code": code
    }
    
    try:
        response = requests.post(
            f"{API_URL}/verify-otp",
            json=payload,
            timeout=10
        )
        
        print_info(f"Status: {response.status_code}")
        print_info(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("access_token"):
                print_success("OTP verificado exitosamente")
                print_info(f"Token: {data['access_token'][:50]}...")
                return data["access_token"]
            else:
                print_error("Respuesta indica fallo")
                return None
        else:
            print_error(f"Error HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Error en request: {e}")
        return None


def test_get_customer_data(token):
    """Probar obtención de datos del cliente"""
    print_test("GET /api/customer-portal/me")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_URL}/me",
            headers=headers,
            timeout=10
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Datos del cliente obtenidos")
            print_info(f"Nombre: {data.get('full_name')}")
            print_info(f"Teléfono: {data.get('phone')}")
            print_info(f"Email: {data.get('email')}")
            print_info(f"Paquetes recibidos: {data.get('total_packages_received')}")
            print_info(f"Paquetes entregados: {data.get('total_packages_delivered')}")
            return True
        else:
            print_error(f"Error HTTP {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error en request: {e}")
        return False


def test_get_packages(token):
    """Probar obtención de paquetes"""
    print_test("GET /api/customer-portal/packages")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_URL}/packages",
            headers=headers,
            timeout=10
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Paquetes obtenidos: {data.get('total')}")
            
            if data.get('packages'):
                print_info("Últimos paquetes:")
                for pkg in data['packages'][:3]:
                    print_info(f"  - {pkg.get('tracking_number')} | {pkg.get('status')}")
            
            return True
        else:
            print_error(f"Error HTTP {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error en request: {e}")
        return False


def test_update_customer_data(token):
    """Probar actualización de datos del cliente"""
    print_test("PUT /api/customer-portal/me")
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "email": "test_updated@example.com",
        "address_street": "Calle de Prueba 123"
    }
    
    try:
        response = requests.put(
            f"{API_URL}/me",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Datos actualizados")
            print_info(f"Email: {data.get('email')}")
            print_info(f"Dirección: {data.get('address_street')}")
            return True
        else:
            print_error(f"Error HTTP {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error en request: {e}")
        return False


def test_invalid_token():
    """Probar con token inválido"""
    print_test("GET /api/customer-portal/me (token inválido)")
    
    headers = {"Authorization": "Bearer invalid_token_12345"}
    
    try:
        response = requests.get(
            f"{API_URL}/me",
            headers=headers,
            timeout=10
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print_success("Token inválido rechazado correctamente")
            return True
        else:
            print_error(f"Debería retornar 401, retornó {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en request: {e}")
        return False


def test_wrong_otp_code(phone):
    """Probar con código OTP incorrecto"""
    print_test("POST /api/customer-portal/verify-otp (código incorrecto)")
    
    payload = {
        "phone": phone,
        "code": "000000"  # Código incorrecto
    }
    
    try:
        response = requests.post(
            f"{API_URL}/verify-otp",
            json=payload,
            timeout=10
        )
        
        print_info(f"Status: {response.status_code}")
        print_info(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print_success("Código incorrecto rechazado correctamente")
            return True
        else:
            print_error(f"Debería retornar 400, retornó {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Error en request: {e}")
        return False


def main():
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}🚀 PRUEBAS DE API - PORTAL DE CLIENTES{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    
    results = {}
    
    # 1. Verificar servidor
    if not check_server():
        print(f"\n{Colors.RED}❌ El servidor no está corriendo. Inicia el servidor primero.{Colors.RESET}")
        return 1
    
    results['server'] = True
    
    # 2. Obtener teléfono de prueba
    test_phone = get_test_phone()
    if not test_phone:
        print(f"\n{Colors.RED}❌ No se pudo obtener un cliente de prueba.{Colors.RESET}")
        return 1
    
    results['test_phone'] = True
    
    # 3. Solicitar OTP
    results['request_otp'] = test_request_otp(test_phone)
    
    if not results['request_otp']:
        print(f"\n{Colors.RED}❌ No se pudo solicitar OTP.{Colors.RESET}")
        return 1
    
    # Esperar un momento
    time.sleep(1)
    
    # 4. Obtener código OTP de la BD
    otp_code = get_otp_from_db(test_phone)
    if not otp_code:
        print(f"\n{Colors.RED}❌ No se pudo obtener el código OTP.{Colors.RESET}")
        return 1
    
    results['get_otp'] = True
    
    # 5. Verificar OTP
    access_token = test_verify_otp(test_phone, otp_code)
    results['verify_otp'] = access_token is not None
    
    if not access_token:
        print(f"\n{Colors.RED}❌ No se pudo verificar el OTP.{Colors.RESET}")
        return 1
    
    # 6. Obtener datos del cliente
    results['get_customer_data'] = test_get_customer_data(access_token)
    
    # 7. Obtener paquetes
    results['get_packages'] = test_get_packages(access_token)
    
    # 8. Actualizar datos
    results['update_customer_data'] = test_update_customer_data(access_token)
    
    # 9. Probar token inválido
    results['invalid_token'] = test_invalid_token()
    
    # 10. Probar código incorrecto
    # Solicitar nuevo OTP primero
    test_request_otp(test_phone)
    time.sleep(1)
    results['wrong_code'] = test_wrong_otp_code(test_phone)
    
    # Resumen
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}📊 RESUMEN DE PRUEBAS{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    
    for test_name, result in results.items():
        if result:
            status = f"{Colors.GREEN}✅ PASÓ{Colors.RESET}"
        else:
            status = f"{Colors.RED}❌ FALLÓ{Colors.RESET}"
        
        print(f"{test_name.upper().replace('_', ' '):.<40} {status}")
    
    # Resultado final
    all_passed = all(results.values())
    
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ¡TODAS LAS PRUEBAS DE API PASARON!{Colors.RESET}")
        print(f"\n{Colors.GREEN}La API del portal de clientes está funcionando correctamente.{Colors.RESET}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ ALGUNAS PRUEBAS FALLARON{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Revisa los errores anteriores.{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
