#!/usr/bin/env python3
"""
Script de Prueba: Implementación OTP para Preferencias
Verifica que la nueva funcionalidad no rompa nada existente
"""

import sys
sys.path.insert(0, 'src')

def test_imports():
    """Verificar que todos los imports funcionen"""
    print("="*70)
    print("TEST 1: IMPORTS")
    print("="*70)
    
    try:
        from app.routes.customer_preferences_otp import router as otp_router
        print("✅ customer_preferences_otp.py importado correctamente")
        print(f"   Prefix: {otp_router.prefix}")
        print(f"   Rutas: {len(otp_router.routes)}")
        
        from app.routes.customer_preferences import router as prefs_router
        print("✅ customer_preferences.py importado correctamente")
        print(f"   Prefix: {prefs_router.prefix}")
        
        from app.routes.views import router as views_router
        print("✅ views.py importado correctamente")
        
        from app.config_routes import is_public_route, is_api_public_route
        print("✅ config_routes.py importado correctamente")
        
        return True
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False


def test_routes_configuration():
    """Verificar configuración de rutas"""
    print("\n" + "="*70)
    print("TEST 2: CONFIGURACIÓN DE RUTAS")
    print("="*70)
    
    from app.config_routes import is_public_route, is_api_public_route
    
    # Rutas HTML que deben ser públicas
    html_routes = {
        "/": True,
        "/announce": True,
        "/search": True,
        "/auth/login": True,
        "/customer-portal": True,
        "/customer/preferences": True,  # Existente
        "/customer/verify": True,  # Nueva
    }
    
    print("\nRutas HTML:")
    all_ok = True
    for route, should_be_public in html_routes.items():
        is_public = is_public_route(route)
        status = "✅" if is_public == should_be_public else "❌"
        label = "NUEVA" if route == "/customer/verify" else "EXISTENTE"
        print(f"{status} {route} - {label}")
        if is_public != should_be_public:
            all_ok = False
    
    # Rutas API que deben ser públicas
    api_routes = {
        "/api/auth/login": True,
        "/api/customer-portal/request-otp": True,
        "/api/customer/preferences": True,  # Existente
        "/api/customer/preferences-otp/request": True,  # Nueva
        "/api/customer/preferences-otp/verify": True,  # Nueva
        "/api/customer/preferences-otp/send-link": True,  # Nueva
    }
    
    print("\nRutas API:")
    for route, should_be_public in api_routes.items():
        is_public = is_api_public_route(route)
        status = "✅" if is_public == should_be_public else "❌"
        label = "NUEVA" if "preferences-otp" in route else "EXISTENTE"
        print(f"{status} {route} - {label}")
        if is_public != should_be_public:
            all_ok = False
    
    return all_ok


def test_existing_functionality():
    """Verificar que funcionalidades existentes sigan funcionando"""
    print("\n" + "="*70)
    print("TEST 3: FUNCIONALIDADES EXISTENTES")
    print("="*70)
    
    try:
        # Test 1: Portal de clientes existente
        from app.routes.customer_portal import router as portal_router
        print("✅ Portal de clientes (/customer-portal) - OK")
        
        # Test 2: Preferencias existentes
        from app.routes.customer_preferences import router as prefs_router
        print("✅ Preferencias existentes (/api/customer/preferences) - OK")
        
        # Test 3: Servicio de portal existente
        from app.services.customer_portal_service import CustomerPortalService
        service = CustomerPortalService()
        print("✅ CustomerPortalService - OK")
        
        # Test 4: Modelo OTP existente
        from app.models.customer_otp import CustomerOTP
        print("✅ Modelo CustomerOTP - OK")
        
        # Test 5: Modelo de preferencias existente
        from app.models.customer_preferences import CustomerPreferences
        print("✅ Modelo CustomerPreferences - OK")
        
        return True
    except Exception as e:
        print(f"❌ Error en funcionalidades existentes: {e}")
        return False


