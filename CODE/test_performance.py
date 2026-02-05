#!/usr/bin/env python3
"""
Test de rendimiento del endpoint de facturas
"""
import requests
import time

BASE_URL = "http://localhost:8000"

print("="*80)
print("⚡ TEST DE RENDIMIENTO - SISTEMA DE FACTURAS")
print("="*80)

tests = [
    ("Listar 25 facturas (página 1)", f"{BASE_URL}/api/v2/invoices/facturas?skip=0&limit=25"),
    ("Listar 25 facturas (página 2)", f"{BASE_URL}/api/v2/invoices/facturas?skip=25&limit=25"),
    ("Buscar por 'Venep'", f"{BASE_URL}/api/v2/invoices/facturas?skip=0&limit=25&search=Venep"),
    ("Buscar por 'MAF'", f"{BASE_URL}/api/v2/invoices/facturas?skip=0&limit=25&search=MAF"),
    ("Filtrar por estado", f"{BASE_URL}/api/v2/invoices/facturas?skip=0&limit=25&estado=sin_dian"),
]

results = []

for test_name, url in tests:
    print(f"\n🧪 {test_name}")
    print(f"   URL: {url}")
    
    # Hacer 3 peticiones para obtener promedio
    times = []
    for i in range(3):
        start = time.time()
        try:
            response = requests.get(url, timeout=10)
            elapsed = (time.time() - start) * 1000  # Convertir a ms
            times.append(elapsed)
            
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                items = len(data.get('items', []))
                print(f"   Intento {i+1}: {elapsed:.0f}ms (total: {total}, items: {items})")
            else:
                print(f"   Intento {i+1}: ERROR {response.status_code}")
        except Exception as e:
            print(f"   Intento {i+1}: ERROR - {e}")
            times.append(10000)  # 10 segundos como penalización
    
    # Calcular promedio
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"   📊 Promedio: {avg_time:.0f}ms | Min: {min_time:.0f}ms | Max: {max_time:.0f}ms")
    
    # Evaluar rendimiento
    if avg_time < 300:
        status = "✅ EXCELENTE"
    elif avg_time < 500:
        status = "✅ BUENO"
    elif avg_time < 1000:
        status = "⚠️ ACEPTABLE"
    else:
        status = "❌ LENTO"
    
    print(f"   {status}")
    
    results.append({
        'test': test_name,
        'avg': avg_time,
        'min': min_time,
        'max': max_time,
        'status': status
    })

# Resumen final
print("\n" + "="*80)
print("📊 RESUMEN DE RENDIMIENTO")
print("="*80)

for result in results:
    print(f"\n{result['test']}")
    print(f"  Promedio: {result['avg']:.0f}ms | Min: {result['min']:.0f}ms | Max: {result['max']:.0f}ms")
    print(f"  {result['status']}")

# Promedio general
avg_general = sum(r['avg'] for r in results) / len(results)
print(f"\n{'='*80}")
print(f"📈 PROMEDIO GENERAL: {avg_general:.0f}ms")

if avg_general < 300:
    print("✅ RENDIMIENTO EXCELENTE - Sistema optimizado correctamente")
elif avg_general < 500:
    print("✅ RENDIMIENTO BUENO - Sistema funcionando bien")
elif avg_general < 1000:
    print("⚠️ RENDIMIENTO ACEPTABLE - Considerar más optimizaciones")
else:
    print("❌ RENDIMIENTO LENTO - Requiere optimización urgente")

print("="*80)
