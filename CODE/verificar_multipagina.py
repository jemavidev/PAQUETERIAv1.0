#!/usr/bin/env python3
"""
Script para verificar si el parser está leyendo todas las páginas
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import boto3
import tempfile
from app.config import settings
from app.services.pdf_parser_service import PDFParserService
import pdfplumber

def main():
    # CUFE de la factura con más productos
    cufe = "7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2"
    s3_key = f"invoices/dian/{cufe}.pdf"
    
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE EXTRACCIÓN MULTI-PÁGINA")
    print("=" * 80)
    print(f"Factura: FE-15778")
    print(f"CUFE: {cufe[:20]}...")
    print()
    
    try:
        # Descargar de S3
        print("📥 Descargando archivo de S3...")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            s3_client.download_fileobj(settings.aws_s3_bucket, s3_key, tmp_file)
            tmp_path = tmp_file.name
        
        print(f"✅ Archivo descargado")
        print()
        
        # Contar páginas
        print("📄 Analizando páginas...")
        with pdfplumber.open(tmp_path) as pdf:
            num_pages = len(pdf.pages)
            print(f"   Total de páginas: {num_pages}")
            
            # Ver cuánto texto hay en cada página
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                print(f"   Página {i}: {len(text)} caracteres")
        
        print()
        
        # Parsear documento
        print("🔍 Parseando documento con PDFParserService...")
        result = PDFParserService.parse_dian_document(tmp_path)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            productos = result.get('productos', [])
            print(f"✅ Productos extraídos: {len(productos)}")
            print()
            
            if productos:
                print("📦 LISTA COMPLETA DE PRODUCTOS:")
                print("-" * 80)
                for i, p in enumerate(productos, 1):
                    codigo = p.get('codigo_producto', 'N/A')
                    desc = p.get('descripcion', 'N/A')[:45]
                    cant = p.get('cantidad', 0)
                    precio = p.get('precio_unitario', 0)
                    print(f"  {i:2d}. {codigo:15s} | {desc:45s} | {cant:6.2f} | ${precio:8,.2f}")
        
        # Limpiar archivo temporal
        os.unlink(tmp_path)
        print()
        print("=" * 80)
        print("✅ Análisis completado")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
