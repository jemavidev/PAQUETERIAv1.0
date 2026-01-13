#!/usr/bin/env python3
"""
Script de prueba para sincronización de productos
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.database import SessionLocal
from app.services.product_sync_service import ProductSyncService
from app.models.product import Product

def test_sync():
    """Probar sincronización de productos"""
    print("=" * 60)
    print("PRUEBA DE SINCRONIZACIÓN DE PRODUCTOS")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Verificar productos existentes
        count_before = db.query(Product).count()
        print(f"\n📊 Productos en BD antes de sincronizar: {count_before}")
        
        # Ejecutar sincronización
        print("\n🔄 Iniciando sincronización desde DynamiaERP...")
        service = ProductSyncService(db)
        result = service.sync_products()
        
        # Mostrar resultados
        print("\n✅ Sincronización completada:")
        print(f"   - Total procesados: {result['total']}")
        print(f"   - Nuevos: {result['new']}")
        print(f"   - Actualizados: {result['updated']}")
        print(f"   - Errores: {result['errors']}")
        print(f"   - Duración: {result['duration_seconds']:.2f} segundos")
        
        # Verificar productos después
        count_after = db.query(Product).count()
        print(f"\n📊 Productos en BD después de sincronizar: {count_after}")
        
        # Mostrar algunos productos de ejemplo
        print("\n📦 Primeros 5 productos:")
        products = db.query(Product).limit(5).all()
        for p in products:
            print(f"   - {p.codigo}: {p.nombre} (${p.precio_venta})")
        
        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_sync()
