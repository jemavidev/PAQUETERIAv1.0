#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba de rendimiento de cache
Versión: 1.0.0
Fecha: 2024-12-18
"""

import sys
import os
import time
import requests
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

def test_cache_performance(base_url: str = "http://localhost:8000"):
    """Probar rendimiento del cache"""
    
    print("=" * 80)
    print("🧪 TEST DE RENDIMIENTO DE CACHE")
    print("=" * 80)
    print(f"URL Base: {base_url}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    results = []
    
    # Test 1: Búsqueda de paquetes
    print("📦 Test 1: Búsqueda de paquetes")
    print("-" * 80)
    
    endpoint = f"{base_url}/api/packages"
    
    # Primera llamada (cache miss)
    start = time.time()
    try:
        response = requests.get(endpoint, timeout=10)
        time_miss = (time.time() - start) * 1000
        print(f"✅ Primera llamada (CACHE MISS): {time_miss:.2f}ms")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        time_miss = 0
    
    # Segunda llamada (cache hit)
    time.sleep(0.5)
    start = time.time()
    try:
        response = requests.get(endpoint, timeout=10)
        time_hit = (time.time() - start) * 1000
        print(f"✅ Segunda llamada (CACHE HIT): {time_hit:.2f}ms")
        print(f"   Status: {response.status_code}")
        
        if time_miss > 0:
            improvement = ((time_miss - time_hit) / time_miss) * 100
            print(f"🚀 Mejora: {improvement:.1f}%")
            results.append({
                'test': 'Búsqueda de paquetes',
                'miss': time_miss,
                'hit': time_hit,
                'improvement': improvement
            })
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Estadísticas de paquetes
    print("📊 Test 2: Estadísticas de paquetes")
    print("-" * 80)
    
    endpoint = f"{base_url}/api/admin/dashboard"
    
    # Primera llamada (cache miss)
    start = time.time()
    try:
        response = requests.get(endpoint, timeout=10)
        time_miss = (time.time() - start) * 1000
        print(f"✅ Primera llamada (CACHE MISS): {time_miss:.2f}ms")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        time_miss = 0
    
    # Segunda llamada (cache hit)
    time.sleep(0.5)
    start = time.time()
    try:
        response = requests.get(endpoint, timeout=10)
        time_hit = (time.time() - start) * 1000
        print(f"✅ Segunda llamada (CACHE HIT): {time_hit:.2f}ms")
        print(f"   Status: {response.status_code}")
        
        if time_miss > 0:
            improvement = ((time_miss - time_hit) / time_miss) * 100
            print(f"🚀 Mejora: {improvement:.1f}%")
            results.append({
                'test': 'Estadísticas de paquetes',
                'miss': time_miss,
                'hit': time_hit,
                'improvement': improvement
            })
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: Búsqueda de clientes
    print("👥 Test 3: Búsqueda de clientes")
    print("-" * 80)
    
    endpoint = f"{base_url}/api/admin/customers"
    
    # Primera llamada (cache miss)
    start = time.time()
    try:
        response = requests.get(endpoint, timeout=10)
        time_miss = (time.time() - start) * 1000
        print(f"✅ Primera llamada (CACHE MISS): {time_miss:.2f}ms")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        time_miss = 0
    
    # Segunda llamada (cache hit)
    time.sleep(0.5)
    start = time.time()
    try:
        response = requests.get(endpoint, timeout=10)
        time_hit = (time.time() - start) * 1000
        print(f"✅ Segunda llamada (CACHE HIT): {time_hit:.2f}ms")
        print(f"   Status: {response.status_code}")
        
        if time_miss > 0:
            improvement = ((time_miss - time_hit) / time_miss) * 100
            print(f"🚀 Mejora: {improvement:.1f}%")
            results.append({
                'test': 'Búsqueda de clientes',
                'miss': time_miss,
                'hit': time_hit,
                'improvement': improvement
            })
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Resumen
    print("=" * 80)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 80)
    
    if results:
        print(f"\n{'Test':<30} {'Cache Miss':<15} {'Cache Hit':<15} {'Mejora':<10}")
        print("-" * 80)
        
        total_improvement = 0
        for result in results:
            print(f"{result['test']:<30} {result['miss']:>10.2f}ms {result['hit']:>10.2f}ms {result['improvement']:>8.1f}%")
            total_improvement += result['improvement']
        
        avg_improvement = total_improvement / len(results)
        print("-" * 80)
        print(f"{'PROMEDIO':<30} {'':<15} {'':<15} {avg_improvement:>8.1f}%")
        print()
        
        # Evaluación
        if avg_improvement >= 80:
            print("✅ EXCELENTE: Cache funcionando óptimamente (>80% mejora)")
        elif avg_improvement >= 50:
            print("✅ BUENO: Cache funcionando bien (50-80% mejora)")
        elif avg_improvement >= 30:
            print("⚠️  ACEPTABLE: Cache funcionando (30-50% mejora)")
        else:
            print("❌ PROBLEMA: Cache no está mejorando significativamente (<30% mejora)")
    else:
        print("❌ No se pudieron obtener resultados")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Probar rendimiento del cache')
    parser.add_argument('--url', default='http://localhost:8000', help='URL base del servidor')
    
    args = parser.parse_args()
    
    test_cache_performance(args.url)
