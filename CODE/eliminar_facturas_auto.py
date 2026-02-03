#!/usr/bin/env python3
"""
Script automático para eliminar TODAS las facturas (sin confirmación)
Ejecutar: python3 CODE/eliminar_facturas_auto.py
"""
import psycopg2
import sys

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
    print("⚠️  ELIMINACIÓN AUTOMÁTICA DE TODAS LAS FACTURAS")
    print("="*80)
    
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
            return 0
        
        # Eliminar
        print("\n🗑️  Eliminando productos...")
        cursor.execute("DELETE FROM invoice_products_v2")
        productos_eliminados = cursor.rowcount
        print(f"  ✓ {productos_eliminados} productos eliminados")
        
        print("\n🗑️  Eliminando facturas...")
        cursor.execute("DELETE FROM invoices_v2")
        facturas_eliminadas = cursor.rowcount
        print(f"  ✓ {facturas_eliminadas} facturas eliminadas")
        
        # Commit
        print("\n💾 Guardando cambios...")
        conn.commit()
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM invoices_v2")
        restantes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoice_products_v2")
        productos_restantes = cursor.fetchone()[0]
        
        print("\n" + "="*80)
        print("✅ ELIMINACIÓN COMPLETADA")
        print("="*80)
        print(f"\n📊 Resumen:")
        print(f"  • Facturas eliminadas: {facturas_eliminadas}")
        print(f"  • Productos eliminados: {productos_eliminados}")
        print(f"  • Facturas restantes: {restantes}")
        print(f"  • Productos restantes: {productos_restantes}")
        
        if restantes == 0 and productos_restantes == 0:
            print("\n✅ Base de datos completamente limpia")
        else:
            print(f"\n⚠️  Advertencia: Aún quedan {restantes} facturas y {productos_restantes} productos")
        
        cursor.close()
        conn.close()
        
        print("\n⚠️  NOTA: Los archivos en S3 NO fueron eliminados")
        print("Para eliminar archivos S3, ejecuta el script completo con S3Service")
        
    except psycopg2.Error as e:
        print(f"\n❌ Error de base de datos: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