def test_new_functionality():
    """Verificar que la nueva funcionalidad esté correctamente implementada"""
    print("\n" + "="*70)
    print("TEST 4: NUEVA FUNCIONALIDAD")
    print("="*70)
    
    try:
        # Test 1: Nuevo router OTP
        from app.routes.customer_preferences_otp import router as otp_router
        print(f"✅ Router OTP creado - {len(otp_router.routes)} rutas")
        
        # Test 2: Schemas
        from app.routes.customer_preferences_otp import (
            PreferencesOTPRequest,
            PreferencesOTPResponse,
            PreferencesOTPVerifyRequest,
            PreferencesOTPVerifyResponse,
            SendLinkRequest,
            SendLinkResponse
        )
        print("✅ Schemas de OTP definidos")
        
        # Test 3: Verificar que las rutas estén registradas
        route_paths = [r.path for r in otp_router.routes]
        expected_paths = [
            "/api/customer/preferences-otp/request",
            "/api/customer/preferences-otp/verify",
            "/api/customer/preferences-otp/send-link"
        ]
        
        for path in expected_paths:
            if path in route_paths:
                print(f"✅ Ruta registrada: {path}")
            else:
                print(f"❌ Ruta NO registrada: {path}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error en nueva funcionalidad: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_templates():
    """Verificar que los templates existan"""
    print("\n" + "="*70)
    print("TEST 5: TEMPLATES")
    print("="*70)
    
    import os
    
    templates = {
        "customer/verify.html": "NUEVO",
        "customer/preferences.html": "EXISTENTE",
        "customers/manage.html": "MODIFICADO",
    }
    
    all_ok = True
    for template, status in templates.items():
        path = f"src/templates/{template}"
        exists = os.path.exists(path)
        icon = "✅" if exists else "❌"
        print(f"{icon} {template} - {status}")
        if not exists:
            all_ok = False
    
    return all_ok


def test_no_conflicts():
    """Verificar que no haya conflictos con rutas existentes"""
    print("\n" + "="*70)
    print("TEST 6: VERIFICACIÓN DE CONFLICTOS")
    print("="*70)
    
    from app.config_routes import PUBLIC_ROUTES, API_PUBLIC_ROUTES
    
    # Verificar que no haya duplicados
    print(f"Total rutas HTML públicas: {len(PUBLIC_ROUTES)}")
    print(f"Total rutas API públicas: {len(API_PUBLIC_ROUTES)}")
    
    # Verificar rutas específicas
    conflicts = []
    
    # La ruta /customer/preferences ya existía y debe seguir siendo pública
    if "/customer/preferences" not in PUBLIC_ROUTES:
        conflicts.append("/customer/preferences no está en PUBLIC_ROUTES")
    
    # La nueva ruta /customer/verify debe ser pública
    if "/customer/verify" not in PUBLIC_ROUTES:
        conflicts.append("/customer/verify no está en PUBLIC_ROUTES")
    
    # Las nuevas rutas API deben ser públicas
    new_api_routes = [
        "/api/customer/preferences-otp/request",
        "/api/customer/preferences-otp/verify",
        "/api/customer/preferences-otp/send-link",
    ]
    
    for route in new_api_routes:
        if route not in API_PUBLIC_ROUTES:
            conflicts.append(f"{route} no está en API_PUBLIC_ROUTES")
    
    if conflicts:
        print("❌ Conflictos encontrados:")
        for conflict in conflicts:
            print(f"   - {conflict}")
        return False
    else:
        print("✅ No se encontraron conflictos")
        return True


def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*70)
    print("PRUEBAS DE IMPLEMENTACIÓN OTP PARA PREFERENCIAS")
    print("="*70)
    print()
    
    results = {
        "Imports": test_imports(),
        "Configuración de Rutas": test_routes_configuration(),
        "Funcionalidades Existentes": test_existing_functionality(),
        "Nueva Funcionalidad": test_new_functionality(),
        "Templates": test_templates(),
        "Verificación de Conflictos": test_no_conflicts(),
    }
    
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("="*70)
        print()
        print("La implementación está lista para usar:")
        print("1. Reinicia el servidor: docker compose restart")
        print("2. Prueba la nueva vista: https://staging.jemavi.co/customer/verify")
        print("3. Verifica el botón morado en: https://staging.jemavi.co/customers/manage")
        print()
        return 0
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("="*70)
        print()
        print("Revisa los errores arriba y corrige antes de desplegar.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
