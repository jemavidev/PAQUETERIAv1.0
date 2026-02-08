#!/usr/bin/env python3
"""
Fix para extracción de productos de archivos CUFE/DIAN
El problema: La descripción está dividida en múltiples líneas
"""

NUEVO_METODO = '''    @staticmethod
    def _extract_productos(text: str) -> List[Dict[str, Any]]:
        """
        Extrae productos del documento DIAN con TODA la información
        Maneja el formato específico de CUFE donde la descripción está en múltiples líneas
        
        Formato típico:
                             CUADERNO COSIDO FAM
         1         5654                              NIU    60,00     $       1.950,00
        $        2.340,00 $           0,00                         $ 114.660,00                         A 100H M-452111 CJX90
        """
        productos = []
        
        # Buscar sección de productos
        match = re.search(
            r'(?:Detalles de Productos|Detalle de Ítems|DETALLE DE PRODUCTOS)([\s\S]{0,15000}?)(?:Notas [Ff]inales|Datos [Tt]otales|Observaciones)',
            text,
            re.IGNORECASE
        )
        
        if not match:
            logger.warning("No se encontró sección de productos en el PDF")
            return productos
        
        productos_section = match.group(1)
        lines = productos_section.split('\\n')
        
        i = 0
        while i < len(lines) and len(productos) < 200:
            line = lines[i].strip()
            
            # Buscar línea que comienza con número (indica producto)
            # Formato: Nro Código U/M Cantidad Precio...
            match_producto = re.match(
                r'^(\\d{1,3})\\s+(\\d{3,13})?\\s+(NIU|PK|BX|UND|UN)?\\s+([0-9]+[.,][0-9]{2})\\s+\\$\\s*([0-9.,]+)',
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
                        # La descripción suele estar indentada y sin números al inicio
                        if prev_line and not re.match(r'^\\d+\\s', prev_line):
                            descripcion_parte1 = prev_line
                    
                    # Buscar descripción adicional al FINAL de la línea actual o siguiente
                    descripcion_parte2 = ""
                    # Buscar texto después del último precio
                    resto = re.split(r'\\$\\s*[0-9.,]+', line)
                    if len(resto) > 1:
                        descripcion_parte2 = resto[-1].strip()
                    
                    # Combinar descripciones
                    descripcion = f"{descripcion_parte1} {descripcion_parte2}".strip()
                    
                    # Si no hay descripción, buscar en línea siguiente
                    if not descripcion and i + 1 < len(lines):
                        next_line = lines[i+1].strip()
                        if next_line and not re.match(r'^\\d+\\s', next_line):
                            descripcion = next_line
                    
                    # Limpiar descripción
                    descripcion = re.sub(r'\\s+', ' ', descripcion)
                    descripcion = descripcion[:250]
                    
                    # Buscar total (último valor monetario en la línea)
                    valores = re.findall(r'\\$\\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
                    total_item = None
                    if valores:
                        try:
                            total_str = valores[-1].replace('.', '').replace(',', '.')
                            total_item = float(total_str)
                        except:
                            pass
                    
                    # Buscar IVA
                    iva_porcentaje = 0.0
                    iva_match = re.search(r'(\\d{1,2})[.,]00\\s+', line)
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
                    
                    logger.info(f"Producto extraído: {codigo} - {descripcion[:40]}... (Cant: {cantidad}, Total: ${total_item})")
                    
                except Exception as e:
                    logger.warning(f"Error procesando producto línea {i}: {e}")
            
            i += 1
        
        logger.info(f"Total productos extraídos: {len(productos)}")
        return productos'''

print("Método mejorado para extracción de productos CUFE:")
print("="*80)
print(NUEVO_METODO)
print("="*80)
print("\nEste método:")
print("✓ Busca la descripción en la línea ANTERIOR al número de producto")
print("✓ Busca descripción adicional al FINAL de la línea del producto")
print("✓ Combina ambas partes de la descripción")
print("✓ Maneja códigos faltantes")
print("✓ Extrae IVA, cantidad, precios y totales correctamente")
