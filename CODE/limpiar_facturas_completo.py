#!/usr/bin/env python3
"""
Script para limpiar TODAS las facturas y productos de la base de datos
Mantiene usuarios y configuración
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from app.config import settings

def limpiar_facturas():
    """Elimina todas las facturas y productos"""
    
    print("=" * 100)
    print("🗑️  LIMPIEZA COMPLETA DE FACTURAS")
    print("=" * 100)
    print()
    
    # Conectar a la base de datos
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Contar registros antes
        print("📊 Contando registros actuales...")
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2"))
        productos_count = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoices_v2"))
        facturas_count = result.scalar()
        
        print(f"   Productos actuales: {productos_count}")
        print(f"   Facturas actuales: {facturas_count}")
        print()
        
        if facturas_count == 0 and productos_count == 0:
            print("✅ No hay facturas ni productos para eliminar")
            return
        
        # Confirmar
        print("⚠️  ADVERTENCIA: Esta acción eliminará:")
        print(f"   - {facturas_count} facturas")
        print(f"   - {productos_count} productos")
        print()
        print("   Los usuarios y configuración NO se eliminarán")
        print()
        
        respuesta = input("¿Deseas continuar? (si/no): ").strip().lower()
        
        if respuesta not in ['si', 's', 'yes', 'y']:
            print("❌ Operación cancelada")
            return
        
        print()
        print("🗑️  Eliminando registros...")
        
        # Eliminar productos primero (foreign key)
        conn.execute(text("DELETE FROM invoice_products_v2"))
        conn.commit()
        print("   ✅ Productos eliminados")
        
        # Eliminar facturas
        conn.execute(text("DELETE FROM invoices_v2"))
        conn.commit()
        print("   ✅ Facturas eliminadas")
        
        # Verificar
        result = conn.execute(text("SELECT COUNT(*) FROM invoice_products_v2"))
        productos_final = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM invoices_v2"))
        facturas_final = result.scalar()
        
        print()
        print("=" * 100)
        print("✅ LIMPIEZA COMPLETADA")
        print("=" * 100)
        print(f"   Productos restantes: {productos_final}")
        print(f"   Facturas restantes: {facturas_final}")
        print()
        print("🎯 Ahora puedes subir las facturas nuevamente desde la interfaz web")
        print("   URL: http://localhost:8000/invoices/upload")
        print()

if __name__ == '__main__':
    try:
        limpiar_facturas()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
