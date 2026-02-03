#!/usr/bin/env python3
"""
Script para eliminar TODAS las facturas y sus archivos asociados
ADVERTENCIA: Esta operación es IRREVERSIBLE
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.invoice_v2 import InvoiceV2, InvoiceProductV2
from app.database import get_database_url
from app.services.s3_service import S3Service

def eliminar_todas_facturas():
    """
    Elimina TODAS las facturas de la base de datos y sus archivos de S3
    """
    print("\n" + "="*80)
    print("⚠️  ADVERTENCIA: ELIMINACIÓN TOTAL DE FACTURAS")
    print("="*80)
    print("\nEsta operación eliminará:")
    print("  • Todas las facturas de la base de datos")
    print("  • Todos los productos asociados")
    print("  • Todos los archivos PDF en S3")
    print("\n⚠️  ESTA OPERACIÓN ES IRREVERSIBLE ⚠️")
    print("\n" + "="*80)
    
    # Confirmación 1
    respuesta1 = input("\n¿Estás seguro de que quieres continuar? (escribe 'SI' en mayúsculas): ")
    if respuesta1 != 'SI':
        print("\n❌ Operación cancelada")
        return
    
    # Confirmación 2
    respuesta2 = input("\n¿REALMENTE quieres eliminar TODAS las facturas? (escribe 'ELIMINAR TODO'): ")
    if respuesta2 != 'ELIMINAR TODO':
        print("\n❌ Operación cancelada")
        return
    
    print("\n🔄 Iniciando eliminación...\n")
    
    # Conectar a la base de datos
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Inicializar S3 service
    try:
        s3_service = S3Service()
        s3_available = True
        print("✅ Servicio S3 disponible")
    except Exception as e:
        s3_service = None
        s3_available = False
        print(f"⚠️  Servicio S3 no disponible: {e}")
    
    try:
        # Contar facturas
        total_facturas = session.query(InvoiceV2).count()
        total_productos = session.query(InvoiceProductV2).count()
        
        print(f"\n📊 Estadísticas:")
        print(f"  • Facturas a eliminar: {total_facturas}")
        print(f"  • Productos a eliminar: {total_productos}")
        
        if total_facturas == 0:
            print("\n✅ No hay facturas para eliminar")
            return
        
        # Obtener todas las facturas
        facturas = session.query(InvoiceV2).all()
        
        archivos_s3_eliminados = 0
        archivos_s3_fallidos = 0
        
        # Eliminar archivos de S3
        if s3_available:
            print(f"\n🗑️  Eliminando archivos de S3...")
            for i, factura in enumerate(facturas, 1):
                print(f"  [{i}/{total_facturas}] Procesando: {factura.cufe[:20]}...")
                
                # Eliminar archivo proveedor
                if factura.archivo_proveedor_s3_key:
                    try:
                        s3_service.delete_file(factura.archivo_proveedor_s3_key)
                        archivos_s3_eliminados += 1
                        print(f"    ✓ Eliminado: {factura.archivo_proveedor_s3_key}")
                    except Exception as e:
                        archivos_s3_fallidos += 1
                        print(f"    ✗ Error: {e}")
                
                # Eliminar archivo DIAN
                if factura.archivo_dian_s3_key:
                    try:
                        s3_service.delete_file(factura.archivo_dian_s3_key)
                        archivos_s3_eliminados += 1
                        print(f"    ✓ Eliminado: {factura.archivo_dian_s3_key}")
                    except Exception as e:
                        archivos_s3_fallidos += 1
                        print(f"    ✗ Error: {e}")
        
        # Eliminar productos (cascada automática, pero por si acaso)
        print(f"\n🗑️  Eliminando productos...")
        productos_eliminados = session.query(InvoiceProductV2).delete()
        print(f"  ✓ {productos_eliminados} productos eliminados")
        
        # Eliminar facturas
        print(f"\n🗑️  Eliminando facturas...")
        facturas_eliminadas = session.query(InvoiceV2).delete()
        print(f"  ✓ {facturas_eliminadas} facturas eliminadas")
        
        # Commit
        session.commit()
        
        # Resumen
        print("\n" + "="*80)
        print("✅ ELIMINACIÓN COMPLETADA")
        print("="*80)
        print(f"\n📊 Resumen:")
        print(f"  • Facturas eliminadas: {facturas_eliminadas}")
        print(f"  • Productos eliminados: {productos_eliminados}")
        if s3_available:
            print(f"  • Archivos S3 eliminados: {archivos_s3_eliminados}")
            if archivos_s3_fallidos > 0:
                print(f"  • Archivos S3 fallidos: {archivos_s3_fallidos}")
        print("\n✅ Base de datos limpia")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error durante la eliminación: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        session.close()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(eliminar_todas_facturas())
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(1)
