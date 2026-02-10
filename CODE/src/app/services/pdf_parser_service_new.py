"""
Servicio de parseo MEJORADO de PDFs DIAN
Extrae productos de facturas electrónicas con máxima precisión
"""
import re
from typing import Dict, Optional, List, Any
import logging

try:
    import pdfplumber
    PDF_LIBRARY_AVAILABLE = True
except ImportError:
    PDF_LIBRARY_AVAILABLE = False
    logging.warning("pdfplumber no está disponible")

logger = logging.getLogger(__name__)


class PDFParserServiceNew:
    """
    Parser MEJORADO para PDFs de facturas DIAN
    Maneja todos los formatos encontrados en producción
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str, max_pages: int = 999) -> str:
        """Extrae texto completo del PDF"""
        if not PDF_LIBRARY_AVAILABLE:
            logger.error("❌ pdfplumber no disponible")
            return ""
        
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                pages_to_process = min(len(pdf.pages), max_pages)
                logger.info(f"📄 Procesando {pages_to_process} páginas")
                
                for i in range(pages_to_process):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return '\n'.join(text_parts)
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return ""
    
    @staticmethod
    def _extract_productos(text: str) -> List[Dict[str, Any]]:
        """
        Extrae productos del PDF DIAN
        
        FORMATOS SOPORTADOS:
        1. Formato con código visible:
           "1 7706616340433 BANDERITAS ADH 5X20H/12X45MM MARFIL NIU 6,00 $ 1.600,00 $ 0,00 $ 0,00 $ 1.533,00 19.00 $ 8.067,00"
        
        2. Formato sin código (descripción en columna código):
           "1 94 2,00 $ 2.101,00 $ 0,00 $ 0,00 $ 798,38 19.00 $ 4.202,00"
           Con descripción en línea anterior: "CORDONES CORTOS PLANOS X 12"
        
        3. Formato con código numérico corto:
           "2 5676 NIU 24,00 $ 460,00 $ 0,00 $ 0,00 $ 11.040,00"
           Con descripción: "PERIODICO TAYDEM 1/32"
        """
        productos = []
        
        # Buscar sección de productos
        patterns = [
            r'Detalles de Productos([\s\S]+?)(?:Notas Finales|Datos Totales|Hoja \d+ de \d+)',
            r'DETALLE DE PRODUCTOS([\s\S]+?)(?:Notas Finales|Datos Totales)',
            r'Descripción\s+U/M\s+Cantidad([\s\S]+?)(?:Notas Finales|Datos Totales)',
        ]
        
        productos_section = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                productos_section = match.group(1)
                logger.info("✅ Sección de productos encontrada")
                break
        
        if not productos_section:
            logger.warning("⚠️ No se encontró sección de productos")
            return productos
        
        lines = productos_section.split('\n')
        i = 0
        
        while i < len(lines) and len(productos) < 200:
            line = lines[i].strip()
            
            # Saltar líneas vacías, encabezados y separadores
            if not line or line.startswith('---') or line.startswith('==='):
                i += 1
                continue
            
            # Detener en marcadores de fin
            if any(marker in line for marker in ['Notas Finales', 'Datos Totales', 'Hoja ', 'TOTAL ITEMS']):
                logger.info(f"🛑 Fin de productos detectado")
                break
            
            # Saltar encabezados de tabla
            if any(header in line for header in ['IMPUESTOS', 'Precio unitario', 'Descuento detalle', 'Nro. Código Descripción']):
                i += 1
                continue
            
            # ============================================================
            # FORMATO 1: Con código de barras/SKU largo (10-13 dígitos)
            # Ejemplo: "1 7706616340433 BANDERITAS ADH 5X20H/12X45MM MARFIL NIU 6,00 $ 1.600,00..."
            # ============================================================
            match1 = re.match(
                r'^(\d{1,3})\s+(\d{10,13})\s+(.+?)\s+(NIU|PK|BX|UND|UN|EA|PC)\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
                line
            )
            
            if match1:
                try:
                    nro = match1.group(1)
                    codigo = match1.group(2)
                    descripcion = match1.group(3).strip()
                    unidad = match1.group(4)
                    cantidad = float(match1.group(5).replace(',', '.'))
                    precio_unitario = float(match1.group(6).replace('.', '').replace(',', '.'))
                    
                    # Extraer IVA y total
                    iva_porcentaje = 0.0
                    iva_match = re.search(r'(\d{1,2})[.,]00\s+\$', line)
                    if iva_match:
                        iva_porcentaje = float(iva_match.group(1))
                    
                    # Total es el último valor monetario
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
                    logger.warning(f"⚠️ Error FORMATO 1: {e}")
            
            # ============================================================
            # FORMATO 2: Con código corto (3-9 dígitos)
            # Ejemplo: "2 5676 NIU 24,00 $ 460,00..."
            # Descripción puede estar en línea anterior
            # ============================================================
            match2 = re.match(
                r'^(\d{1,3})\s+(\d{3,9})\s+(NIU|PK|BX|UND|UN|EA|PC)\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
                line
            )
            
            if match2:
                try:
                    nro = match2.group(1)
                    codigo = match2.group(2)
                    unidad = match2.group(3)
                    cantidad = float(match2.group(4).replace(',', '.'))
                    precio_unitario = float(match2.group(5).replace('.', '').replace(',', '.'))
                    
                    # Buscar descripción en línea anterior
                    descripcion = f"Producto {nro}"
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        # Si la línea anterior no empieza con número, es descripción
                        if prev_line and not re.match(r'^\d+\s', prev_line):
                            # Verificar que no sea encabezado
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                                descripcion = prev_line
                    
                    # Extraer IVA y total
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
                    logger.warning(f"⚠️ Error FORMATO 2: {e}")
            
            # ============================================================
            # FORMATO 3: SIN código visible (descripción en columna código)
            # Ejemplo: "1 94 2,00 $ 2.101,00 $ 0,00 $ 0,00 $ 798,38 19.00 $ 4.202,00"
            # Descripción DEBE estar en línea anterior
            # ============================================================
            match3 = re.match(
                r'^(\d{1,3})\s+(\d{2})\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
                line
            )
            
            if match3:
                try:
                    nro = match3.group(1)
                    unidad_codigo = match3.group(2)  # 94 = NIU
                    cantidad = float(match3.group(3).replace(',', '.'))
                    precio_unitario = float(match3.group(4).replace('.', '').replace(',', '.'))
                    
                    # Mapear código de unidad
                    unidad_map = {'94': 'NIU', '10': 'PK', '11': 'BX', '01': 'UND'}
                    unidad = unidad_map.get(unidad_codigo, 'NIU')
                    
                    # Buscar descripción en línea ANTERIOR (obligatorio)
                    descripcion = f"Producto {nro}"
                    codigo = f"PROD{nro}"
                    
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        if prev_line and not re.match(r'^\d+\s', prev_line):
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código', 'U/M']):
                                descripcion = prev_line
                                # Usar primeras palabras como código
                                palabras = descripcion.split()
                                if palabras:
                                    codigo = ''.join(palabras[:2]).upper()[:20]
                    
                    # Extraer IVA y total
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
                    logger.warning(f"⚠️ Error FORMATO 3: {e}")
            
            # Si no coincide con ningún formato, avanzar
            i += 1
        
        logger.info(f"📊 Total productos extraídos: {len(productos)}")
        return productos
    
    @staticmethod
    def extract_cufe(text: str) -> Optional[str]:
        """Extrae CUFE (96 caracteres hexadecimales)"""
        pattern = r'[0-9a-fA-F]{96}'
        match = re.search(pattern, text)
        if match:
            return match.group(0).lower()
        return None
    
    @staticmethod
    def extract_invoice_number(text: str) -> Optional[str]:
        """Extrae número de factura"""
        patterns = [
            r'Número de Factura:\s*([A-Z0-9\-]+)',
            r'Factura:\s*([A-Z0-9\-]+)',
            r'No\.\s*Factura:\s*([A-Z0-9\-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    @staticmethod
    def extract_total(text: str) -> Optional[float]:
        """Extrae total de la factura"""
        patterns = [
            r'Total factura[^\$]*\$\s*([0-9.,]+)',
            r'TOTAL[^\$]*\$\s*([0-9.,]+)',
            r'Valor total[^\$]*\$\s*([0-9.,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    total_str = match.group(1).replace('.', '').replace(',', '.')
                    return float(total_str)
                except:
                    pass
        return None
