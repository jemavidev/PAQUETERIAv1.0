#!/usr/bin/env python3
"""
Script para aplicar el fix del parser de productos
Reemplaza el método _extract_productos con la versión mejorada
"""
import re

# Leer el archivo original
with open('src/app/services/pdf_parser_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Nuevo método mejorado (sin emojis ni caracteres especiales)
nuevo_metodo = '''    @staticmethod
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
            r'(?:Detalles de productos|Detalle de Ítems|DETALLE DE PRODUCTOS|DETALLE)([\\s\\S]{0,10000}?)(?:Notas finales|Datos totales|Observaciones|OBSERVACIONES|Total factura|TOTAL FACTURA|IVA=)',
            r'(?:DESCRIPCIÓN|DESCRIPCION|Descripción del Producto)([\\s\\S]{0,10000}?)(?:Notas|NOTAS|Total|TOTAL|IVA=|Observaciones)',
            r'(?:Item|ITEM|Ítem|ÍTEM)([\\s\\S]{0,10000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|IVA=)',
            r'(?:Código\\s+Cantidad|CODIGO\\s+CANTIDAD)([\\s\\S]{0,10000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|IVA=|Observaciones|DESPUES DE)',
            r'(?:No\\.\\s+Código\\s+Descripción|Código\\s+Descripción\\s+U/M)([\\s\\S]{0,10000}?)(?:Subtotal|SUBTOTAL|Total|TOTAL|Observaciones|OBSERVACIONES)',
        ]
        
        productos_section = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                productos_section = match.group(1)
                logger.info(f"Seccion de productos encontrada con patron")
                break
        
        if not productos_section:
            logger.warning("No se encontro seccion de productos en el PDF")
            return productos
        
        lines = productos_section.split('\\n')
        
        for i, line in enumerate(lines[:300]):
            line = line.strip()
            if len(line) < 10:
                continue
            
            # ESTRATEGIA 1: Formato con número de línea al inicio
            match_con_numero = re.match(
                r'^(\\d{1,3})\\s+(\\d{6,13})\\s+([A-ZÁÉÍÓÚÑ\\s\\d/\\-\\.]+?)\\s+([A-Z]{2,4})\\s+([0-9]{1,5}(?:[.,][0-9]{1,3})?)\\s+.*?([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)\\s*$',
                line,
                re.IGNORECASE
            )
            
            if match_con_numero:
                try:
                    num_linea = match_con_numero.group(1)
                    codigo = match_con_numero.group(2)
                    descripcion = match_con_numero.group(3).strip()
                    unidad_medida = match_con_numero.group(4)
                    cantidad_str = match_con_numero.group(5).replace(',', '.')
                    precio_final_str = match_con_numero.group(6).replace('.', '').replace(',', '.')
                    
                    cantidad = float(cantidad_str)
                    precio_final = float(precio_final_str)
                    
                    valores = re.findall(r'\\$\\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
                    iva_match = re.search(r'\\s+(19\\.00|0\\.00|5\\.00|19|0|5)\\s+', line)
                    iva_porcentaje = float(iva_match.group(1)) if iva_match else None
                    
                    precio_unitario = None
                    if len(valores) >= 1:
                        try:
                            precio_unitario = float(valores[0].replace('.', '').replace(',', '.'))
                        except:
                            pass
                    
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
                    
                    logger.info(f"Producto extraido: {codigo} - {descripcion[:30]}... (${precio_final})")
                    
                    if len(productos) >= 150:
                        break
                    continue
                except Exception as e:
                    logger.warning(f"Error procesando linea con numero: {e}")
            
            # ESTRATEGIA 2: Formato sin número de línea
            codigo_match = re.match(r'^(\\d{3,13})\\s+', line)
            if not codigo_match:
                codigo_match = re.search(r'\\b(\\d{6,13})\\b', line)
            
            if codigo_match:
                codigo = codigo_match.group(1)
                resto_linea = line[codigo_match.end():].strip()
                
                cantidad = None
                cantidad_match = re.match(r'^([0-9]{1,5}(?:[.,][0-9]{1,3})?)\\s+', resto_linea)
                if cantidad_match:
                    try:
                        cant_str = cantidad_match.group(1).replace(',', '.')
                        cantidad = float(cant_str)
                        resto_linea = resto_linea[cantidad_match.end():].strip()
                    except:
                        pass
                
                unidad_medida = None
                unidad_match = re.match(r'^([A-Z]{2,10})\\s+', resto_linea)
                if unidad_match:
                    unidad_medida = unidad_match.group(1)
                    resto_linea = resto_linea[unidad_match.end():].strip()
                
                valores_monetarios = re.findall(r'([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)', line)
                
                iva_porcentaje = None
                iva_match = re.search(r'(\\d{1,2}(?:[.,]\\d{1,2})?)\\s*%?', line)
                if not iva_match:
                    iva_match = re.search(r'\\s+(19\\.00|0\\.00|5\\.00|19|0|5)\\s+', line)
                if iva_match:
                    try:
                        iva_porcentaje = float(iva_match.group(1).replace(',', '.'))
                    except:
                        pass
                
                desc_clean = re.sub(r'\\s+\\d+[.,]?\\d*\\s+\\d+[.,]?\\d*\\s*$', '', resto_linea).strip()
                desc_clean = re.sub(r'\\s+REF:.*$', '', desc_clean, flags=re.IGNORECASE).strip()
                desc_clean = re.sub(r'\\s+-MARCA:.*$', '', desc_clean, flags=re.IGNORECASE).strip()
                desc_clean = re.sub(r'\\s+', ' ', desc_clean)
                
                precio_unitario = None
                total_item = None
                
                if len(valores_monetarios) >= 2:
                    try:
                        precio_str = valores_monetarios[-2].replace('.', '').replace(',', '.')
                        precio_unitario = float(precio_str)
                        total_str = valores_monetarios[-1].replace('.', '').replace(',', '.')
                        total_item = float(total_str)
                    except:
                        pass
                elif len(valores_monetarios) == 1:
                    try:
                        total_str = valores_monetarios[0].replace('.', '').replace(',', '.')
                        total_item = float(total_str)
                    except:
                        pass
                
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
                    
                    if len(productos) >= 150:
                        break
        
        logger.info(f"Extraidos {len(productos)} productos del PDF")
        return productos'''

# Buscar y reemplazar el método
# Usar regex para encontrar el método completo
pattern = r'(@staticmethod\s+def _extract_productos\(text: str\) -> List\[Dict\[str, Any\]\]:.*?)((?=\n    @staticmethod|\n    def [a-z_]+\(|\Z))'

match = re.search(pattern, content, re.DOTALL)

if match:
    # Reemplazar el método
    content_nuevo = content[:match.start()] + nuevo_metodo + '\n    ' + content[match.end():]
    
    # Guardar el archivo
    with open('src/app/services/pdf_parser_service.py', 'w', encoding='utf-8') as f:
        f.write(content_nuevo)
    
    print("✅ Parser actualizado exitosamente!")
    print("✅ El método _extract_productos ahora soporta:")
    print("   - Formato con número de línea al inicio")
    print("   - Formato sin número de línea (fallback)")
    print("\n📋 Próximos pasos:")
    print("   1. Reiniciar el servidor")
    print("   2. Cargar una factura DIAN de prueba")
    print("   3. Verificar que se extraen todos los productos")
else:
    print("❌ No se pudo encontrar el método _extract_productos")
    print("   Verifica que el archivo no haya sido modificado")
