"""
Script para reemplazar el método _extract_productos con una versión mejorada
que maneja el formato de tabla con número de línea al inicio
"""

# Nuevo método mejorado
NUEVO_METODO = '''    @staticmethod
    def _extract_productos(text: str) -> List[Dict[str, Any]]:
        """
        Extrae productos del documento DIAN con TODA la información
        Para trazabilidad completa: código, descripción, cantidad, precio, IVA, total
        
        Soporta múltiples formatos:
        - Formato con número de línea: "1 7706616340433 BANDERITAS ADH... NIU 6.00 $ 1.600,00..."
        - Formato sin número: "7706616340433 BANDERITAS ADH... NIU 6.00 $ 1.600,00..."
        """
        productos = []
        
        # Buscar sección de productos con más variantes
        patterns = [
            # Patrón 1: Detalles de productos
            r'(?:Detalles de productos|Detalle de Ítems|DETALLE DE PRODUCTOS|DETALLE)([\\s\\S]{0,10000}?)(?:Notas finales|Datos totales|Observaciones|OBSERVACIONES|Total factura|TOTAL FACTURA|IVA=)',
            # Patrón 2: Descripción
            r'(?:DESCRIPCIÓN|DESCRIPCION|Descripción del Producto)([\\s\\S]{0,10000}?)(?:Notas|NOTAS|Total|TOTAL|IVA=|Observaciones)',
            # Patrón 3: Item
            r'(?:Item|ITEM|Ítem|ÍTEM)([\\s\\S]{0,10000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|IVA=)',
            # Patrón 4: Código Cantidad (formato común en facturas)
            r'(?:Código\\s+Cantidad|CODIGO\\s+CANTIDAD)([\\s\\S]{0,10000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|IVA=|Observaciones|DESPUES DE)',
            # Patrón 5: Tabla con headers (No. Código Descripción U/M Cantidad...)
            r'(?:No\\.\\s+Código\\s+Descripción|Código\\s+Descripción\\s+U/M)([\\s\\S]{0,10000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|Observaciones|OBSERVACIONES)',
        ]
        
        productos_section = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                productos_section = match.group(1)
                logger.info(f"✅ Sección de productos encontrada con patrón")
                break
        
        if not productos_section:
            logger.warning("⚠️ No se encontró sección de productos en el PDF")
            return productos
        
        # Dividir en líneas y procesar
        lines = productos_section.split('\\n')
        
        # Intentar detectar formato de tabla
        for i, line in enumerate(lines[:300]):  # Aumentar límite a 300 líneas
            line = line.strip()
            if len(line) < 10:
                continue
            
            # ESTRATEGIA 1: Formato con número de línea al inicio
            # Ejemplo: "1 7706616340433 BANDERITAS ADH 5X20H /12X45MM MARFIL NIU 6.00 $ 1.600,00 $ 0,00 $ 0,00 $ 1.533,00 19.00 $ 8.067,00"
            match_con_numero = re.match(
                r'^(\\d{1,3})\\s+'  # Número de línea
                r'(\\d{6,13})\\s+'  # Código de producto
                r'([A-ZÁÉÍÓÚÑ\\s\\d/\\-\\.]+?)\\s+'  # Descripción (letras mayúsculas, números, espacios)
                r'([A-Z]{2,4})\\s+'  # Unidad de medida (NIU, PK, KG, etc.)
                r'([0-9]{1,5}(?:[.,][0-9]{1,3})?)\\s+'  # Cantidad
                r'.*?'  # Resto de la línea (precios, IVA, etc.)
                r'([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)\\s*$',  # Precio final
                line,
                re.IGNORECASE
            )
            
            if match_con_numero:
                num_linea = match_con_numero.group(1)
                codigo = match_con_numero.group(2)
                descripcion = match_con_numero.group(3).strip()
                unidad_medida = match_con_numero.group(4)
                cantidad_str = match_con_numero.group(5).replace(',', '.')
                precio_final_str = match_con_numero.group(6).replace('.', '').replace(',', '.')
                
                try:
                    cantidad = float(cantidad_str)
                    precio_final = float(precio_final_str)
                    
                    # Buscar todos los valores monetarios en la línea
                    valores = re.findall(r'\\$\\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
                    
                    # Buscar IVA (número seguido de punto decimal, común: 19.00, 0.00, 5.00)
                    iva_match = re.search(r'\\s+(19\\.00|0\\.00|5\\.00|19|0|5)\\s+', line)
                    iva_porcentaje = float(iva_match.group(1)) if iva_match else None
                    
                    # Precio unitario es típicamente el primer valor después de la cantidad
                    precio_unitario = None
                    if len(valores) >= 1:
                        try:
                            precio_unitario = float(valores[0].replace('.', '').replace(',', '.'))
                        except:
                            pass
                    
                    # Calcular precio unitario desde el total si no lo encontramos
                    if not precio_unitario and cantidad > 0:
                        precio_unitario = precio_final / cantidad
                    
                    productos.append({
                        'codigo_producto': codigo,
                        'descripcion': descripcion[:250],
                        'cantidad': cantidad,
                        'unidad_medida': unidad_medida,
                        'precio_unitario': precio_unitario,
                        'iva_porcentaje': iva_porcentaje,
                        'total_item': precio_final,
                    })
                    
                    logger.info(f"✅ Producto extraído: {codigo} - {descripcion[:30]}... (${precio_final})")
                    
                    if len(productos) >= 150:
                        break
                    continue
                except Exception as e:
                    logger.warning(f"Error procesando línea con número: {e}")
            
            # ESTRATEGIA 2: Formato sin número de línea (código al inicio)
            # Ejemplo: "787138 BANDERIN... NIU 3.00 $ 1.600,00..."
            codigo_match = re.match(r'^(\\d{3,13})\\s+', line)
            
            if not codigo_match:
                # Intentar buscar código en cualquier parte
                codigo_match = re.search(r'\\b(\\d{6,13})\\b', line)
            
            if codigo_match:
                codigo = codigo_match.group(1)
                
                # Extraer el resto de la línea después del código
                resto_linea = line[codigo_match.end():].strip()
                
                # Buscar cantidad (número decimal al inicio del resto)
                cantidad = None
                cantidad_match = re.match(r'^([0-9]{1,5}(?:[.,][0-9]{1,3})?)\\s+', resto_linea)
                if cantidad_match:
                    try:
                        cant_str = cantidad_match.group(1).replace(',', '.')
                        cantidad = float(cant_str)
                        resto_linea = resto_linea[cantidad_match.end():].strip()
                    except:
                        pass
                
                # Buscar unidad de medida (UNIDAD, KG, NIU, PK, etc.)
                unidad_medida = None
                unidad_match = re.match(r'^([A-Z]{2,10})\\s+', resto_linea)
                if unidad_match:
                    unidad_medida = unidad_match.group(1)
                    resto_linea = resto_linea[unidad_match.end():].strip()
                
                # Buscar valores monetarios en la línea (precio unitario y total)
                valores_monetarios = re.findall(r'([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
                
                # Buscar porcentaje de IVA
                iva_porcentaje = None
                iva_match = re.search(r'(\\d{1,2}(?:[.,]\\d{1,2})?)\\s*%?', line)
                if not iva_match:
                    # Buscar "19.00" o "0.00" o "5.00" (común en facturas colombianas)
                    iva_match = re.search(r'\\s+(19\\.00|0\\.00|5\\.00|19|0|5)\\s+', line)
                if iva_match:
                    try:
                        iva_porcentaje = float(iva_match.group(1).replace(',', '.'))
                    except:
                        pass
                
                # Extraer descripción (lo que queda en resto_linea antes de los números finales)
                desc_clean = re.sub(r'\\s+\\d+[.,]?\\d*\\s+\\d+[.,]?\\d*\\s*$', '', resto_linea).strip()
                desc_clean = re.sub(r'\\s+REF:.*$', '', desc_clean, flags=re.IGNORECASE).strip()
                desc_clean = re.sub(r'\\s+-MARCA:.*$', '', desc_clean, flags=re.IGNORECASE).strip()
                desc_clean = re.sub(r'\\s+', ' ', desc_clean)  # Normalizar espacios
                
                # Extraer precio unitario y total de los valores monetarios
                precio_unitario = None
                total_item = None
                
                if len(valores_monetarios) >= 2:
                    try:
                        # Los últimos dos valores suelen ser precio unitario y total
                        precio_str = valores_monetarios[-2].replace('.', '').replace(',', '.')
                        precio_unitario = float(precio_str)
                        
                        total_str = valores_monetarios[-1].replace('.', '').replace(',', '.')
                        total_item = float(total_str)
                    except:
                        pass
                elif len(valores_monetarios) == 1:
                    try:
                        # Solo un valor, probablemente el total
                        total_str = valores_monetarios[0].replace('.', '').replace(',', '.')
                        total_item = float(total_str)
                    except:
                        pass
                
                # Validar que tenemos al menos código y descripción
                if codigo and desc_clean and len(desc_clean) > 3:
                    productos.append({
                        'codigo_producto': codigo,
                        'descripcion': desc_clean[:250],
                        'cantidad': cantidad,
                        'unidad_medida': unidad_medida,
                        'precio_unitario': precio_unitario,
                        'iva_porcentaje': iva_porcentaje,
                        'total_item': total_item,
                    })
                    
                    # Limitar a 150 productos por factura
                    if len(productos) >= 150:
                        break
        
        logger.info(f"✅ Extraídos {len(productos)} productos del PDF")
        return productos'''

print("Método mejorado guardado en fix_parser_productos.py")
print("\nPara aplicar el fix:")
print("1. Abre CODE/src/app/services/pdf_parser_service.py")
print("2. Busca el método _extract_productos (línea ~597)")
print("3. Reemplaza todo el método con el contenido de este archivo")
print("\nO ejecuta el script de reemplazo automático")
