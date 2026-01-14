#!/usr/bin/env python3
"""
Script de prueba para validar el endpoint /api/inventario/items/ultimos
de la API de DynamiaERP

Este script verifica:
1. Si el endpoint existe y responde
2. Qué parámetros acepta
3. Formato de la respuesta
4. Campos de fecha disponibles
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
DYNAMIA_API_URL = os.getenv('DYNAMIA_API_URL', 'https://api.dynamiaerp.co')
DYNAMIA_TOKEN = os.getenv('DYNAMIA_TOKEN')

def get_headers():
    """Obtener headers con autenticación"""
    return {
        "Authorization": f"Bearer {DYNAMIA_TOKEN}",
        "Content-Type": "application/json"
    }

def test_endpoint_exists():
    """Probar si el endpoint /ultimos existe"""
    print("=" * 80)
    print("TEST 1: Verificar existencia del endpoint")
    print("=" * 80)
    
    url = f"{DYNAMIA_API_URL}/api/inventario/items/ultimos"
    
    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        
        print(f"✅ Endpoint responde")
        print(f"   Status Code: {response.status_code}")
        print(f"   URL: {url}")
        
        if response.status_code == 200:
            print(f"   ✅ Endpoint funciona correctamente")
            return True, response.json()
        elif response.status_code == 404:
            print(f"   ❌ Endpoint no existe (404)")
            return False, None
        else:
            print(f"   ⚠️  Respuesta inesperada: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return False, None

def test_with_limit():
    """Probar endpoint con parámetro limit"""
    print("\n" + "=" * 80)
    print("TEST 2: Probar con parámetro 'limit'")
    print("=" * 80)
    
    url = f"{DYNAMIA_API_URL}/api/inventario/items/ultimos"
    
    for limit in [5, 10, 50]:
        try:
            response = requests.get(
                url, 
                headers=get_headers(), 
                params={'limit': limit},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', [])
                print(f"✅ limit={limit}: Obtenidos {len(items)} productos")
            else:
                print(f"⚠️  limit={limit}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ limit={limit}: Error - {e}")

def test_with_date_filters():
    """Probar endpoint con filtros de fecha"""
    print("\n" + "=" * 80)
    print("TEST 3: Probar con filtros de fecha")
    print("=" * 80)
    
    url = f"{DYNAMIA_API_URL}/api/inventario/items/ultimos"
    
    # Probar diferentes formatos de fecha
    date_params = [
        ('desde', (datetime.now() - timedelta(days=7)).isoformat()),
        ('desde', (datetime.now() - timedelta(days=30)).isoformat()),
        ('fechaDesde', (datetime.now() - timedelta(days=7)).isoformat()),
        ('startDate', (datetime.now() - timedelta(days=7)).isoformat()),
        ('after', (datetime.now() - timedelta(days=7)).isoformat()),
    ]
    
    for param_name, param_value in date_params:
        try:
            response = requests.get(
                url,
                headers=get_headers(),
                params={param_name: param_value, 'limit': 10},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', [])
                print(f"✅ {param_name}={param_value[:10]}: {len(items)} productos")
            else:
                print(f"⚠️  {param_name}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {param_name}: Error - {e}")

def analyze_response_structure(data):
    """Analizar estructura de la respuesta"""
    print("\n" + "=" * 80)
    print("TEST 4: Analizar estructura de respuesta")
    print("=" * 80)
    
    if not data:
        print("❌ No hay datos para analizar")
        return
    
    print(f"Claves principales: {list(data.keys())}")
    
    items = data.get('data', [])
    if not items:
        print("⚠️  No hay items en la respuesta")
        return
    
    print(f"\n✅ Total de items: {len(items)}")
    
    # Analizar primer item
    first_item = items[0]
    print(f"\nCampos del primer item ({len(first_item)} campos):")
    
    # Campos de fecha
    date_fields = [k for k in first_item.keys() if 'date' in k.lower() or 'fecha' in k.lower() or 'time' in k.lower() or 'update' in k.lower() or 'creation' in k.lower()]
    
    print(f"\n📅 Campos de fecha encontrados ({len(date_fields)}):")
    for field in date_fields:
        value = first_item.get(field)
        print(f"   - {field}: {value}")
    
    # Campos importantes
    important_fields = ['id', 'codigo', 'nombre', 'precioVenta', 'existenciasTotales', 'activo']
    print(f"\n📊 Campos importantes:")
    for field in important_fields:
        if field in first_item:
            value = first_item.get(field)
            print(f"   - {field}: {value}")

def compare_with_all_items():
    """Comparar endpoint /ultimos con /items"""
    print("\n" + "=" * 80)
    print("TEST 5: Comparar /ultimos vs /items")
    print("=" * 80)
    
    try:
        # Obtener de /ultimos
        response_ultimos = requests.get(
            f"{DYNAMIA_API_URL}/api/inventario/items/ultimos",
            headers=get_headers(),
            params={'limit': 10},
            timeout=30
        )
        
        # Obtener de /items
        response_all = requests.get(
            f"{DYNAMIA_API_URL}/api/inventario/items",
            headers=get_headers(),
            timeout=30
        )
        
        if response_ultimos.status_code == 200 and response_all.status_code == 200:
            data_ultimos = response_ultimos.json()
            data_all = response_all.json()
            
            items_ultimos = data_ultimos.get('data', [])
            items_all = data_all.get('data', [])
            
            print(f"✅ /ultimos: {len(items_ultimos)} productos")
            print(f"✅ /items: {len(items_all)} productos")
            print(f"📊 Diferencia: {len(items_all) - len(items_ultimos)} productos")
            
            # Verificar si los campos son iguales
            if items_ultimos and items_all:
                fields_ultimos = set(items_ultimos[0].keys())
                fields_all = set(items_all[0].keys())
                
                if fields_ultimos == fields_all:
                    print(f"✅ Estructura de campos idéntica")
                else:
                    print(f"⚠️  Diferencias en campos:")
                    only_ultimos = fields_ultimos - fields_all
                    only_all = fields_all - fields_ultimos
                    if only_ultimos:
                        print(f"   Solo en /ultimos: {only_ultimos}")
                    if only_all:
                        print(f"   Solo en /items: {only_all}")
        else:
            print(f"⚠️  Error en comparación")
            print(f"   /ultimos: {response_ultimos.status_code}")
            print(f"   /items: {response_all.status_code}")
            
    except Exception as e:
        print(f"❌ Error en comparación: {e}")

def test_pagination():
    """Probar paginación"""
    print("\n" + "=" * 80)
    print("TEST 6: Probar paginación")
    print("=" * 80)
    
    url = f"{DYNAMIA_API_URL}/api/inventario/items/ultimos"
    
    # Probar diferentes parámetros de paginación
    pagination_params = [
        {'page': 0, 'size': 10},
        {'page': 1, 'size': 10},
        {'offset': 0, 'limit': 10},
        {'offset': 10, 'limit': 10},
        {'skip': 0, 'take': 10},
    ]
    
    for params in pagination_params:
        try:
            response = requests.get(
                url,
                headers=get_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', [])
                print(f"✅ {params}: {len(items)} productos")
            else:
                print(f"⚠️  {params}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {params}: Error - {e}")

def save_sample_response(data):
    """Guardar respuesta de ejemplo"""
    print("\n" + "=" * 80)
    print("Guardando respuesta de ejemplo...")
    print("=" * 80)
    
    if not data:
        print("❌ No hay datos para guardar")
        return
    
    filename = f"dynamia_ultimos_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Respuesta guardada en: {filename}")
    except Exception as e:
        print(f"❌ Error guardando respuesta: {e}")

def main():
    """Ejecutar todos los tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TEST DE ENDPOINT /ultimos" + " " * 33 + "║")
    print("║" + " " * 25 + "DynamiaERP API" + " " * 39 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    if not DYNAMIA_TOKEN:
        print("❌ ERROR: DYNAMIA_TOKEN no configurado en .env")
        return
    
    print(f"🔧 Configuración:")
    print(f"   API URL: {DYNAMIA_API_URL}")
    print(f"   Token: {DYNAMIA_TOKEN[:20]}...")
    print()
    
    # Test 1: Verificar existencia
    exists, data = test_endpoint_exists()
    
    if not exists:
        print("\n" + "=" * 80)
        print("❌ CONCLUSIÓN: El endpoint /ultimos NO está disponible")
        print("=" * 80)
        print("\n💡 ALTERNATIVAS:")
        print("   1. Usar /api/inventario/items con filtros de fecha")
        print("   2. Implementar caché local con timestamps")
        print("   3. Consultar documentación de DynamiaERP")
        print("   4. Contactar soporte: devteam@dynamiasoluciones.com")
        return
    
    # Tests adicionales si el endpoint existe
    test_with_limit()
    test_with_date_filters()
    analyze_response_structure(data)
    compare_with_all_items()
    test_pagination()
    save_sample_response(data)
    
    # Conclusión
    print("\n" + "=" * 80)
    print("✅ CONCLUSIÓN: Tests completados")
    print("=" * 80)
    print("\n📋 PRÓXIMOS PASOS:")
    print("   1. Revisar archivo JSON generado con respuesta completa")
    print("   2. Identificar parámetros que funcionan")
    print("   3. Implementar sincronización incremental")
    print("   4. Actualizar product_sync_service.py")

if __name__ == "__main__":
    main()
