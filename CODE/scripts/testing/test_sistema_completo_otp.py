#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba Completa del Sistema OTP
Prueba: OTP + Preferencias + Notificaciones
"""

import requests
import json
import time

# Configuración
BASE_URL = "https://staging.jemavi.co"
TEST_PHONE = "3002596319"
TEST_EMAIL = "jveyes@gmail.com"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(success, message):
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_1_request_otp():
    """Prueba 1: Solicitar OTP"""
    print_section("PRUEBA 1: Solicitar OTP")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customer/preferences-otp/request",
            json={"phone": TEST_PHONE},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("success"):
            print_result(True, "OTP solicitado exitosamente")
            print(f"📱 Mensaje: {data.get('message')}")
            return True
        else:
            print_result(False, f"Error: {data.get('detail', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_result(False, f"Excepción: {str(e)}")
        return False

def test_2_verify_otp(otp_code):
    """Prueba 2: Verificar OTP y obtener token"""
    print_section("PRUEBA 2: Verificar OTP")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/customer/preferences-otp/verify",
            json={
                "phone": TEST_PHONE,
                "code": otp_code
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200 and data.get("success"):
            token = data.get("access_token")
            print_result(True, "OTP verificado exitosamente")
            print(f"🔑 Token obtenido: {token[:30]}...")
            return token
        else:
            print_result(False, f"Error: {data.get('detail', 'Unknown error')}")
            return None
            
    except Exception as e:
        print_result(False, f"Excepción: {str(e)}")
        return None

def test_3_get_preferences(token):
    """Prueba 3: Obtener preferencias actuales"""
    print_section("PRUEBA 3: Obtener Preferencias")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/customer-portal/preferences/notifications",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            prefs = data.get("preferences", {})
            
            print_result(True, "Preferencias obtenidas")
            print(f"📱 SMS habilitado: {prefs.get('sms_notifications_enabled')}")
            print(f"📧 Email habilitado: {prefs.get('email_notifications_enabled')}")
            
            return prefs
        else:
            print_result(False, f"Error: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Excepción: {str(e)}")
        return None

def test_4_update_preferences(token, sms_enabled, email_enabled):
    """Prueba 4: Actualizar preferencias"""
    print_section(f"PRUEBA 4: Actualizar Preferencias (SMS={sms_enabled}, Email={email_enabled})")
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/customer-portal/preferences/notifications",
            json={
                "sms_notifications_enabled": sms_enabled,
                "email_notifications_enabled": email_enabled
            },
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            prefs = data.get("preferences", {})
            
            print_result(True, "Preferencias actualizadas")
            print(f"📱 SMS habilitado: {prefs.get('sms_notifications_enabled')}")
            print(f"📧 Email habilitado: {prefs.get('email_notifications_enabled')}")
            
            # Verificar que se guardaron correctamente
            if prefs.get('sms_notifications_enabled') == sms_enabled and \
               prefs.get('email_notifications_enabled') == email_enabled:
                print_result(True, "Valores guardados correctamente")
                return True
            else:
                print_result(False, "Valores NO coinciden con lo enviado")
                return False
        else:
            print_result(False, f"Error: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Excepción: {str(e)}")
        return False

def test_5_verify_persistence(token):
    """Prueba 5: Verificar que las preferencias persisten"""
    print_section("PRUEBA 5: Verificar Persistencia")
    
    print("⏳ Esperando 2 segundos...")
    time.sleep(2)
    
    return test_3_get_preferences(token)

def main():
    print("\n" + "🚀"*35)
    print("  PRUEBA COMPLETA DEL SISTEMA OTP Y PREFERENCIAS")
    print("🚀"*35)
    print(f"\n📞 Teléfono de prueba: {TEST_PHONE}")
    print(f"📧 Email de prueba: {TEST_EMAIL}")
    
    # Prueba 1: Solicitar OTP
    if not test_1_request_otp():
        print("\n❌ PRUEBA FALLIDA: No se pudo solicitar OTP")
        return
    
    # Solicitar código al usuario
    print("\n" + "-"*70)
    otp_code = input("🔑 Ingrese el código OTP recibido por SMS: ").strip()
    
    if not otp_code or len(otp_code) != 6:
        print("❌ Código inválido")
        return
    
    # Prueba 2: Verificar OTP
    token = test_2_verify_otp(otp_code)
    if not token:
        print("\n❌ PRUEBA FALLIDA: No se pudo verificar OTP")
        return
    
    # Prueba 3: Obtener preferencias iniciales
    initial_prefs = test_3_get_preferences(token)
    if not initial_prefs:
        print("\n❌ PRUEBA FALLIDA: No se pudieron obtener preferencias")
        return
    
    # Prueba 4a: Deshabilitar SMS
    print("\n⏳ Deshabilitando SMS...")
    if not test_4_update_preferences(token, False, True):
        print("\n❌ PRUEBA FALLIDA: No se pudo actualizar (deshabilitar SMS)")
        return
    
    # Prueba 5a: Verificar persistencia
    prefs_after_1 = test_5_verify_persistence(token)
    if not prefs_after_1:
        print("\n❌ PRUEBA FALLIDA: No se pudo verificar persistencia")
        return
    
    if prefs_after_1.get('sms_notifications_enabled') != False:
        print_result(False, "SMS NO se deshabilitó correctamente")
        return
    
    # Prueba 4b: Habilitar SMS nuevamente
    print("\n⏳ Habilitando SMS nuevamente...")
    if not test_4_update_preferences(token, True, True):
        print("\n❌ PRUEBA FALLIDA: No se pudo actualizar (habilitar SMS)")
        return
    
    # Prueba 5b: Verificar persistencia final
    prefs_after_2 = test_5_verify_persistence(token)
    if not prefs_after_2:
        print("\n❌ PRUEBA FALLIDA: No se pudo verificar persistencia final")
        return
    
    if prefs_after_2.get('sms_notifications_enabled') != True:
        print_result(False, "SMS NO se habilitó correctamente")
        return
    
    # Resumen final
    print_section("RESUMEN FINAL")
    print_result(True, "Todas las pruebas pasaron exitosamente")
    print("\n✅ Sistema OTP: Funcionando")
    print("✅ Preferencias: Se guardan correctamente")
    print("✅ Persistencia: Verificada")
    print("\n" + "🎉"*35)
    print("  SISTEMA COMPLETAMENTE FUNCIONAL")
    print("🎉"*35 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
