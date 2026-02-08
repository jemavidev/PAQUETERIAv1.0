#!/usr/bin/env python3
"""
Script para analizar patrones en archivos CUFE
Extrae texto de múltiples PDFs y detecta formatos de productos
"""
import os
import sys
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pdfplumber
except ImportError:
    print("❌ Error: pdfplumber no está instalado")
    print("Instalar con: pip install pdfplumber")
    sys.exit(1)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto de un PDF"""
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return '\n'.join(text_parts)
    except Exception as e:
        return f"ERROR: {e}"

def find_products_section(text: str) -> tuple:
    """Encuentra la sección de productos y retorna (inicio, fin, texto_seccion)"""
    patterns_inicio = [
        r'Detalles de [Pp]roductos',
        r'DETALLE DE PRODUCTOS',
        r'DETALLE',
        r'Descripción\s+U/M\s+Cantidad',
        r'Nro\.\s+Código\s+Descripción',
        r'Item\s+Código',
    ]
    
    patterns_fin = [
        r'Datos [Tt]otales',
        r'Notas [Ff]inales',
        r'Observaciones',
        r'OBSERVACIONES',
        r'Total factura',
        r'Subtotal',
    ]
    
    inicio_idx = -1
    inicio_pattern = None
    
    for pattern in patterns_inicio:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            inicio_idx = match.start()
            inicio_pattern = pattern
            break
    
    if inicio_idx == -1:
        return None, None, None
    
    fin_idx = len(text)
    fin_pattern = None
    
    for pattern in patterns_fin:
        match = re.search(pattern, text[inicio_idx:], re.IGNORECASE)
        if match:
            fin_idx = inicio_idx + match.start()
            fin_pattern = pattern
            break
    
    seccion = text[inicio_idx:fin_idx]
    return inicio_pattern, fin_pattern, seccion

def analyze_product_lines(seccion: str) -> dict:
    """Analiza las líneas de productos para detectar patrones"""
    lines = seccion.split('\n')
    
    analysis = {
        'total_lines': len(lines),
        'patterns_found': [],
        'sample_lines': [],
        'has_codigo': False,
        'has_descripcion': False,
        'has_cantidad': False,
        'has_precio': False,
        'has_iva': False,
        'formato_detectado': None,
    }
    
    # Analizar primeras 20 líneas de productos
    for i, line in enumerate(lines[:30]):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # Detectar si tiene número de línea al inicio
        if re.match(r'^\d{1,3}\s+', line):
            analysis['sample_lines'].append(line)
            
            # PATRÓN 1: Nro Código Descripción U/M Cantidad Precio...
            if re.match(r'^\d{1,3}\s+\d{3,13}\s+.+?\s+\d{2,3}\s+[0-9]+[.,][0-9]{2}\s+\$', line):
                analysis['patterns_found'].append('FORMATO_0: Nro Código Descripción U/M Cantidad Precio')
                analysis['formato_detectado'] = 'FORMATO_0'
                analysis['has_codigo'] = True
                analysis['has_descripcion'] = True
                analysis['has_cantidad'] = True
                analysis['has_precio'] = True
            
            # PATRÓN 2: Nro Código U/M Cantidad Precio (descripción en otra línea)
            elif re.match(r'^\d{1,3}\s+\d{3,13}\s+(NIU|PK|BX|UND|UN|EA|\d{2})\s+[0-9]+[.,][0-9]{2}\s+\$', line):
                analysis['patterns_found'].append('FORMATO_1: Nro Código U/M Cantidad Precio')
                if not analysis['formato_detectado']:
                    analysis['formato_detectado'] = 'FORMATO_1'
                analysis['has_codigo'] = True
                analysis['has_cantidad'] = True
                analysis['has_precio'] = True
            
            # PATRÓN 3: Nro U/M Cantidad Precio (sin código)
            elif re.match(r'^\d{1,3}\s+(NIU|PK|BX|UND|UN|EA|\d{2})\s+[0-9]+[.,][0-9]{2}\s+\$', line):
                analysis['patterns_found'].append('FORMATO_5: Nro U/M Cantidad Precio (sin código)')
                if not analysis['formato_detectado']:
                    analysis['formato_detectado'] = 'FORMATO_5'
                analysis['has_cantidad'] = True
                analysis['has_precio'] = True
            
            # PATRÓN 4: Nro Código Descripción_Corta U/M | texto Cantidad
            elif re.match(r'^\d{1,3}\s+\d{3,13}\s+.+?\s+(NIU|PK|BX|UND|UN|EA)\s*\|', line):
                analysis['patterns_found'].append('FORMATO_2: Nro Código Descripción U/M | texto Cantidad')
                if not analysis['formato_detectado']:
                    analysis['formato_detectado'] = 'FORMATO_2'
                analysis['has_codigo'] = True
                analysis['has_descripcion'] = True
            
            # Detectar IVA
            if re.search(r'\d{1,2}[.,]00\s+\$', line):
                analysis['has_iva'] = True
        
        # Detectar descripciones en líneas separadas (sin número al inicio)
        elif re.match(r'^[A-ZÁÉÍÓÚÑ]', line) and len(line) > 10:
            if i < 25:  # Solo primeras líneas
                analysis['sample_lines'].append(f"DESC: {line}")
                analysis['has_descripcion'] = True
    
    # Eliminar duplicados en patterns_found
    analysis['patterns_found'] = list(set(analysis['patterns_found']))
    
    return analysis

def main():
    cufe_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE")
    
    if not cufe_dir.exists():
        print(f"❌ Error: Directorio no encontrado: {cufe_dir}")
        return
    
    pdf_files = list(cufe_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ Error: No se encontraron archivos PDF en {cufe_dir}")
        return
    
    print("=" * 100)
    print("🔍 ANÁLISIS DE PATRONES EN ARCHIVOS CUFE")
    print("=" * 100)
    print(f"\n📁 Directorio: {cufe_dir}")
    print(f"📄 Archivos encontrados: {len(pdf_files)}")
    print()
    
    # Analizar primeros 10 archivos
    resultados = []
    
    for i, pdf_file in enumerate(pdf_files[:10], 1):
        print(f"\n{'='*100}")
        print(f"📄 ARCHIVO {i}/10: {pdf_file.name[:60]}...")
        print(f"{'='*100}")
        
        # Extraer texto
        print("   Extrayendo texto...", end=" ")
        text = extract_text_from_pdf(str(pdf_file))
        
        if text.startswith("ERROR"):
            print(f"❌ {text}")
            continue
        
        print(f"✅ ({len(text)} caracteres)")
        
        # Buscar sección de productos
        print("   Buscando sección de productos...", end=" ")
        inicio_pattern, fin_pattern, seccion = find_products_section(text)
        
        if not seccion:
            print("❌ No encontrada")
            continue
        
        print(f"✅")
        print(f"      Inicio: {inicio_pattern}")
        print(f"      Fin: {fin_pattern}")
        print(f"      Tamaño: {len(seccion)} caracteres")
        
        # Analizar patrones
        print("   Analizando patrones...", end=" ")
        analysis = analyze_product_lines(seccion)
        print(f"✅")
        
        print(f"\n   📊 ANÁLISIS:")
        print(f"      Formato detectado: {analysis['formato_detectado'] or 'DESCONOCIDO'}")
        print(f"      Patrones encontrados: {len(analysis['patterns_found'])}")
        for pattern in analysis['patterns_found']:
            print(f"         - {pattern}")
        
        print(f"\n      Características:")
        print(f"         ✅ Código: {'SÍ' if analysis['has_codigo'] else 'NO'}")
        print(f"         ✅ Descripción: {'SÍ' if analysis['has_descripcion'] else 'NO'}")
        print(f"         ✅ Cantidad: {'SÍ' if analysis['has_cantidad'] else 'NO'}")
        print(f"         ✅ Precio: {'SÍ' if analysis['has_precio'] else 'NO'}")
        print(f"         ✅ IVA: {'SÍ' if analysis['has_iva'] else 'NO'}")
        
        print(f"\n      📝 Muestra de líneas (primeras 5):")
        for j, sample in enumerate(analysis['sample_lines'][:5], 1):
            print(f"         {j}. {sample[:90]}...")
        
        resultados.append({
            'archivo': pdf_file.name,
            'formato': analysis['formato_detectado'],
            'patterns': analysis['patterns_found'],
            'has_codigo': analysis['has_codigo'],
            'sample_lines': analysis['sample_lines'][:3]
        })
    
    # Resumen final
    print("\n" + "=" * 100)
    print("📊 RESUMEN DE ANÁLISIS")
    print("=" * 100)
    
    formatos_count = {}
    for r in resultados:
        formato = r['formato'] or 'DESCONOCIDO'
        formatos_count[formato] = formatos_count.get(formato, 0) + 1
    
    print(f"\n🎯 Formatos detectados:")
    for formato, count in sorted(formatos_count.items(), key=lambda x: x[1], reverse=True):
        print(f"   {formato}: {count} archivos")
    
    print(f"\n📋 Archivos con código de producto:")
    con_codigo = sum(1 for r in resultados if r['has_codigo'])
    sin_codigo = len(resultados) - con_codigo
    print(f"   ✅ Con código: {con_codigo}")
    print(f"   ❌ Sin código: {sin_codigo}")
    
    print(f"\n📝 Detalles por archivo:")
    for i, r in enumerate(resultados, 1):
        print(f"\n   {i}. {r['archivo'][:50]}...")
        print(f"      Formato: {r['formato'] or 'DESCONOCIDO'}")
        print(f"      Código: {'✅' if r['has_codigo'] else '❌'}")
        if r['sample_lines']:
            print(f"      Muestra: {r['sample_lines'][0][:70]}...")
    
    print("\n" + "=" * 100)
    print("✅ Análisis completado")
    print("=" * 100)

if __name__ == '__main__':
    main()
