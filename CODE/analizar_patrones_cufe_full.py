#!/usr/bin/env python3
"""
Script para analizar patrones en archivos CUFE - VERSIÓN EXTENDIDA
Analiza el directorio completo con 113+ archivos
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
    
    # Analizar primeras 30 líneas de productos
    for i, line in enumerate(lines[:30]):
        line = line.strip()
        if not line or len(line) < 10:
            continue
        
        # Detectar si tiene número de línea al inicio
        if re.match(r'^\d{1,3}\s+', line):
            analysis['sample_lines'].append(line)
            
            # PATRÓN 0: Nro Código Descripción U/M Cantidad Precio...
            if re.match(r'^\d{1,3}\s+\d{3,13}\s+.+?\s+\d{2,3}\s+[0-9]+[.,][0-9]{2}\s+\$', line):
                analysis['patterns_found'].append('FORMATO_0: Nro Código Descripción U/M Cantidad Precio')
                analysis['formato_detectado'] = 'FORMATO_0'
                analysis['has_codigo'] = True
                analysis['has_descripcion'] = True
                analysis['has_cantidad'] = True
                analysis['has_precio'] = True
            
            # PATRÓN 1: Nro Código U/M Cantidad Precio (descripción en otra línea)
            elif re.match(r'^\d{1,3}\s+\d{3,13}\s+(NIU|PK|BX|UND|UN|EA|\d{2})\s+[0-9]+[.,][0-9]{2}\s+\$', line):
                analysis['patterns_found'].append('FORMATO_1: Nro Código U/M Cantidad Precio')
                if not analysis['formato_detectado']:
                    analysis['formato_detectado'] = 'FORMATO_1'
                analysis['has_codigo'] = True
                analysis['has_cantidad'] = True
                analysis['has_precio'] = True
            
            # PATRÓN 5: Nro U/M Cantidad Precio (sin código)
            elif re.match(r'^\d{1,3}\s+(\d{2})\s+[0-9]+[.,][0-9]{2}\s+\$', line):
                analysis['patterns_found'].append('FORMATO_5: Nro U/M Cantidad Precio (sin código)')
                if not analysis['formato_detectado']:
                    analysis['formato_detectado'] = 'FORMATO_5'
                analysis['has_cantidad'] = True
                analysis['has_precio'] = True
            
            # PATRÓN 2: Nro Código Descripción U/M | texto Cantidad
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
    cufe_dir = Path("/home/stk/Downloads/INVOICES FULL/CUFE")
    
    if not cufe_dir.exists():
        print(f"❌ Error: Directorio no encontrado: {cufe_dir}")
        return
    
    pdf_files = list(cufe_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ Error: No se encontraron archivos PDF en {cufe_dir}")
        return
    
    print("=" * 100)
    print("🔍 ANÁLISIS EXTENDIDO DE PATRONES EN ARCHIVOS CUFE")
    print("=" * 100)
    print(f"\n📁 Directorio: {cufe_dir}")
    print(f"📄 Archivos encontrados: {len(pdf_files)}")
    print()
    
    # Analizar TODOS los archivos
    resultados = []
    errores = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        # Mostrar progreso cada 10 archivos
        if i % 10 == 0 or i == 1:
            print(f"\n{'='*100}")
            print(f"📄 Procesando archivo {i}/{len(pdf_files)}: {pdf_file.name[:60]}...")
            print(f"{'='*100}")
        
        # Extraer texto
        text = extract_text_from_pdf(str(pdf_file))
        
        if text.startswith("ERROR"):
            errores.append({'archivo': pdf_file.name, 'error': text})
            if i % 10 == 0 or i == 1:
                print(f"   ❌ {text}")
            continue
        
        # Buscar sección de productos
        inicio_pattern, fin_pattern, seccion = find_products_section(text)
        
        if not seccion:
            errores.append({'archivo': pdf_file.name, 'error': 'No se encontró sección de productos'})
            if i % 10 == 0 or i == 1:
                print(f"   ❌ No se encontró sección de productos")
            continue
        
        # Analizar patrones
        analysis = analyze_product_lines(seccion)
        
        if i % 10 == 0 or i == 1:
            print(f"   ✅ Formato: {analysis['formato_detectado'] or 'DESCONOCIDO'}")
            print(f"   📊 Código: {'✅' if analysis['has_codigo'] else '❌'}")
        
        resultados.append({
            'archivo': pdf_file.name,
            'formato': analysis['formato_detectado'],
            'patterns': analysis['patterns_found'],
            'has_codigo': analysis['has_codigo'],
            'sample_lines': analysis['sample_lines'][:3]
        })
    
    # Resumen final
    print("\n" + "=" * 100)
    print("📊 RESUMEN DE ANÁLISIS EXTENDIDO")
    print("=" * 100)
    
    print(f"\n📈 Estadísticas generales:")
    print(f"   Total de archivos: {len(pdf_files)}")
    print(f"   Archivos analizados: {len(resultados)}")
    print(f"   Archivos con errores: {len(errores)}")
    
    formatos_count = {}
    for r in resultados:
        formato = r['formato'] or 'DESCONOCIDO'
        formatos_count[formato] = formatos_count.get(formato, 0) + 1
    
    print(f"\n🎯 Formatos detectados:")
    for formato, count in sorted(formatos_count.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (count / len(resultados) * 100) if resultados else 0
        print(f"   {formato}: {count} archivos ({porcentaje:.1f}%)")
    
    print(f"\n📋 Archivos con código de producto:")
    con_codigo = sum(1 for r in resultados if r['has_codigo'])
    sin_codigo = len(resultados) - con_codigo
    porcentaje_con = (con_codigo / len(resultados) * 100) if resultados else 0
    porcentaje_sin = (sin_codigo / len(resultados) * 100) if resultados else 0
    print(f"   ✅ Con código: {con_codigo} ({porcentaje_con:.1f}%)")
    print(f"   ❌ Sin código: {sin_codigo} ({porcentaje_sin:.1f}%)")
    
    if errores:
        print(f"\n⚠️ Archivos con errores ({len(errores)}):")
        for i, err in enumerate(errores[:10], 1):
            print(f"   {i}. {err['archivo'][:50]}... - {err['error'][:50]}")
        if len(errores) > 10:
            print(f"   ... y {len(errores) - 10} errores más")
    
    # Mostrar ejemplos de cada formato
    print(f"\n📝 Ejemplos por formato:")
    formatos_mostrados = set()
    for r in resultados:
        formato = r['formato'] or 'DESCONOCIDO'
        if formato not in formatos_mostrados and len(formatos_mostrados) < 5:
            formatos_mostrados.add(formato)
            print(f"\n   {formato}:")
            print(f"      Archivo: {r['archivo'][:60]}...")
            print(f"      Código: {'✅' if r['has_codigo'] else '❌'}")
            if r['sample_lines']:
                print(f"      Muestra: {r['sample_lines'][0][:70]}...")
    
    print("\n" + "=" * 100)
    print("✅ Análisis extendido completado")
    print(f"📊 Total: {len(resultados)} archivos analizados de {len(pdf_files)} encontrados")
    print("=" * 100)

if __name__ == '__main__':
    main()
