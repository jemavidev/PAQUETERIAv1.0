#!/usr/bin/env python3
"""
Script ultra-simplificado para corregir emisor/adquiriente
Solo usa SQL directo para evitar problemas de importación
"""
import os
os.chdir('/home/stk/Documents/GIT/PAQUETEX v1.0/CODE')

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear conexión a la base de datos
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("🔧 CORRECCIÓN RÁPIDA: Emisor/Adquiriente")
print("=" * 80)
print()

# Consultar facturas con archivo DIAN
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT cufe, dian_emisor_razon_social, dian_adquiriente_razon_social, archivo_dian_s3_key
        FROM invoices_v2
        WHERE archivo_dian_s3_key IS NOT NULL
        LIMIT 5
    """))
    
    facturas = result.fetchall()
    
    print(f"📊 Encontradas {len(facturas)} facturas con archivo DIAN (mostrando primeras 5)")
    print()
    
    if len(facturas) == 0:
        print("ℹ️ No hay facturas con archivos DIAN para procesar")
    else:
        print("Facturas encontradas:")
        print("-" * 80)
        for i, f in enumerate(facturas, 1):
            print(f"{i}. CUFE: {f[0][:16]}...")
            print(f"   Emisor: {f[1]}")
            print(f"   Adquiriente: {f[2]}")
            print(f"   Archivo S3: {f[3]}")
            print()
        
        print("=" * 80)
        print("⚠️ NOTA IMPORTANTE:")
        print("=" * 80)
        print()
        print("El código de corrección ya está implementado en:")
        print("  - CODE/src/app/services/pdf_parser_service.py")
        print()
        print("Para aplicar la corrección a estas facturas:")
        print("  1. Elimina las facturas desde la interfaz web (Tab CUFE)")
        print("  2. Vuelve a cargar los archivos DIAN")
        print("  3. Los datos se extraerán correctamente con la nueva lógica")
        print()
        print("O bien, puedes reprocesar manualmente cada factura desde la interfaz.")
        print()

print("✅ Análisis completado")
