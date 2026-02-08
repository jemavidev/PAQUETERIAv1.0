#!/usr/bin/env python3
"""
Script para analizar la extracción de productos de los PDFs CUFE
"""
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto del PDF usando pdftotext"""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', pdf_path, '-'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error extrayendo texto: {e}")
        return ""

def analyze_product_section(text: str) -> Dict[str, Any]:
    """Analiza la sección de productos"""
    
    # Buscar sección de productos
    patterns = [
        r'(?:Detalles de Productos|Detalle de Ítems|DETALLE DE PRODUCTOS)([\s\S]{0,10000}?)(?:Notas [Ff]inales|Datos [Tt]otales|Observaciones)',
    ]
    
    productos_section = None
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            productos_section = match.group(1)
            print(f"✓ Sección de productos encontrada")
            break
    
    if not productos_section:
        print("✗ No se encontró sección de productos")
        return {'found': False, 'section': None, 'lines': []}
    
    lines = productos_section.split('\n')
    product_lines = []
    
    for i, line in enumerate(lines[:100]):
        line_stripped = line.strip()
        if len(line_stripped) < 10:
            continue
        
        # Buscar líneas que parecen productos
        # Formato típico: Nro Código Descripción U/M Cantidad Precio...
        if re.search(r'\d{4,13}', line_stripped):  # Tiene código de producto
            product_lines.append({
                'line_num': i,
                'content': line_stripped,
                'has_code': True,
                'has_price': bool(re.search(r'\$\s*[\d.,]+', line_stripped)),
                'has_quantity': bool(re.search(r'\b\d{1,4}[.,]\d{2}\b', line_stripped)),
            })
    
    return {
        'found': True,
        'section': productos_section[:500],
        'lines': product_lines,
        'total_lines': len(product_lines)
    }

def extract_products_improved(text: str) -> List[Dict[str, Any]]:
    """Extracción mejorada de productos"""
    productos = []
    
    # Buscar sección de productos
    match = re.search(
        r'(?:Detalles de Productos)([\s\S]{0,10000}?)(?:Notas [Ff]inales)',
        text,
        re.IGNORECASE
    )
    
    if not match:
        return productos
    
    productos_section = match.group(1)
    lines = productos_section.split('\n')
    
    for line in lines:
        line = line.strip()
        if len(line) < 20:
            continue
        
        # Patrón mejorado para capturar productos
        # Formato: Nro Código Descripción U/M Cantidad Precio_unit Descuento Recargo IVA % Total
        pattern = r'^\s*(\d{1,3})\s+(\d{4,13})\s+(.+?)\s+(NIU|PK|BX|UND)\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)'
        
        match = re.match(pattern, line)
        if match:
            try:
                nro = match.group(1)
                codigo = match.group(2)
                descripcion = match.group(3).strip()
                unidad = match.group(4)
                cantidad = float(match.group(5).replace(',', '.'))
                precio_str = match.group(6).replace('.', '').replace(',', '.')
                precio = float(precio_str)
                
                # Buscar el total al final de la línea
                total_match = re.search(r'\$\s*([0-9.,]+)\s*$', line)
                total = None
                if total_match:
                    total_str = total_match.group(1).replace('.', '').replace(',', '.')
                    total = float(total_str)
                
                # Buscar IVA
                iva_match = re.search(r'(\d{1,2})[.,]00\s+', line)
                iva = float(iva_match.group(1)) if iva_match else 0.0
                
                productos.append({
                    'nro': nro,
                    'codigo': codigo,
                    'descripcion': descripcion[:100],
                    'unidad_medida': unidad,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'iva_porcentaje': iva,
                    'total': total
                })
                
            except Exception as e:
                print(f"Error procesando línea: {e}")
                print(f"Línea: {line[:100]}")
    
    return productos

def main():
    cufe_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE")
    
    if not cufe_dir.exists():
        print(f"Directorio no encontrado: {cufe_dir}")
        return
    
    pdf_files = list(cufe_dir.glob("*.pdf"))
    print(f"\n{'='*80}")
    print(f"Analizando {len(pdf_files)} archivos PDF CUFE")
    print(f"{'='*80}\n")
    
    # Analizar primeros 3 PDFs
    for i, pdf_file in enumerate(pdf_files[:3], 1):
        print(f"\n{'='*80}")
        print(f"PDF {i}: {pdf_file.name[:60]}...")
        print(f"{'='*80}")
        
        text = extract_text_from_pdf(str(pdf_file))
        if not text:
            print("✗ No se pudo extraer texto")
            continue
        
        print(f"✓ Texto extraído: {len(text)} caracteres")
        
        # Analizar sección de productos
        analysis = analyze_product_section(text)
        
        if analysis['found']:
            print(f"✓ Líneas de productos detectadas: {analysis['total_lines']}")
            print(f"\nPrimeras 3 líneas de productos:")
            for j, pline in enumerate(analysis['lines'][:3], 1):
                print(f"\n  Línea {j}:")
                print(f"    {pline['content'][:120]}...")
                print(f"    - Tiene código: {pline['has_code']}")
                print(f"    - Tiene precio: {pline['has_price']}")
                print(f"    - Tiene cantidad: {pline['has_quantity']}")
        
        # Intentar extracción
        print(f"\n{'─'*80}")
        print("Intentando extracción de productos...")
        productos = extract_products_improved(text)
        
        if productos:
            print(f"✓ Productos extraídos: {len(productos)}")
            print(f"\nPrimeros 3 productos:")
            for j, prod in enumerate(productos[:3], 1):
                print(f"\n  Producto {j}:")
                print(f"    Código: {prod['codigo']}")
                print(f"    Descripción: {prod['descripcion']}")
                print(f"    Cantidad: {prod['cantidad']} {prod['unidad_medida']}")
                print(f"    Precio Unit: ${prod['precio_unitario']:,.2f}")
                print(f"    IVA: {prod['iva_porcentaje']}%")
                if prod['total']:
                    print(f"    Total: ${prod['total']:,.2f}")
        else:
            print("✗ No se extrajeron productos")
            print("\nMuestra de la sección de productos:")
            if analysis['found']:
                print(analysis['section'][:800])

if __name__ == "__main__":
    main()
