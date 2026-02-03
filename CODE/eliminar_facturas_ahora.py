#!/usr/bin/env python3
"""
Script simple para eliminar TODAS las facturas
Ejecutar: python3 CODE/eliminar_facturas_ahora.py
"""
import psycopg2
from psycopg2 import sql

# Credenciales de la base de datos
DB_CONFIG = {
    'host': 'ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com',
    'port': 5432,
    'database': 'paqueteria_staging',
    'user': 'jveyes',
    'password': 'a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'
}

def main():
    print("\n" + "="*80)
    print("⚠️  ELIMINACIÓN DE TODAS LAS FACTURAS")
    print("="*80)
    
    # Confirmación
    respuesta = input("\n¿Eliminar TODAS las facturas? (escribe 'SI'): ")
    if respuesta != 'SI':
        print("❌ Cancelado")
        return
    
    try:
        # Conectar
        print("\n🔄 Conectando a la base de datos...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Ver estadísticas antes
        cursor.execute("SELECT COUNT(*) FROM invoices_v2")
        total_facturas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoice_products_v2")
        total_productos = cursor.fetchone()[0]
        
        print(f"\n📊 Encontradas:")
        print(f"  • {total_facturas} facturas")
        print(f"  • {total_productos} productos")
        
        if total_facturas == 0:
            print("\n✅ No hay facturas para eliminar")
            conn.close()
            return
        
        # Eliminar
        print("\n🗑️  Eliminando productos...")
        cursor.execute("DELETE FROM invoice_products_v2")
        productos_eliminados = cursor.rowcount
        
        print("🗑️  Eliminando facturas...")
        cursor.execute("DELETE FROM invoices_v2")
        facturas_eliminadas = cursor.rowcount
        
        # Commit
        conn.commit()
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM invoices_v2")
        restantes = cursor.fetchone()[0]
        
        print("\n" + "="*80)
        print("✅ COMPLETADO")
        print("="*80)
        print(f"\n📊 Eliminadas:")
        print(f"  • {facturas_eliminadas} facturas")
        print(f"  • {productos_eliminados} productos")
        print(f"  • Facturas restantes: {restantes}")
        
        cursor.close()
        conn.close()
        
        print("\n⚠️  NOTA: Los archivos en S3 NO fueron eliminados")
        print("Para eliminar archivos S3, usa: python3 CODE/eliminar_todas_facturas.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
