#!/usr/bin/env python3
"""
Script para diagnosticar por qué las facturas se están cargando con CUFE temporal
cuando deberían extraerse correctamente
"""
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.pdf_parser_service import PDFParserService
import tempfile
import shutil

# PDFs de prueba
test_pdfs = [
    'CUFE/FACTURAS/FE15778.pdf',
    'CUFE/FACTURAS/FV09006851640112400000125.pdf',
    'CUFE/FACTURAS/ad00454539650892500016306.pdf',
]

parser = PDFParserService()

print("="*80)
print("DIAGNÓSTICO: Extracción de CUFE en carga de facturas")
print("="*80)
print()

for pdf_path in test_pdfs:
    print(f"\n{'='*80}")
    print(f"Probando: {pdf_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        continue
    
    try:
        # Simular el flujo de carga de facturas
        print("\n1️⃣ Extrayendo texto del PDF...")
        text = parser.extract_text_from_pdf(pdf_path, max_pages=5)
        print(f"   ✓ Texto extraído: {len(text)} caracteres")
        
        print("\n2️⃣ Parseando factura de proveedor...")
        data = parser.parse_provider_invoice(pdf_path)
        
        if 'error' in data:
            print(f"   ❌ Error: {data['error']}")
            continue
        
        print(f"   ✓ Datos extraídos:")
        print(f"      - CUFE: {data.get('cufe', 'NO ENCONTRADO')}")
        print(f"      - Proveedor: {data.get('proveedor_nombre', 'NO ENCONTRADO')}")
        print(f"      - NIT: {data.get('proveedor_nit', 'NO ENCONTRADO')}")
        print(f"      - Número: {data.get('numero_factura', 'NO ENCONTRADO')}")
        print(f"      - Fecha: {data.get('fecha_emision', 'NO ENCONTRADO')}")
        print(f"      - Total: {data.get('total_factura', 'NO ENCONTRADO')}")
        
        # Verificar si se generaría CUFE temporal
        cufe = data.get('cufe')
        if not cufe:
            print("\n   ⚠️ NO SE EXTRAJO CUFE - Se generaría CUFE temporal")
            print("   Razón: El método extract_cufe() no encontró un patrón de 96 caracteres hex")
        else:
            print(f"\n   ✅ CUFE EXTRAÍDO CORRECTAMENTE")
            print(f"      Longitud: {len(cufe)} caracteres")
            print(f"      Primeros 20: {cufe[:20]}...")
            print(f"      Últimos 20: ...{cufe[-20:]}")
        
    except Exception as e:
        print(f"   ❌ Error procesando PDF: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("CONCLUSIÓN:")
print("="*80)
print("""
Si los CUFEs se extraen correctamente aquí pero no en la aplicación:
1. Verificar que pdfplumber esté instalado en el entorno de producción
2. Verificar que los PDFs cargados sean los mismos que estos de prueba
3. Verificar logs del servidor para ver errores durante la carga
4. Verificar que el método parse_provider_invoice() se esté llamando correctamente

Si los CUFEs NO se extraen aquí:
1. Los PDFs pueden tener el CUFE en formato de imagen (no texto)
2. El CUFE puede estar dividido en múltiples líneas con espacios
3. El formato del PDF puede ser diferente al esperado
""")
