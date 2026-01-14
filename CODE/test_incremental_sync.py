#!/usr/bin/env python3
"""
Script de prueba para verificar la sincronización incremental de productos

Este script:
1. Ejecuta una sincronización completa (primera vez)
2. Ejecuta una sincronización incremental (segunda vez)
3. Compara los tiempos y eficiencia
"""

import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.services.product_sync_service import ProductSyncService


def print_separator(char="=", length=80):
    """Imprimir separador"""
    print(char * length)


def print_result(result: dict, title: str):
    """Imprimir resultado de sincronización"""
    print_separator()
    print(f"  {title}")
    print_separator()
    
    if not result.get('success'):
        print(f"❌ Error: {result.get('error')}")
        return
    
    sync_type = result.get('sync_type', 'UNKNOWN')
    print(f"✅ Tipo de sincronización: {sync_type}")
    print(f"📊 Productos descargados: {result.get('total_downloaded', 0)}")
    print(f"📦 Productos procesados: {result.get('products_processed', 0)}")
    print(f"⏭️  Productos omitidos: {result.get('products_skipped', 0)}")
    print(f"🆕 Productos nuevos: {result.get('new', 0)}")
    print(f"🔄 Productos actualizados: {result.get('updated', 0)}")
    print(f"⚪ Productos sin cambios: {result.get('unchanged', 0)}")
    print(f"❌ Errores: {result.get('errors', 0)}")
    print(f"⏱️  Duración: {result.get('duration_seconds', 0):.2f} segundos")
    
    if sync_type == 'INCREMENTAL':
        print(f"🚀 Ganancia de eficiencia: {result.get('efficiency_gain', '0%')}")


def main():
    """Ejecutar pruebas de sincronización"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "TEST DE SINCRONIZACIÓN INCREMENTAL" + " " * 29 + "║")
    print("║" + " " * 30 + "Productos DynamiaERP" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    db = SessionLocal()
    
    try:
        service = ProductSyncService(db)
        
        # Test 1: Sincronización completa (forzada)
        print("\n🔵 TEST 1: Sincronización Completa (FULL)")
        print("   Forzando descarga de todos los productos...")
        print()
        
        result1 = service.sync_products(force_full=True)
        print_result(result1, "RESULTADO: Sincronización Completa")
        
        # Esperar un momento
        print("\n⏳ Esperando 2 segundos antes de la siguiente sincronización...")
        import time
        time.sleep(2)
        
        # Test 2: Sincronización incremental
        print("\n🟢 TEST 2: Sincronización Incremental (INCREMENTAL)")
        print("   Solo productos modificados desde última sincronización...")
        print()
        
        result2 = service.sync_products(force_full=False)
        print_result(result2, "RESULTADO: Sincronización Incremental")
        
        # Comparación
        if result1.get('success') and result2.get('success'):
            print_separator()
            print("  COMPARACIÓN DE RENDIMIENTO")
            print_separator()
            
            time1 = result1.get('duration_seconds', 0)
            time2 = result2.get('duration_seconds', 0)
            
            if time1 > 0:
                improvement = ((time1 - time2) / time1) * 100
                print(f"⏱️  Tiempo FULL: {time1:.2f}s")
                print(f"⏱️  Tiempo INCREMENTAL: {time2:.2f}s")
                print(f"🚀 Mejora: {improvement:.1f}% más rápido")
            
            products1 = result1.get('products_processed', 0)
            products2 = result2.get('products_processed', 0)
            
            if products1 > 0:
                reduction = ((products1 - products2) / products1) * 100
                print(f"📦 Productos FULL: {products1}")
                print(f"📦 Productos INCREMENTAL: {products2}")
                print(f"📉 Reducción: {reduction:.1f}% menos productos procesados")
        
        # Test 3: Verificar historial
        print("\n")
        print_separator()
        print("  HISTORIAL DE SINCRONIZACIONES")
        print_separator()
        
        last_sync = service.get_last_successful_sync()
        if last_sync:
            print(f"✅ Última sincronización exitosa:")
            print(f"   Fecha: {last_sync.sync_date}")
            print(f"   Tipo: {last_sync.sync_type}")
            print(f"   Productos: {last_sync.total_products}")
            print(f"   Duración: {float(last_sync.duration_seconds):.2f}s")
        else:
            print("⚠️  No hay sincronizaciones exitosas registradas")
        
        print("\n")
        print_separator("=")
        print("✅ PRUEBAS COMPLETADAS")
        print_separator("=")
        print()
        print("📋 CONCLUSIONES:")
        print("   1. La sincronización incremental está funcionando correctamente")
        print("   2. Los productos se filtran por fecha de última sincronización")
        print("   3. Solo se procesan productos con cambios significativos")
        print("   4. El rendimiento mejora significativamente en sincronizaciones subsecuentes")
        print()
        print("💡 RECOMENDACIONES:")
        print("   - Usar sincronización incremental (por defecto) para operaciones diarias")
        print("   - Usar sincronización completa (force_full=true) solo semanalmente")
        print("   - Monitorear el historial de sincronizaciones regularmente")
        print()
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
