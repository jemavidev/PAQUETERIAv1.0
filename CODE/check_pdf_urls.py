#!/usr/bin/env python3
"""
Script para verificar si las facturas tienen archivo_proveedor_url
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from src.app.core.config import settings

def main():
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            # Contar facturas
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(archivo_proveedor_url) as con_url,
                    COUNT(*) - COUNT(archivo_proveedor_url) as sin_url
                FROM invoices_v2
            """))
            
            row = result.fetchone()
            print("=" * 80)
            print("DIAGNÓSTICO: Archivos PDF en Facturas")
            print("=" * 80)
            print(f"\n📊 Total de facturas: {row[0]}")
            print(f"✅ Con archivo_proveedor_url: {row[1]}")
            print(f"❌ Sin archivo_proveedor_url: {row[2]}")
            
            # Mostrar ejemplos
            print("\n" + "-" * 80)
            print("EJEMPLOS DE FACTURAS:")
            print("-" * 80)
            
            result = conn.execute(text("""
                SELECT 
                    SUBSTR(cufe, 1, 20) as cufe_corto,
                    proveedor_nombre,
                    numero_factura,
                    CASE 
                        WHEN archivo_proveedor_url IS NOT NULL AND archivo_proveedor_url != '' 
                        THEN '✅ SÍ' 
                        ELSE '❌ NO' 
                    END as tiene_pdf,
                    SUBSTR(archivo_proveedor_url, 1, 60) as url_corta
                FROM invoices_v2
                ORDER BY created_at DESC
                LIMIT 10
            """))
            
            for row in result:
                print(f"\nCUFE: {row[0]}...")
                print(f"  Proveedor: {row[1]}")
                print(f"  Número: {row[2]}")
                print(f"  Tiene PDF: {row[3]}")
                if row[4]:
                    print(f"  URL: {row[4]}...")
            
            print("\n" + "=" * 80)
            print("CONCLUSIÓN:")
            print("=" * 80)
            
            if row[2] == row[0]:  # Si sin_url == total
                print("\n⚠️  NINGUNA factura tiene archivo_proveedor_url")
                print("\nPOSIBLES CAUSAS:")
                print("1. Las facturas fueron creadas antes de implementar la subida a S3")
                print("2. El servicio S3 no está configurado (variables de entorno)")
                print("3. Hubo errores al subir los archivos a S3")
                print("\nSOLUCIÓN:")
                print("- Verifica las variables de entorno AWS en .env")
                print("- Re-sube las facturas usando el modal de carga")
                print("- O implementa un script de migración para subir PDFs existentes")
            elif row[1] > 0:
                print(f"\n✅ {row[1]} facturas tienen PDF disponible")
                print(f"⚠️  {row[2]} facturas NO tienen PDF")
                print("\nLas facturas con PDF deberían tener el botón verde funcionando.")
            else:
                print("\n❌ Todas las facturas NO tienen PDF")
            
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
