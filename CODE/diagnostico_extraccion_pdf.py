#!/usr/bin/env python3
"""
Script de diagnóstico para ver qué información se está extrayendo de los PDFs
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.pdf_parser_service import PDFParserService

def diagnosticar_pdf(pdf_path: str):
    """
    Diagnostica la extracción de un PDF mostrando:
    1. Texto extraído (primeras 2000 caracteres)
    2. Información detectada
    3. Patrones que coincidieron
    """
    print(f"\n{'='*80}")
    print(f"📄 Analizando: {os.path.basename(pdf_path)}")
    print(f"{'='*80}\n")
    
    parser = PDFParserService()
    
    # 1. Extraer texto
    print("1️⃣  TEXTO EXTRAÍDO (primeros 2000 caracteres):")
    print("-" * 80)
    text = parser.extract_text_from_pdf(pdf_path)
    if text:
        print(text[:2000])
        print(f"\n... (Total: {len(text)} caracteres)")
    else:
        print("❌ No se pudo extraer texto")
        return
    
    print("\n" + "="*80 + "\n")
    
    # 2. Parsear factura
    print("2️⃣  INFORMACIÓN DETECTADA:")
    print("-" * 80)
    result = parser.parse_provider_invoice(pdf_path)
    
    # Mostrar cada campo
    campos = [
        ('CUFE', result.get('cufe')),
        ('Proveedor', result.get('proveedor_nombre')),
        ('NIT', result.get('proveedor_nit')),
        ('Fecha', result.get('fecha_emision')),
        ('Número Factura', result.get('numero_factura')),
        ('Total', result.get('total_factura')),
    ]
    
    for nombre, valor in campos:
        if valor:
            print(f"✅ {nombre:20s}: {valor}")
        else:
            print(f"❌ {nombre:20s}: NO DETECTADO")
    
    print("\n" + "="*80 + "\n")
    
    # 3. Buscar manualmente patrones comunes
    print("3️⃣  BÚSQUEDA MANUAL DE PATRONES:")
    print("-" * 80)
    
    # Buscar líneas con palabras clave
    keywords = {
        'Proveedor/Emisor': ['razón social', 'razon social', 'emisor', 'vendedor', 'proveedor'],
        'NIT': ['nit', 'n.i.t'],
        'Número': ['número', 'numero', 'factura', 'documento', 'fev', 'fv', 'ad'],
        'Fecha': ['fecha', 'date'],
        'Total': ['total', 'valor', 'pagar', 'neto'],
    }
    
    lines = text.split('\n')
    for categoria, palabras in keywords.items():
        print(f"\n🔍 Buscando {categoria}:")
        encontradas = []
        for i, line in enumerate(lines[:100]):  # Primeras 100 líneas
            line_lower = line.lower()
            if any(palabra in line_lower for palabra in palabras):
                encontradas.append(f"  Línea {i+1}: {line.strip()}")
        
        if encontradas:
            for linea in encontradas[:5]:  # Mostrar máximo 5
                print(linea)
        else:
            print(f"  ❌ No se encontraron líneas con: {', '.join(palabras)}")
    
    print("\n" + "="*80 + "\n")
    
    # 4. Sugerencias
    print("4️⃣  SUGERENCIAS:")
    print("-" * 80)
    
    if not result.get('proveedor_nombre'):
        print("⚠️  PROVEEDOR NO DETECTADO")
        print("   Busca manualmente en el texto líneas que contengan:")
        print("   - Razón Social, Emisor, Vendedor")
        print("   - Nombres en MAYÚSCULAS seguidos de SAS, LTDA, S.A.S, etc.")
        print()
    
    if not result.get('numero_factura'):
        print("⚠️  NÚMERO DE FACTURA NO DETECTADO")
        print("   Busca manualmente patrones como:")
        print("   - Número: 123456")
        print("   - Factura: ABC-123")
        print("   - FEV123, FV-456, AD789")
        print()
    
    if not result.get('total_factura'):
        print("⚠️  TOTAL NO DETECTADO")
        print("   Busca manualmente líneas con:")
        print("   - Total a pagar, Total factura, Total neto")
        print("   - Valores con formato: $1.234.567 o 1,234,567.89")
        print()
    
    if not result.get('cufe'):
        print("⚠️  CUFE NO DETECTADO")
        print("   El CUFE es un código de 96 caracteres hexadecimales")
        print("   Busca en el PDF un código largo (96 caracteres)")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python diagnostico_extraccion_pdf.py <ruta_al_pdf>")
        print("\nEjemplo:")
        print("  python diagnostico_extraccion_pdf.py CUFE/FACTURAS/factura1.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: El archivo no existe: {pdf_path}")
        sys.exit(1)
    
    try:
        diagnosticar_pdf(pdf_path)
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
