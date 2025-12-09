#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar configuración de rutas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.config_routes import is_public_route, is_api_public_route, PUBLIC_ROUTES, API_PUBLIC_ROUTES

def test_routes():
    """Verificar que las rutas del portal estén configuradas correctamente"""
    
    print("="*60)
    print("DIAGNÓSTICO DE RUTAS - PORTAL DE CLIENTES")
    print("="*60)
    
    # Rutas a verificar
    test_routes = [
        "/customer-portal",
        "/customer-portal/verify",
        "/customer-portal/dashboard",
        "/api/customer-portal/request-otp",
        "/api/customer-portal/verify-otp",
        "/api/customer-portal/me",
        "/api/customer-portal/packages",
    ]
    
    print("\n📋 Verificando rutas HTML:")
    print("-" * 60)
    for route in test_routes[:3]:
        is_public = is_public_route(route)
        status = "✅ PÚBLICA" if is_public else "❌ PROTEGIDA"
        print(f"{status} - {route}")
        if not is_public:
            print(f"   ⚠️  PROBLEMA: Esta ruta debería ser pública!")
    
    print("\n📋 Verificando rutas API:")
    print("-" * 60)
    for route in test_routes[3:]:
        is_public = is_api_public_route(route)
        status = "✅ PÚBLICA" if is_public else "❌ PROTEGIDA"
        print(f"{status} - {route}")
        if not is_public:
            print(f"   ⚠️  PROBLEMA: Esta ruta debería ser pública!")
    
    print("\n📋 Todas las rutas públicas HTML configuradas:")
    print("-" * 60)
    portal_routes = [r for r in PUBLIC_ROUTES if 'customer-portal' in r]
    if portal_routes:
        for route in sorted(portal_routes):
            print(f"  ✅ {route}")
    else:
        print("  ❌ NO HAY RUTAS DEL PORTAL CONFIGURADAS!")
    
    print("\n📋 Todas las rutas API públicas del portal:")
    print("-" * 60)
    portal_api_routes = [r for r in API_PUBLIC_ROUTES if 'customer-portal' in r]
    if portal_api_routes:
        for route in sorted(portal_api_routes):
            print(f"  ✅ {route}")
    else:
        print("  ❌ NO HAY RUTAS API DEL PORTAL CONFIGURADAS!")
    
    print("\n" + "="*60)
    
    # Verificar si hay problemas
    problems = []
    if not is_public_route("/customer-portal"):
        problems.append("/customer-portal no es pública")
    if not is_api_public_route("/api/customer-portal/request-otp"):
        problems.append("/api/customer-portal/request-otp no es pública")
    
    if problems:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for problem in problems:
            print(f"   - {problem}")
        print("\n⚠️  El servidor necesita reiniciarse después de actualizar config_routes.py")
        return False
    else:
        print("✅ TODAS LAS RUTAS ESTÁN CORRECTAMENTE CONFIGURADAS")
        print("\nSi aún hay problemas de redirección:")
        print("1. Reiniciar el servidor: docker-compose restart web")
        print("2. Limpiar caché del navegador")
        print("3. Verificar logs: docker-compose logs -f web | grep customer-portal")
        return True

if __name__ == "__main__":
    success = test_routes()
    sys.exit(0 if success else 1)
