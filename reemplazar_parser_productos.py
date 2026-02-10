#!/usr/bin/env python3
"""
Reemplazar el método _extract_productos con la versión mejorada
"""
import re

# Leer el archivo actual
with open('CODE/src/app/services/pdf_parser_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Nuevo método mejorado
nuevo_metodo = '''    @staticmethod
    def _extract_productos(text: str) -> List[Dict[str, Any]]:
        """
        Extrae productos del PDF DIAN - VERSIÓN MEJORADA
        
        FORMATOS SOPORTADOS:
        1. Con código largo (10-13 dígitos) + descripción
        2. Con código largo SIN descripción (descripción en línea anterior/siguiente)
        3. Con código corto (3-9 dígitos) + descripción
        4. Con código corto SIN descripción
        5. SIN código (solo U/M código como 94) - descripción en línea anterior
        """
        productos = []
        
        # Buscar sección de productos
        patterns = [
            r'Detalles de Productos([\\s\\S]+?)(?:Notas Finales|Datos Totales|Hoja \\d+ de \\d+)',
            r'DETALLE DE PRODUCTOS([\\s\\S]+?)(?:Notas Finales|Datos Totales)',
            r'Descripción\\s+U/M\\s+Cantidad([\\s\\S]+?)(?:Notas Finales|Datos Totales)',
        ]
        
        productos_section = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                productos_section = match.group(1)
                logger.info("Sección de productos encontrada")
                break
        
        if not productos_section:
            logger.warning("No se encontró sección de productos")
            return productos
        
        lines = productos_section.split('\\n')
        i = 0
        
        while i < len(lines) and len(productos) < 200:
            line = lines[i].strip()
            
            # Saltar líneas vacías, encabezados y separadores
            if not line or line.startswith('---') or line.startswith('==='):
                i += 1
                continue
            
            # Detener en marcadores de fin
            if any(marker in line for marker in ['Notas Finales', 'Datos Totales', 'Hoja ', 'TOTAL ITEMS']):
                logger.info("Fin de productos detectado")
                break
            
            # Saltar encabezados de tabla
            if any(header in line for header in ['IMPUESTOS', 'Precio unitario', 'Descuento detalle', 'Nro. Código Descripción']):
                i += 1
                continue
            
            # FORMATO 1A: Con código largo (10-13 dígitos) Y descripción
            match1a = re.match(
                r'^(\\d{1,3})\\s+(\\d{10,13})\\s+(.+?)\\s+(NIU|PK|BX|UND|UN|EA|PC)\\s+([0-9]+[.,][0-9]{2})\\s+\\$\\s*([0-9.,]+)',
                line
            )
            
            # FORMATO 1B: Con código largo (10-13 dígitos) SIN descripción
            match1b = re.match(
                r'^(\\d{1,3})\\s+(\\d{10,13})\\s+(NIU|PK|BX|UND|UN|EA|PC)\\s+([0-9]+[.,][0-9]{2})\\s+\\$\\s*([0-9.,]+)',
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
                    iva_match = re.search(r'(\\d{1,2})[.,]00\\s+\\$', line)
                    if iva_match:
                        iva_porcentaje = float(iva_match.group(1))
                    
                    valores = re.findall(r'\\$\\s*([0-9.,]+)', line)
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
                    
                    logger.info(f"Producto {nro}: {codigo} - {descripcion[:30]}...")
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
                    
                    descripcion = f"Producto {nro}"
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        if prev_line and not re.match(r'^\\d+\\s', prev_line):
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                                descripcion = prev_line
                    
                    if i + 1 < len(lines):
                        next_line = lines[i+1].strip()
                        if next_line and not re.match(r'^\\d+\\s', next_line):
                            if not any(h in next_line for h in ['Hoja ', 'IMPUESTOS', 'Precio']):
                                descripcion = f"{descripcion} {next_line}".strip()
                    
                    iva_porcentaje = 0.0
                    iva_match = re.search(r'(\\d{1,2})[.,]00\\s+\\$', line)
                    if iva_match:
                        iva_porcentaje = float(iva_match.group(1))
                    
                    valores = re.findall(r'\\$\\s*([0-9.,]+)', line)
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
                    
                    logger.info(f"Producto {nro}: {codigo} - {descripcion[:30]}...")
                    i += 1
                    continue
                    
                except Exception as e:
                    logger.warning(f"Error FORMATO 1B: {e}")
            
            # FORMATO 2A: Con código corto (3-9 dígitos) Y descripción
            match2a = re.match(
                r'^(\\d{1,3})\\s+(\\d{3,9})\\s+(.+?)\\s+(NIU|PK|BX|UND|UN|EA|PC)\\s+([0-9]+[.,][0-9]{2})\\s+\\$\\s*([0-9.,]+)',
                line
            )
            
            # FORMATO 2B: Con código corto (3-9 dígitos) SIN descripción
            match2b = re.match(
                r'^(\\d{1,3})\\s+(\\d{3,9})\\s+(NIU|PK|BX|UND|UN|EA|PC)\\s+([0-9]+[.,][0-9]{2})\\s+\\$\\s*([0-9.,]+)',
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
                    
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        if prev_line and not re.match(r'^\\d+\\s', prev_line):
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                                descripcion = f"{prev_line} {descripcion}".strip()
                    
                    if i + 1 < len(lines):
                        next_line = lines[i+1].strip()
                        if next_line and not re.match(r'^\\d+\\s', next_line):
                            if not any(h in next_line for h in ['Hoja ', 'IMPUESTOS', 'Precio']):
                                descripcion = f"{descripcion} {next_line}".strip()
                    
                    iva_porcentaje = 0.0
                    iva_match = re.search(r'(\\d{1,2})[.,]00\\s+\\$', line)
                    if iva_match:
                        iva_porcentaje = float(iva_match.group(1))
                    
                    valores = re.findall(r'\\$\\s*([0-9.,]+)', line)
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
                    
                    logger.info(f"Producto {nro}: {codigo} - {descripcion[:30]}...")
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
                        if prev_line and not re.match(r'^\\d+\\s', prev_line):
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                                descripcion = prev_line
                    
                    iva_porcentaje = 0.0
                    iva_match = re.search(r'(\\d{1,2})[.,]00\\s+\\$', line)
                    if iva_match:
                        iva_porcentaje = float(iva_match.group(1))
                    
                    valores = re.findall(r'\\$\\s*([0-9.,]+)', line)
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
                    
                    logger.info(f"Producto {nro}: {codigo} - {descripcion[:30]}...")
                    i += 1
                    continue
                    
                except Exception as e:
                    logger.warning(f"Error FORMATO 2B: {e}")
            
            # FORMATO 3: SIN código (solo U/M código como 94)
            match3 = re.match(
                r'^(\\d{1,3})\\s+(\\d{2})\\s+([0-9]+[.,][0-9]{2})\\s+\\$\\s*([0-9.,]+)',
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
                        if prev_line and not re.match(r'^\\d+\\s', prev_line):
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código', 'U/M']):
                                descripcion = prev_line
                                palabras = descripcion.split()
                                if palabras:
                                    codigo = ''.join(palabras[:2]).upper()[:20]
                    
                    iva_porcentaje = 0.0
                    iva_match = re.search(r'(\\d{1,2})[.,]00\\s+\\$', line)
                    if iva_match:
                        iva_porcentaje = float(iva_match.group(1))
                    
                    valores = re.findall(r'\\$\\s*([0-9.,]+)', line)
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
                    
                    logger.info(f"Producto {nro}: {codigo} - {descripcion[:30]}...")
                    i += 1
                    continue
                    
                except Exception as e:
                    logger.warning(f"Error FORMATO 3: {e}")
            
            i += 1
        
        logger.info(f"Total productos extraídos: {len(productos)}")
        return productos'''

# Buscar y reemplazar el método completo
# El método empieza en @staticmethod def _extract_productos y termina antes del siguiente @staticmethod
pattern = r'(@staticmethod\s+def _extract_productos\(text: str\) -> List\[Dict\[str, Any\]\]:.*?)((?=\n    @staticmethod|\Z))'

match = re.search(pattern, content, re.DOTALL)

if match:
    print("✅ Método _extract_productos encontrado")
    print(f"   Posición: {match.start()} - {match.end()}")
    print(f"   Longitud actual: {len(match.group(1))} caracteres")
    
    # Reemplazar
    nuevo_content = content[:match.start()] + nuevo_metodo + '\n    ' + content[match.end():]
    
    # Guardar
    with open('CODE/src/app/services/pdf_parser_service.py', 'w', encoding='utf-8') as f:
        f.write(nuevo_content)
    
    print("✅ Método reemplazado exitosamente")
    print(f"   Longitud nuevo: {len(nuevo_metodo)} caracteres")
else:
    print("❌ No se encontró el método _extract_productos")
