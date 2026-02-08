#!/usr/bin/env python3
"""
Prueba del nuevo parser de productos CUFE
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

def extract_productos_cufe(text: str) -> List[Dict[str, Any]]:
    """
    Extrae productos del documento DIAN/CUFE
    Maneja el formato donde la descripción está en múltiples líneas
    """
    productos = []
    
    # Buscar sección de productos
    match = re.search(
        r'(?:Detalles de Productos|Detalle de Ítems|DETALLE DE PRODUCTOS)([\s\S]{0,15000}?)(?:Notas [Ff]inales|Datos [Tt]otales|Observaciones)',
        text,
        re.IGNORECASE
    )
    
    if not match:
        print("✗ No se encontró sección de productos")
        return productos
    
    productos_section = match.group(1)
    lines = productos_section.split('\n')
    
    i = 0
    while i < len(lines) and len(productos) < 200:
        line = lines[i].strip()
        
        # Buscar línea que comienza con número (indica producto)
        match_producto = re.match(
            r'^(\d{1,3})\s+(\d{3,13})?\s+(NIU|PK|BX|UND|UN)?\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
            line
        )
        
        if match_producto:
            try:
                nro = match_producto.group(1)
                codigo = match_producto.group(2) if match_producto.group(2) else ""
                unidad = match_producto.group(3) if match_producto.group(3) else "NIU"
                cantidad_str = match_producto.group(4).replace(',', '.')
                precio_unit_str = match_producto.group(5).replace('.', '').replace(',', '.')
                
                cantidad = float(cantidad_str)
                precio_unitario = float(precio_unit_str)
                
                # Buscar descripción en la línea ANTERIOR
                descripcion_parte1 = ""
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line and not re.match(r'^\d+\s', prev_line):
                        descripcion_parte1 = prev_line
                
                # Buscar descripción adicional al FINAL de la línea actual
                descripcion_parte2 = ""
                resto = re.split(r'\$\s*[0-9.,]+', line)
                if len(resto) > 1:
                    descripcion_parte2 = resto[-1].strip()
                
                # Combinar descripciones
                descripcion = f"{descripcion_parte1} {descripcion_parte2}".strip()
                
                # Limpiar descripción
                descripcion = re.sub(r'\s+', ' ', descripcion)
                descripcion = descripcion[:250]
                
                # Buscar total (último valor monetario)
                valores = re.findall(r'\$\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
                total_item = None
                if valores:
                    try:
                        total_str = valores[-1].replace('.', '').replace(',', '.')
                        total_item = float(total_str)
                    except:
                        pass
                
                # Buscar IVA
                iva_porcentaje = 0.0
                iva_match = re.search(r'(\d{1,2})[.,]00\s+', line)
                if iva_match:
                    iva_porcentaje = float(iva_match.group(1))
                
                # Si no hay código, usar el número de línea
                if not codigo:
                    codigo = f"ITEM-{nro}"
                
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': descripcion if descripcion else f"Producto {nro}",
                    'cantidad': cantidad,
                    'unidad_medida': unidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item if total_item else (precio_unitario * cantidad),
                })
                
            except Exception as e:
                print(f"Error procesando línea {i}: {e}")
        
        i += 1
    
    return productos

def main():
    cufe_dir = Path("/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE")
    
    if not cufe_dir.exists():
        print(f"Directorio no encontrado: {cufe_dir}")
        return
    
    pdf_files = list(cufe_dir.glob("*.pdf"))
    print(f"\n{'='*80}")
    print(f"Probando nuevo parser CUFE con {len(pdf_files)} archivos")
    print(f"{'='*80}\n")
    
    # Probar con 3 PDFs
    for i, pdf_file in enumerate(pdf_files[:3], 1):
        print(f"\n{'='*80}")
        print(f"PDF {i}: {pdf_file.name[:60]}...")
        print(f"{'='*80}")
        
        text = extract_text_from_pdf(str(pdf_file))
        if not text:
            print("✗ No se pudo extraer texto")
            continue
        
        productos = extract_productos_cufe(text)
        
        if productos:
            print(f"✓ Productos extraídos: {len(productos)}")
            print(f"\nPrimeros 5 productos:\n")
            for j, prod in enumerate(productos[:5], 1):
                print(f"  {j}. Código: {prod['codigo_producto']}")
                print(f"     Descripción: {prod['descripcion']}")
                print(f"     Cantidad: {prod['cantidad']} {prod['unidad_medida']}")
                print(f"     Precio Unit: ${prod['precio_unitario']:,.2f}")
                print(f"     IVA: {prod['iva_porcentaje']}%")
                print(f"     Total: ${prod['total_item']:,.2f}")
                print()
        else:
            print("✗ No se extrajeron productos")

if __name__ == "__main__":
    main()
