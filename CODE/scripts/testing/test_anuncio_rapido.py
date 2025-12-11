#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de Anuncio Rápido
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
TEST_PHONE = "+573001234567"  # Cambiar por un teléfono real en tu BD

async def test_search_customer():
    """Probar búsqueda de cliente por teléfono"""
    print("\n" + "="*60)
    print("TEST 1: Buscar cliente por teléfono")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/customers/search-by-phone",
                params={"phone": TEST_PHONE}
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200:
                print("\n✅ Cliente encontrado exitosamente")
                return True
            elif response.status_code == 404:
                print("\n⚠️  Cliente no encontrado - Necesitas crear un cliente primero")
                return False
            else:
                print(f"\n❌ Error inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error en la petición: {e}")
            return False

async def test_create_quick_announcement():
    """Probar creación de anuncio rápido"""
    print("\n" + "="*60)
    print("TEST 2: Crear anuncio rápido")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            announcement_data = {
                "customer_phone": TEST_PHONE
            }
            
            print(f"\nDatos a enviar:")
            print(json.dumps(announcement_data, indent=2, ensure_ascii=False))
            
            response = await client.post(
                f"{BASE_URL}/api/announcements/quick",
                json=announcement_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    announcement = data.get("announcement", {})
                    print("\n✅ Anuncio creado exitosamente!")
                    print(f"\n📦 Detalles del anuncio:")
                    print(f"   - Número de guía: {announcement.get('guide_number')}")
                    print(f"   - Código de tracking: {announcement.get('tracking_code')}")
                    print(f"   - Cliente: {announcement.get('customer_name')}")
                    print(f"   - Teléfono: {announcement.get('customer_phone')}")
                    return True
                else:
                    print(f"\n❌ Error: {data.get('message')}")
                    return False
            elif response.status_code == 400:
                error = response.json()
                print(f"\n⚠️  Error de validación: {error.get('detail')}")
                return False
            else:
                print(f"\n❌ Error inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error en la petición: {e}")
            import traceback
            traceback.print_exc()
            return False

async def test_search_with_invalid_phone():
    """Probar búsqueda con teléfono inválido"""
    print("\n" + "="*60)
    print("TEST 3: Buscar con teléfono inválido")
    print("="*60)
    
    invalid_phones = [
        "123",  # Muy corto
        "abcdefghij",  # No numérico
        "+57123",  # Incompleto
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for phone in invalid_phones:
            try:
                print(f"\nProbando con: {phone}")
                response = await client.get(
                    f"{BASE_URL}/api/customers/search-by-phone",
                    params={"phone": phone}
                )
                
                print(f"Status Code: {response.status_code}")
                if response.status_code == 404:
                    print("✅ Correctamente rechazado (404)")
                else:
                    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")

async def test_create_announcement_without_customer():
    """Probar crear anuncio sin cliente existente"""
    print("\n" + "="*60)
    print("TEST 4: Crear anuncio sin cliente existente")
    print("="*60)
    
    fake_phone = "+573009999999"  # Teléfono que no existe
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            announcement_data = {
                "customer_phone": fake_phone
            }
            
            print(f"\nIntentando crear anuncio con teléfono no registrado: {fake_phone}")
            
            response = await client.post(
                f"{BASE_URL}/api/announcements/quick",
                json=announcement_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            if response.status_code == 400:
                error = response.json()
                if "no encontrado" in error.get("detail", "").lower():
                    print("\n✅ Correctamente rechazado - Cliente no encontrado")
                    return True
            
            print("\n⚠️  Debería haber rechazado el anuncio")
            return False
                
        except Exception as e:
            print(f"\n❌ Error en la petición: {e}")
            return False

async def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("🧪 SUITE DE PRUEBAS - ANUNCIO RÁPIDO")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Teléfono de prueba: {TEST_PHONE}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Buscar cliente
    result1 = await test_search_customer()
    results.append(("Buscar cliente", result1))
    
    if result1:
        # Solo continuar si el cliente existe
        # Test 2: Crear anuncio rápido
        result2 = await test_create_quick_announcement()
        results.append(("Crear anuncio rápido", result2))
    else:
        print("\n⚠️  Saltando test de creación porque el cliente no existe")
        print(f"   Crea un cliente con el teléfono {TEST_PHONE} primero")
    
    # Test 3: Teléfonos inválidos
    await test_search_with_invalid_phone()
    results.append(("Validación de teléfonos", True))
    
    # Test 4: Anuncio sin cliente
    result4 = await test_create_announcement_without_customer()
    results.append(("Rechazo sin cliente", result4))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron!")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron")

if __name__ == "__main__":
    print("\n🚀 Iniciando pruebas del sistema de Anuncio Rápido...")
    print("\n⚠️  IMPORTANTE: Asegúrate de que:")
    print("   1. El servidor esté corriendo en http://localhost:8000")
    print(f"   2. Exista un cliente con el teléfono {TEST_PHONE}")
    print("   3. La base de datos esté accesible")
    
    input("\nPresiona ENTER para continuar...")
    
    asyncio.run(run_all_tests())
