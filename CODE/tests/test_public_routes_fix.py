#!/usr/bin/env python3
"""
Script de prueba para verificar que las rutas de tracking son públicas
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'CODE', 'src'))

from app.config_routes import is_api_public_route, API_PUBLIC_ROUTES

def test_tracking_routes():
    """Probar que las rutas de tracking son públicas"""
    
    print("=" * 60)
    print("PRUEBA DE RUTAS PÚBLICAS DE TRACKING")
    print("=" * 60)
    
    # Rutas a probar
    test_routes = [
        "/api/messages/tracking/IMV6",
        "/api/messages/tracking/ABC123",
        "/api/messages/tracking",
        "/api/messages/check-tracking-inquiries",
        "/api/messages/check-tracking-inquiries?package_tracking_code=IMV6",
        "/api/messages/customer-inquiry",
        "/api/messages/check-inquiry-exists",
        "/api/messages/check-inquiry-exists?customer_email=test@example.com",
    ]
    
    print("\n📋 Rutas públicas configuradas:")
    for route in sorted(API_PUBLIC_ROUTES):
        if "tracking" in route or "messages" in route:
            print(f"  ✓ {route}")
    
    print("\n🧪 Probando rutas:")
    all_passed = True
    
    for route in test_routes:
        is_public = is_api_public_route(route)
        status = "✅ PÚBLICO" if is_public else "❌ PROTEGIDO"
        print(f"  {status}: {route}")
        
        if not is_public:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("Las rutas de tracking son públicas correctamente")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("Revisa la configuración de rutas públicas")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = test_tracking_routes()
    sys.exit(0 if success else 1)
