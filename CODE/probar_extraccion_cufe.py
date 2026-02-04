#!/usr/bin/env python3
"""
Script interactivo para probar extracción de CUFE
"""
import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.pdf_parser_service import PDFParserService

def analizar_pdf(pdf_path):
    """Analiza un PDF y muestra información detallada sobre la extracción de CUFE"""
    
    print("="*80)
    print(f"📄 ANALIZANDO: {pdf_path}")
    print("="*80)
    
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    parser = PDFParserService()
    
    # Paso 1: Extraer texto
    print("\n🔹 PASO 1: Extracción de Texto")
    print("-" * 80)
    text = parser.extract_text_from_pdf(pdf_path, max_pages=5)
    
    if not text:
        print("❌ No se pudo extraer texto del PDF")
        print("\n💡 Posibles causas:")
        print("   - El PDF es una imagen escaneada")
        print("   - El PDF está protegido")
        print("   - El PDF está corrupto")
        return
    
    print(f"✅ Texto extraído: {len(text)} caracteres")
    print(f"\n📝 Primeros 300 caracteres:")
    print("-" * 80)
    print(text[:300])
    print("...")
    
    # Paso 2: Buscar CUFE
    print("\n🔹 PASO 2: Búsqueda de CUFE")
    print("-" * 80)
    cufe = parser.extract_cufe(text)
    
    if cufe:
        print(f"✅ CUFE ENCONTRADO:")
        print(f"   {cufe}")
        print(f"\n   Longitud: {len(cufe)} caracteres")
        print(f"   Primeros 20: {cufe[:20]}")
        print(f"   Últimos 20: {cufe[-20:]}")
        print(f"\n   ✅ Este PDF se cargará con CUFE real")
    else:
        print("❌ NO SE ENCONTRÓ CUFE")
        print("\n   ⚠️ Este PDF se cargará con CUFE temporal (TEMP_xxxxx)")
        print("   💡 Podrás asociar el CUFE manualmente después")
        
        # Debugging: Buscar patrones más cortos
        print("\n🔍 Buscando patrones hexadecimales más cortos...")
        shorter_matches = re.findall(r'[0-9a-fA-F]{32,}', text, re.IGNORECASE)
        
        if shorter_matches:
            print(f"   Encontrados {len(shorter_matches)} patrones hex:")
            for i, match in enumerate(shorter_matches[:5], 1):
                print(f"   {i}. {match[:60]}... (longitud: {len(match)})")
        else:
            print("   No se encontraron patrones hexadecimales largos")
        
        # Buscar palabras clave
        print("\n🔍 Buscando palabras clave relacionadas con CUFE...")
        keywords = ['CUFE', 'CUDE', 'CUDS', 'Código', 'codigo', 'Hash']
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in text.lower():
                idx = text.lower().find(keyword.lower())
                context = text[max(0, idx-30):min(len(text), idx+150)]
                found_keywords.append((keyword, context))
        
        if found_keywords:
            print(f"   Encontradas {len(found_keywords)} palabras clave:")
            for keyword, context in found_keywords[:3]:
                print(f"\n   '{keyword}' encontrado:")
                print(f"   ...{context}...")
        else:
            print("   No se encontraron palabras clave relacionadas")
    
    # Paso 3: Otros datos extraídos
    print("\n🔹 PASO 3: Otros Datos Extraídos")
    print("-" * 80)
    
    data = parser.parse_provider_invoice(pdf_path)
    
    print(f"   Proveedor: {data.get('proveedor_nombre', 'NO ENCONTRADO')}")
    print(f"   NIT: {data.get('proveedor_nit', 'NO ENCONTRADO')}")
    print(f"   Número: {data.get('numero_factura', 'NO ENCONTRADO')}")
    print(f"   Fecha: {data.get('fecha_emision', 'NO ENCONTRADO')}")
    print(f"   Total: {data.get('total_factura', 'NO ENCONTRADO')}")
    
    print("\n" + "="*80)
    if cufe:
        print("✅ RESULTADO: PDF con CUFE extraíble")
    else:
        print("⚠️ RESULTADO: PDF sin CUFE extraíble (requiere asociación manual)")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 PROBADOR DE EXTRACCIÓN DE CUFE")
    print("="*80)
    
    if len(sys.argv) > 1:
        # Modo: archivo específico
        pdf_path = sys.argv[1]
        analizar_pdf(pdf_path)
    else:
        # Modo: PDFs de ejemplo
        print("\n📁 Analizando PDFs de ejemplo...")
        print()
        
        pdfs_ejemplo = [
            "CUFE/FACTURAS/FE15778.pdf",
            "CUFE/FACTURAS/FV09006851640112400000125.pdf",
            "CUFE/FACTURAS/ad00454539650892500016306.pdf",
        ]
        
        for pdf_path in pdfs_ejemplo:
            if os.path.exists(pdf_path):
                analizar_pdf(pdf_path)
                print("\n")
            else:
                print(f"⚠️ PDF no encontrado: {pdf_path}")
        
        print("\n💡 Para analizar un PDF específico:")
        print(f"   python3 {sys.argv[0]} ruta/al/archivo.pdf")
