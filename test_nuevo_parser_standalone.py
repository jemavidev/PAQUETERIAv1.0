#!/usr/bin/env python3
"""
Probar el nuevo parser (standalone)
"""
import re
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import pdfplumber
except:
    print("ERROR: pdfplumber no disponible")
    exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto completo del PDF"""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return '\n'.join(text_parts)


def extract_productos(text: str) -> List[Dict[str, Any]]:
    """Extrae productos del PDF DIAN"""
    productos = []
    
    # Buscar sección de productos
    patterns = [
        r'Detalles de Productos([\s\S]+?)(?:Notas Finales|Datos Totales|Hoja \d+ de \d+)',
        r'DETALLE DE PRODUCTOS([\s\S]+?)(?:Notas Finales|Datos Totales)',
    ]
    
    productos_section = None
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            productos_section = match.group(1)
            break
    
    if not productos_section:
        logger.warning("No se encontró sección de productos")
        return productos
    
    lines = productos_section.split('\n')
    i = 0
    
    while i < len(lines) and len(productos) < 200:
        line = lines[i].strip()
        
        if not line or line.startswith('---'):
            i += 1
            continue
        
        if any(marker in line for marker in ['Notas Finales', 'Datos Totales', 'Hoja ']):
            break
        
        if any(header in line for header in ['IMPUESTOS', 'Precio unitario', 'Descuento detalle']):
            i += 1
            continue
        
        # FORMATO 1A: Con código largo (10-13 dígitos) Y descripción
        match1a = re.match(
            r'^(\d{1,3})\s+(\d{10,13})\s+(.+?)\s+(NIU|PK|BX|UND|UN|EA|PC)\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
            line
        )
        
        # FORMATO 1B: Con código largo (10-13 dígitos) SIN descripción (descripción en línea anterior)
        match1b = re.match(
            r'^(\d{1,3})\s+(\d{10,13})\s+(NIU|PK|BX|UND|UN|EA|PC)\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
            line
        )
        
        if match1a:
            try:
                nro = match1a.group(1)
                codigo = match1a.group(2)
                descripcion = match1a.group(3).strip()
                unidad = match1a.group(4)
                cantidad = float(match1a.group(5).replace(',', '.'))
                precio_unitario = float(match1a.group(6).replace('.', '').replace(',', '.'))
                
                iva_porcentaje = 0.0
                iva_match = re.search(r'(\d{1,2})[.,]00\s+\$', line)
                if iva_match:
                    iva_porcentaje = float(iva_match.group(1))
                
                valores = re.findall(r'\$\s*([0-9.,]+)', line)
                total_item = precio_unitario * cantidad
                if valores:
                    try:
                        total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                    except:
                        pass
                
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': descripcion[:250],
                    'cantidad': cantidad,
                    'unidad_medida': unidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item,
                })
                
                logger.info(f"✅ Producto {nro}: {codigo} - {descripcion[:30]}...")
                i += 1
                continue
                
            except Exception as e:
                logger.warning(f"Error FORMATO 1A: {e}")
        
        if match1b:
            try:
                nro = match1b.group(1)
                codigo = match1b.group(2)
                unidad = match1b.group(3)
                cantidad = float(match1b.group(4).replace(',', '.'))
                precio_unitario = float(match1b.group(5).replace('.', '').replace(',', '.'))
                
                # Buscar descripción en línea anterior
                descripcion = f"Producto {nro}"
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line and not re.match(r'^\d+\s', prev_line):
                        if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                            descripcion = prev_line
                
                # Buscar descripción adicional en línea siguiente
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line and not re.match(r'^\d+\s', next_line):
                        if not any(h in next_line for h in ['Hoja ', 'IMPUESTOS', 'Precio']):
                            descripcion = f"{descripcion} {next_line}".strip()
                
                iva_porcentaje = 0.0
                iva_match = re.search(r'(\d{1,2})[.,]00\s+\$', line)
                if iva_match:
                    iva_porcentaje = float(iva_match.group(1))
                
                valores = re.findall(r'\$\s*([0-9.,]+)', line)
                total_item = precio_unitario * cantidad
                if valores:
                    try:
                        total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                    except:
                        pass
                
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': descripcion[:250],
                    'cantidad': cantidad,
                    'unidad_medida': unidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item,
                })
                
                logger.info(f"✅ Producto {nro}: {codigo} - {descripcion[:30]}...")
                i += 1
                continue
                
            except Exception as e:
                logger.warning(f"Error FORMATO 1B: {e}")
        
        # FORMATO 2: Con código corto (3-9 dígitos) Y descripción en medio
        match2a = re.match(
            r'^(\d{1,3})\s+(\d{3,9})\s+(.+?)\s+(NIU|PK|BX|UND|UN|EA|PC)\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
            line
        )
        
        # FORMATO 2B: Con código corto (3-9 dígitos) SIN descripción
        match2b = re.match(
            r'^(\d{1,3})\s+(\d{3,9})\s+(NIU|PK|BX|UND|UN|EA|PC)\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
            line
        )
        
        if match2a:
            try:
                nro = match2a.group(1)
                codigo = match2a.group(2)
                descripcion = match2a.group(3).strip()
                unidad = match2a.group(4)
                cantidad = float(match2a.group(5).replace(',', '.'))
                precio_unitario = float(match2a.group(6).replace('.', '').replace(',', '.'))
                
                # Buscar descripción adicional en línea anterior
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line and not re.match(r'^\d+\s', prev_line):
                        if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                            descripcion = f"{prev_line} {descripcion}".strip()
                
                # Buscar descripción adicional en línea siguiente
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line and not re.match(r'^\d+\s', next_line):
                        if not any(h in next_line for h in ['Hoja ', 'IMPUESTOS', 'Precio']):
                            descripcion = f"{descripcion} {next_line}".strip()
                
                iva_porcentaje = 0.0
                iva_match = re.search(r'(\d{1,2})[.,]00\s+\$', line)
                if iva_match:
                    iva_porcentaje = float(iva_match.group(1))
                
                valores = re.findall(r'\$\s*([0-9.,]+)', line)
                total_item = precio_unitario * cantidad
                if valores:
                    try:
                        total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                    except:
                        pass
                
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': descripcion[:250],
                    'cantidad': cantidad,
                    'unidad_medida': unidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item,
                })
                
                logger.info(f"✅ Producto {nro}: {codigo} - {descripcion[:30]}...")
                i += 1
                continue
                
            except Exception as e:
                logger.warning(f"Error FORMATO 2A: {e}")
        
        if match2b:
            try:
                nro = match2b.group(1)
                codigo = match2b.group(2)
                unidad = match2b.group(3)
                cantidad = float(match2b.group(4).replace(',', '.'))
                precio_unitario = float(match2b.group(5).replace('.', '').replace(',', '.'))
                
                descripcion = f"Producto {nro}"
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line and not re.match(r'^\d+\s', prev_line):
                        if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                            descripcion = prev_line
                
                iva_porcentaje = 0.0
                iva_match = re.search(r'(\d{1,2})[.,]00\s+\$', line)
                if iva_match:
                    iva_porcentaje = float(iva_match.group(1))
                
                valores = re.findall(r'\$\s*([0-9.,]+)', line)
                total_item = precio_unitario * cantidad
                if valores:
                    try:
                        total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                    except:
                        pass
                
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': descripcion[:250],
                    'cantidad': cantidad,
                    'unidad_medida': unidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item,
                })
                
                logger.info(f"✅ Producto {nro}: {codigo} - {descripcion[:30]}...")
                i += 1
                continue
                
            except Exception as e:
                logger.warning(f"Error FORMATO 2B: {e}")
        
        # FORMATO 3: SIN código (solo U/M código como 94)
        match3 = re.match(
            r'^(\d{1,3})\s+(\d{2})\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
            line
        )
        
        if match3:
            try:
                nro = match3.group(1)
                unidad_codigo = match3.group(2)
                cantidad = float(match3.group(3).replace(',', '.'))
                precio_unitario = float(match3.group(4).replace('.', '').replace(',', '.'))
                
                unidad_map = {'94': 'NIU', '10': 'PK', '11': 'BX', '01': 'UND'}
                unidad = unidad_map.get(unidad_codigo, 'NIU')
                
                descripcion = f"Producto {nro}"
                codigo = f"PROD{nro}"
                
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line and not re.match(r'^\d+\s', prev_line):
                        if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código', 'U/M']):
                            descripcion = prev_line
                            palabras = descripcion.split()
                            if palabras:
                                codigo = ''.join(palabras[:2]).upper()[:20]
                
                iva_porcentaje = 0.0
                iva_match = re.search(r'(\d{1,2})[.,]00\s+\$', line)
                if iva_match:
                    iva_porcentaje = float(iva_match.group(1))
                
                valores = re.findall(r'\$\s*([0-9.,]+)', line)
                total_item = precio_unitario * cantidad
                if valores:
                    try:
                        total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                    except:
                        pass
                
                productos.append({
                    'codigo_producto': codigo,
                    'descripcion': descripcion[:250],
                    'cantidad': cantidad,
                    'unidad_medida': unidad,
                    'precio_unitario': precio_unitario,
                    'iva_porcentaje': iva_porcentaje,
                    'total_item': total_item,
                })
                
                logger.info(f"✅ Producto {nro}: {codigo} - {descripcion[:30]}...")
                i += 1
                continue
                
            except Exception as e:
                logger.warning(f"Error FORMATO 3: {e}")
        
        i += 1
    
    logger.info(f"📊 Total productos extraídos: {len(productos)}")
    return productos


# ============================================================
# TESTS
# ============================================================

print("=" * 80)
print("TEST 1: PDF PROBLEMÁTICO (2 productos según XML)")
print("=" * 80)

pdf_path1 = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/90586381def1342a38806c310801a43659405240dcd445e0d640367591143dd4806cf6fca1ea21fb03b2ea47c62264a2.pdf"

text1 = extract_text_from_pdf(pdf_path1)
productos1 = extract_productos(text1)

print(f"\n✅ Productos extraídos: {len(productos1)}")
print(f"📋 Esperado: 2 productos\n")

for i, prod in enumerate(productos1, 1):
    print(f"{i}. Código: {prod['codigo_producto']}")
    print(f"   Descripción: {prod['descripcion']}")
    print(f"   Cantidad: {prod['cantidad']} {prod['unidad_medida']}")
    print(f"   Precio Unit: ${prod['precio_unitario']:,.2f}")
    print(f"   IVA: {prod['iva_porcentaje']}%")
    print(f"   Total: ${prod['total_item']:,.2f}")
    print()

print("\n" + "=" * 80)
print("TEST 2: PDF CON 20 PRODUCTOS")
print("=" * 80)

pdf_path2 = "/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML/6ee372e238cc82c3d95fa44faa0869cd5c6e0e45d51cef31b9828697aad65af8f2e3a89ff13f799961ad968c89503f8e.pdf"

text2 = extract_text_from_pdf(pdf_path2)
productos2 = extract_productos(text2)

print(f"\n✅ Productos extraídos: {len(productos2)}")
print(f"📋 Esperado: 20 productos\n")

for i, prod in enumerate(productos2[:5], 1):
    print(f"{i}. Código: {prod['codigo_producto']}")
    print(f"   Descripción: {prod['descripcion'][:50]}...")
    print(f"   Cantidad: {prod['cantidad']} {prod['unidad_medida']}")
    print(f"   Total: ${prod['total_item']:,.2f}")
    print()

if len(productos2) > 5:
    print(f"... y {len(productos2) - 5} productos más")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"PDF 1 (2 productos esperados): {len(productos1)} extraídos - {'✅ CORRECTO' if len(productos1) == 2 else '❌ INCORRECTO'}")
print(f"PDF 2 (20 productos esperados): {len(productos2)} extraídos - {'✅ CORRECTO' if len(productos2) == 20 else '❌ INCORRECTO'}")
