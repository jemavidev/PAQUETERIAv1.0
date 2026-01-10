# ========================================
# PAQUETES EL CLUB - Servicio de Extracción de PDFs
# ========================================
"""
Servicio para extraer datos de facturas electrónicas y documentos POS.
Implementa mejores prácticas para análisis de datos:
- Normalización de datos
- Validación de integridad
- Detección de inconsistencias
- Formato Colombia (separador de miles, sin decimales)
- Soporte para PDFs de múltiples páginas
"""

import re
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP

import pdfplumber

from app.schemas.invoice import (
    DocumentTypeEnum,
    ExtractedInvoiceData,
    InvoiceItemReview,
    ExtractionWarning,
)

logger = logging.getLogger(__name__)


class PDFExtractorService:
    """Servicio para extraer y normalizar datos de PDFs de facturas"""
    
    # Patrones de regex compilados - MEJORADOS para mayor flexibilidad
    PATTERNS = {
        # CUFE/CUDE - más flexibles (64-96 caracteres hex)
        'cufe': re.compile(r'CUFE\s*:?\s*\n?\s*([a-f0-9]{64,96})', re.IGNORECASE),
        'cude': re.compile(r'CUDE\s*:?\s*\n?\s*([a-f0-9]{64,96})', re.IGNORECASE),
        'cufe_alt': re.compile(r'(?:Código\s+único|CUFE|Clave)\s*:?\s*\n?\s*([a-f0-9]{64,96})', re.IGNORECASE),
        
        # Número de factura - múltiples formatos
        'numero_factura': re.compile(r'(?:Número\s+de\s+Factura|No\.\s*Factura|Factura\s+No\.?|N[úu]mero)\s*:?\s*([A-Z0-9\-]+)', re.IGNORECASE),
        'numero_documento_pos': re.compile(r'(?:Número\s+de\s+documento|Doc(?:umento)?\.?\s*No\.?)\s*:?\s*([A-Z0-9\-]+)', re.IGNORECASE),
        
        # Fechas - múltiples formatos
        'fecha_emision': re.compile(r'(?:Fecha\s+de\s+Emisi[oó]n|Fecha\s+Emisi[oó]n|Fecha)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', re.IGNORECASE),
        'fecha_expedicion': re.compile(r'(?:Fecha\s+y\s+hora\s+de\s+expedici[oó]n|Fecha\s+expedici[oó]n)\s*:?\s*([^\n]+)', re.IGNORECASE),
        'fecha_vencimiento': re.compile(r'(?:Fecha\s+de\s+Vencimiento|Vencimiento)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', re.IGNORECASE),
        
        # Forma y medio de pago
        'forma_pago': re.compile(r'(?:Forma\s+de\s+pago|Condici[oó]n\s+de\s+pago)\s*:?\s*([^\n]+)', re.IGNORECASE),
        'medio_pago': re.compile(r'(?:Medio\s+de\s+Pago|M[ée]todo\s+de\s+pago)\s*:?\s*([^\n]+)', re.IGNORECASE),
        
        # Datos del emisor/vendedor - múltiples formatos
        'vendedor_razon_social': re.compile(r'(?:Datos\s+del\s+Emisor|Emisor|Vendedor).*?(?:Raz[oó]n\s+Social|Nombre)\s*:?\s*([^\n]+)', re.DOTALL | re.IGNORECASE),
        'vendedor_razon_alt': re.compile(r'(?:Raz[oó]n\s+Social|Nombre\s+o\s+raz[oó]n)\s*:?\s*([^\n]+)', re.IGNORECASE),
        'vendedor_nit': re.compile(r'(?:Nit\s+del\s+Emisor|NIT|N\.I\.T\.?)\s*:?\s*(\d[\d\.\-]*\d)', re.IGNORECASE),
        'vendedor_nit_alt': re.compile(r'(?:Identificaci[oó]n|Documento)\s*:?\s*(\d{5,15})', re.IGNORECASE),
        'vendedor_direccion': re.compile(r'(?:Direcci[oó]n)\s*:?\s*([^\n]+)', re.IGNORECASE),
        'vendedor_telefono': re.compile(r'(?:Tel[ée]fono|M[oó]vil|Celular)\s*[:/]?\s*([^\n]+)', re.IGNORECASE),
        'vendedor_correo': re.compile(r'(?:Correo|Email|E-mail)\s*:?\s*([^\s\n]+@[^\s\n]+)', re.IGNORECASE),
        'vendedor_departamento': re.compile(r'(?:Departamento)\s*:?\s*([^\n]+)', re.IGNORECASE),
        'vendedor_ciudad': re.compile(r'(?:Municipio|Ciudad)\s*[:/]?\s*([^\n]+)', re.IGNORECASE),
        
        # POS específicos
        'vendedor_pos_razon': re.compile(r'(?:Datos\s+del\s+vendedor|Vendedor).*?(?:Raz[oó]n\s+social|Nombre)\s*:?\s*([^\n]+)', re.DOTALL | re.IGNORECASE),
        'vendedor_pos_nit': re.compile(r'(?:N[úu]mero\s+de\s+documento|NIT)\s*:?\s*(\d{5,15})', re.IGNORECASE),
        
        # Totales - más flexibles
        'subtotal': re.compile(r'(?:Sub\s*total|Subtotal)\s*:?\s*\$?\s*([\d\.,]+)', re.IGNORECASE),
        'total_iva': re.compile(r'(?:Total\s+)?IVA\s*(?:\d+%?)?\s*:?\s*\$?\s*([\d\.,]+)', re.IGNORECASE),
        'total_neto': re.compile(r'(?:Total\s+(?:neto|a\s+pagar|factura)|Gran\s+Total|TOTAL)\s*:?\s*\$?\s*([\d\.,]+)', re.IGNORECASE),
        'descuento': re.compile(r'(?:Descuento|Dcto\.?)\s*:?\s*\$?\s*([\d\.,]+)', re.IGNORECASE),
    }
    
    def __init__(self):
        self.warnings: List[ExtractionWarning] = []
        self.full_text: str = ""  # Texto completo de todas las páginas

    # ========================================
    # Métodos de Normalización de Datos
    # ========================================
    
    @staticmethod
    def normalize_money(value: str) -> int:
        """
        Convierte un valor monetario a entero (pesos colombianos sin decimales).
        Maneja formatos: $1.234,56 | 1234.56 | 1,234.56 | 1234
        """
        if not value:
            return 0
        
        cleaned = re.sub(r'[$\s]', '', str(value))
        if not cleaned:
            return 0
        
        try:
            # Detectar formato colombiano vs americano
            if ',' in cleaned and '.' in cleaned:
                if cleaned.rfind(',') > cleaned.rfind('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                parts = cleaned.split(',')
                if len(parts[-1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            elif '.' in cleaned:
                parts = cleaned.split('.')
                if len(parts[-1]) == 3 and len(parts) > 1:
                    cleaned = cleaned.replace('.', '')
            
            decimal_value = Decimal(cleaned)
            rounded = decimal_value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            return int(rounded)
        except Exception as e:
            logger.warning(f"Error normalizando valor monetario '{value}': {e}")
            return 0
    
    @staticmethod
    def normalize_quantity(value: str) -> int:
        """Convierte cantidad a entero"""
        if not value:
            return 1
        try:
            cleaned = re.sub(r'[^\d.,\-]', '', str(value))
            if ',' in cleaned:
                cleaned = cleaned.replace(',', '.')
            result = int(float(cleaned))
            return result if result > 0 else 1
        except:
            return 1
    
    @staticmethod
    def normalize_percentage(value: str) -> float:
        """Normaliza porcentaje a float"""
        if not value:
            return 0.0
        try:
            cleaned = re.sub(r'[^\d.,]', '', str(value))
            if ',' in cleaned:
                cleaned = cleaned.replace(',', '.')
            return float(cleaned)
        except:
            return 0.0
    
    @staticmethod
    def normalize_code(value: str) -> str:
        """Normaliza código de producto - mantiene como texto"""
        if not value:
            return ""
        cleaned = str(value).strip()
        # Permitir más caracteres en códigos
        cleaned = re.sub(r'[^\w\-\./]', '', cleaned)
        return cleaned[:50]  # Limitar longitud
    
    @staticmethod
    def normalize_text(value: str) -> str:
        """Normaliza texto: trim, espacios múltiples, saltos de línea"""
        if not value:
            return ""
        cleaned = str(value).strip()
        cleaned = re.sub(r'[\n\r]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned[:500]  # Limitar longitud
    
    @staticmethod
    def normalize_nit(value: str) -> str:
        """Normaliza NIT: solo dígitos"""
        if not value:
            return ""
        return re.sub(r'[^\d]', '', str(value))[:15]  # Limitar a 15 dígitos
    
    @staticmethod
    def parse_date(value: str) -> Optional[datetime]:
        """Parsea fecha en varios formatos"""
        if not value:
            return None
        
        # Limpiar el valor
        cleaned = re.sub(r'[+-]\d{2}:\d{2}$', '', str(value).strip())
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y', 
            '%Y-%m-%d',
            '%d/%m/%y',
            '%d-%m-%y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(cleaned.split()[0] if ' ' in cleaned and fmt.count(' ') == 0 else cleaned, fmt)
            except ValueError:
                continue
        
        # Intentar extraer solo la fecha si hay texto adicional
        date_match = re.search(r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', cleaned)
        if date_match:
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']:
                try:
                    return datetime.strptime(date_match.group(1), fmt)
                except ValueError:
                    continue
        
        return None


    # ========================================
    # Métodos de Extracción
    # ========================================
    
    def _extract_all_text(self, pdf: pdfplumber.PDF) -> str:
        """Extrae texto de TODAS las páginas del PDF"""
        all_text = []
        for i, page in enumerate(pdf.pages):
            try:
                text = page.extract_text() or ''
                all_text.append(f"--- PÁGINA {i+1} ---\n{text}")
                logger.debug(f"Página {i+1}: {len(text)} caracteres extraídos")
            except Exception as e:
                logger.warning(f"Error extrayendo texto de página {i+1}: {e}")
                all_text.append(f"--- PÁGINA {i+1} (ERROR) ---")
        
        return '\n'.join(all_text)
    
    def _extract_match(self, pattern_name: str, text: str = None) -> Optional[str]:
        """Extrae un valor usando un patrón predefinido"""
        search_text = text if text else self.full_text
        pattern = self.PATTERNS.get(pattern_name)
        if not pattern:
            return None
        match = pattern.search(search_text)
        return match.group(1).strip() if match else None
    
    def _extract_with_fallback(self, primary_pattern: str, fallback_patterns: List[str], text: str = None) -> Optional[str]:
        """Intenta extraer con patrón primario, luego con fallbacks"""
        result = self._extract_match(primary_pattern, text)
        if result:
            return result
        
        for pattern in fallback_patterns:
            result = self._extract_match(pattern, text)
            if result:
                logger.debug(f"Usando patrón fallback '{pattern}' para extraer dato")
                return result
        
        return None
    
    def _detect_document_type(self, text: str) -> DocumentTypeEnum:
        """Detecta el tipo de documento buscando en todo el texto"""
        text_upper = text.upper()
        
        # Buscar indicadores de factura electrónica
        factura_indicators = [
            'FACTURA ELECTRÓNICA',
            'FACTURA ELECTRONICA',
            'FACTURA ELECTRÓNICA DE VENTA',
            'FACTURA DE VENTA',
            'CUFE:',
            'CUFE :',
        ]
        
        # Buscar indicadores de POS
        pos_indicators = [
            'DOCUMENTO EQUIVALENTE POS',
            'DOCUMENTO POS',
            'CUDE:',
            'CUDE :',
            'TIQUETE POS',
        ]
        
        for indicator in factura_indicators:
            if indicator in text_upper:
                logger.debug(f"Detectado tipo FACTURA por indicador: {indicator}")
                return DocumentTypeEnum.FACTURA
        
        for indicator in pos_indicators:
            if indicator in text_upper:
                logger.debug(f"Detectado tipo POS por indicador: {indicator}")
                return DocumentTypeEnum.POS
        
        # Si no se detecta, asumir factura pero agregar warning
        self._add_warning("document_type", "No se pudo detectar el tipo de documento, asumiendo Factura", severity="warning")
        return DocumentTypeEnum.FACTURA
    
    def _add_warning(self, field: str, message: str, original_value: str = None,
                     suggested_value: str = None, severity: str = "warning"):
        """Agrega una advertencia a la lista"""
        self.warnings.append(ExtractionWarning(
            field=field, message=message, original_value=original_value,
            suggested_value=suggested_value, severity=severity
        ))
    
    def _extract_cufe_cude(self, doc_type: DocumentTypeEnum) -> str:
        """Extrae CUFE o CUDE buscando en todo el documento"""
        if doc_type == DocumentTypeEnum.FACTURA:
            cufe = self._extract_with_fallback('cufe', ['cufe_alt'])
            if cufe:
                return cufe
        else:
            cude = self._extract_match('cude')
            if cude:
                return cude
        
        # Búsqueda más agresiva - buscar cualquier cadena hex larga
        hex_pattern = re.compile(r'\b([a-f0-9]{64,96})\b', re.IGNORECASE)
        matches = hex_pattern.findall(self.full_text)
        if matches:
            # Tomar la más larga
            longest = max(matches, key=len)
            logger.debug(f"CUFE/CUDE encontrado por búsqueda hex: {longest[:20]}...")
            return longest
        
        return ""
    
    def _extract_supplier(self, doc_type: DocumentTypeEnum) -> Dict[str, str]:
        """Extrae datos del proveedor buscando en todo el documento"""
        supplier = {
            'nit': '',
            'razon_social': '',
            'direccion': '',
            'telefono': '',
            'correo': '',
            'departamento': '',
            'ciudad': '',
        }
        
        # NIT - intentar múltiples patrones
        if doc_type == DocumentTypeEnum.FACTURA:
            supplier['nit'] = self.normalize_nit(
                self._extract_with_fallback('vendedor_nit', ['vendedor_nit_alt']) or ''
            )
            supplier['razon_social'] = self.normalize_text(
                self._extract_with_fallback('vendedor_razon_social', ['vendedor_razon_alt']) or ''
            )
        else:
            supplier['nit'] = self.normalize_nit(
                self._extract_with_fallback('vendedor_pos_nit', ['vendedor_nit', 'vendedor_nit_alt']) or ''
            )
            supplier['razon_social'] = self.normalize_text(
                self._extract_with_fallback('vendedor_pos_razon', ['vendedor_razon_social', 'vendedor_razon_alt']) or ''
            )
        
        # Otros datos del proveedor
        supplier['direccion'] = self.normalize_text(self._extract_match('vendedor_direccion') or '')
        supplier['telefono'] = self.normalize_text(self._extract_match('vendedor_telefono') or '')
        supplier['correo'] = self.normalize_text(self._extract_match('vendedor_correo') or '')
        supplier['departamento'] = self.normalize_text(self._extract_match('vendedor_departamento') or '')
        supplier['ciudad'] = self.normalize_text(self._extract_match('vendedor_ciudad') or '')
        
        return supplier


    def _extract_items_from_tables(self, pdf: pdfplumber.PDF, doc_type: DocumentTypeEnum) -> List[InvoiceItemReview]:
        """Extrae items de las tablas de TODAS las páginas del PDF"""
        items = []
        item_number = 0
        found_products_table = False  # Flag para saber si ya encontramos la tabla de productos
        expected_columns = 0  # Número de columnas de la tabla de productos
        
        for page_num, page in enumerate(pdf.pages):
            try:
                tables = page.extract_tables()
                logger.debug(f"Página {page_num + 1}: {len(tables)} tablas encontradas")
                
                for table_num, table in enumerate(tables):
                    if not table or len(table) < 1:
                        continue
                    
                    # Buscar fila de encabezado
                    header_row = None
                    header_keywords = ['código', 'codigo', 'descripcion', 'descripción', 'cantidad', 'cant', 'producto', 'item', 'artículo', 'nro']
                    
                    for i, row in enumerate(table):
                        if not row:
                            continue
                        row_text = ' '.join([str(c or '').lower() for c in row])
                        if any(kw in row_text for kw in header_keywords):
                            header_row = i
                            expected_columns = len(row)
                            found_products_table = True
                            logger.debug(f"Encabezado encontrado en fila {i}: {row_text[:50]}...")
                            break
                    
                    # Si no hay encabezado pero ya encontramos la tabla de productos antes,
                    # verificar si esta tabla es continuación (misma estructura)
                    if header_row is None and found_products_table:
                        # Verificar si la primera fila parece un item de producto
                        if len(table) > 0 and len(table[0]) >= 4:
                            first_row = table[0]
                            first_cell = str(first_row[0] or '').strip()
                            # Si la primera celda es un número (número de item), es continuación
                            if first_cell.isdigit() and int(first_cell) > 0:
                                header_row = -1  # Indica que no hay encabezado, empezar desde fila 0
                                logger.debug(f"Tabla de continuación detectada en página {page_num + 1}")
                    
                    if header_row is None:
                        # Intentar detectar tabla de productos por contenido
                        if len(table) > 1 and len(table[0]) >= 4:
                            # Verificar si parece tabla de productos
                            first_row = table[0]
                            first_cell = str(first_row[0] or '').strip()
                            if first_cell.isdigit():
                                header_row = -1  # Sin encabezado
                                found_products_table = True
                            else:
                                header_row = 0  # Asumir primera fila es encabezado
                                found_products_table = True
                    
                    if header_row is None:
                        continue
                    
                    # Determinar desde qué fila empezar a procesar
                    start_row = header_row + 1 if header_row >= 0 else 0
                    
                    # Procesar filas de datos
                    for row in table[start_row:]:
                        if not row or len(row) < 3:
                            continue
                        
                        # Saltar filas de totales
                        first_cell = str(row[0] or '').lower().strip()
                        skip_keywords = ['subtotal', 'total', 'iva', 'descuento', 'neto', 'bruto', 'base', 'impuesto']
                        if any(kw in first_cell for kw in skip_keywords):
                            continue
                        
                        # Saltar filas vacías o con solo espacios
                        non_empty = [c for c in row if c and str(c).strip()]
                        if len(non_empty) < 3:
                            continue
                        
                        item = self._parse_item_row(row, doc_type, item_number + 1)
                        if item:
                            items.append(item)
                            item_number += 1
                            
            except Exception as e:
                logger.warning(f"Error procesando tablas de página {page_num + 1}: {e}")
                continue
        
        logger.info(f"Total items extraídos: {len(items)}")
        return items

    def _parse_item_row(self, row: List, doc_type: DocumentTypeEnum, item_number: int) -> Optional[InvoiceItemReview]:
        """Parsea una fila de la tabla de productos"""
        try:
            cells = [self.normalize_text(str(c or '')) for c in row]
            
            # Necesitamos al menos descripción y algún valor numérico
            if len(cells) < 3:
                return None
            
            codigo, descripcion, unidad = '', '', ''
            cantidad, precio, iva_pct, iva_valor, valor_total, descuento = 1, 0, 0.0, 0, 0, 0
            
            # Detectar estructura de la fila
            # Caso 1: Primera celda es número de ítem (1, 2, 3...)
            if cells[0].isdigit() and int(cells[0]) < 1000:
                idx_offset = 1
                codigo = self.normalize_code(cells[1]) if len(cells) > 1 else ''
                descripcion = cells[2] if len(cells) > 2 else ''
                unidad = cells[3] if len(cells) > 3 else ''
                cantidad = self.normalize_quantity(cells[4]) if len(cells) > 4 else 1
                precio = self.normalize_money(cells[5]) if len(cells) > 5 else 0
            # Caso 2: Primera celda es código o descripción
            else:
                # Verificar si primera celda parece código (alfanumérico corto)
                if len(cells[0]) <= 20 and re.match(r'^[\w\-\.]+$', cells[0]):
                    codigo = self.normalize_code(cells[0])
                    descripcion = cells[1] if len(cells) > 1 else ''
                    unidad = cells[2] if len(cells) > 2 else ''
                    cantidad = self.normalize_quantity(cells[3]) if len(cells) > 3 else 1
                    precio = self.normalize_money(cells[4]) if len(cells) > 4 else 0
                else:
                    # Primera celda es descripción
                    descripcion = cells[0]
                    unidad = cells[1] if len(cells) > 1 else ''
                    cantidad = self.normalize_quantity(cells[2]) if len(cells) > 2 else 1
                    precio = self.normalize_money(cells[3]) if len(cells) > 3 else 0
            
            # Buscar IVA y valor total en las últimas celdas
            for i, cell in enumerate(reversed(cells)):
                cell_clean = cell.replace('%', '').replace('$', '').strip()
                if not cell_clean:
                    continue
                    
                # Última celda numérica suele ser el total
                if i == 0:
                    val = self.normalize_money(cell)
                    if val > 0:
                        valor_total = val
                # Buscar porcentaje de IVA
                elif self.normalize_percentage(cell_clean) in [0, 5, 19]:
                    iva_pct = self.normalize_percentage(cell_clean)
            
            # Validar que tengamos una descripción válida
            if not descripcion or len(descripcion.strip()) < 2:
                return None
            
            # Calcular valores faltantes
            if valor_total == 0 and precio > 0 and cantidad > 0:
                valor_total = cantidad * precio
            
            if precio == 0 and valor_total > 0 and cantidad > 0:
                precio = valor_total // cantidad
            
            if iva_pct > 0 and valor_total > 0:
                iva_valor = int(valor_total * iva_pct / (100 + iva_pct))
            
            item = InvoiceItemReview(
                numero_item=item_number,
                codigo=codigo,
                descripcion=descripcion[:500],  # Limitar longitud
                unidad_medida=unidad.split('|')[0].strip()[:50] if unidad else '',
                cantidad=cantidad,
                precio_unitario=precio,
                descuento=descuento,
                recargo=0,
                iva_porcentaje=iva_pct,
                iva_valor=iva_valor,
                inc_porcentaje=0,
                inc_valor=0,
                valor_total=valor_total,
                has_warning=False,
                warning_message=None,
                suggested_fix=None
            )
            
            # Agregar warnings si hay datos faltantes
            if not codigo:
                item.has_warning = True
                item.warning_message = "Producto sin código"
            if precio == 0 and valor_total == 0:
                item.has_warning = True
                item.warning_message = "Sin precio ni valor total"
            
            return item
            
        except Exception as e:
            logger.warning(f"Error parseando fila de item {item_number}: {e}")
            return None


    def _extract_totals(self, pdf: pdfplumber.PDF) -> Dict[str, int]:
        """Extrae totales del documento de TODAS las páginas"""
        totals = {'subtotal': 0, 'descuento': 0, 'total_bruto': 0, 'total_iva': 0, 'total_neto': 0}
        
        # Buscar en tablas de todas las páginas
        for page in pdf.pages:
            try:
                for table in page.extract_tables():
                    if not table:
                        continue
                    for row in table:
                        if not row:
                            continue
                        row_text = ' '.join([str(c or '').lower() for c in row])
                        
                        # Subtotal
                        if 'subtotal' in row_text and 'iva' not in row_text:
                            for cell in row:
                                val = self.normalize_money(str(cell or ''))
                                if val > 0:
                                    totals['subtotal'] = max(totals['subtotal'], val)
                        
                        # IVA
                        if 'iva' in row_text and 'subtotal' not in row_text:
                            for cell in row:
                                val = self.normalize_money(str(cell or ''))
                                if val > 0 and val < totals.get('subtotal', float('inf')) * 0.5:
                                    totals['total_iva'] = max(totals['total_iva'], val)
                        
                        # Total neto/a pagar
                        if any(x in row_text for x in ['total neto', 'total a pagar', 'gran total', 'total factura']):
                            for cell in row:
                                val = self.normalize_money(str(cell or ''))
                                if val > 0:
                                    totals['total_neto'] = max(totals['total_neto'], val)
                        
                        # Descuento
                        if 'descuento' in row_text or 'dcto' in row_text:
                            for cell in row:
                                val = self.normalize_money(str(cell or ''))
                                if val > 0 and val < totals.get('subtotal', float('inf')):
                                    totals['descuento'] = max(totals['descuento'], val)
            except Exception as e:
                logger.warning(f"Error extrayendo totales de tabla: {e}")
        
        # Buscar en texto si no se encontraron en tablas
        if totals['subtotal'] == 0:
            match = self.PATTERNS['subtotal'].search(self.full_text)
            if match:
                totals['subtotal'] = self.normalize_money(match.group(1))
        
        if totals['total_iva'] == 0:
            match = self.PATTERNS['total_iva'].search(self.full_text)
            if match:
                totals['total_iva'] = self.normalize_money(match.group(1))
        
        if totals['total_neto'] == 0:
            match = self.PATTERNS['total_neto'].search(self.full_text)
            if match:
                totals['total_neto'] = self.normalize_money(match.group(1))
        
        # Calcular total bruto
        if totals['total_bruto'] == 0:
            totals['total_bruto'] = totals['subtotal'] - totals['descuento']
        
        # Si no hay total neto pero hay subtotal e IVA, calcular
        if totals['total_neto'] == 0 and totals['subtotal'] > 0:
            totals['total_neto'] = totals['subtotal'] + totals['total_iva'] - totals['descuento']
        
        logger.debug(f"Totales extraídos: {totals}")
        return totals

    # ========================================
    # Método Principal de Extracción
    # ========================================
    
    def extract_from_pdf(self, pdf_path: str, filename: str = None) -> Tuple[ExtractedInvoiceData, List[ExtractionWarning]]:
        """
        Extrae todos los datos de un PDF de factura.
        Lee TODAS las páginas del documento.
        Returns: Tuple con (datos extraídos, lista de advertencias)
        """
        self.warnings = []
        self.full_text = ""
        
        logger.info(f"Iniciando extracción de PDF: {filename or pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                logger.info(f"PDF tiene {num_pages} página(s)")
                
                # Extraer texto de TODAS las páginas
                self.full_text = self._extract_all_text(pdf)
                logger.debug(f"Texto total extraído: {len(self.full_text)} caracteres")
                
                # Detectar tipo de documento
                doc_type = self._detect_document_type(self.full_text)
                logger.info(f"Tipo de documento detectado: {doc_type.value}")
                
                # Extraer CUFE/CUDE
                cufe_cude = self._extract_cufe_cude(doc_type)
                if not cufe_cude:
                    self._add_warning('cufe_cude', 'No se encontró código CUFE/CUDE', severity='error')
                    logger.warning("No se encontró CUFE/CUDE")
                else:
                    logger.info(f"CUFE/CUDE encontrado: {cufe_cude[:20]}...")
                
                # Extraer número de documento y fechas
                if doc_type == DocumentTypeEnum.FACTURA:
                    numero_doc = self._extract_with_fallback('numero_factura', ['numero_documento_pos']) or ''
                    fecha_str = self._extract_with_fallback('fecha_emision', ['fecha_expedicion']) or ''
                else:
                    numero_doc = self._extract_with_fallback('numero_documento_pos', ['numero_factura']) or ''
                    fecha_str = self._extract_with_fallback('fecha_expedicion', ['fecha_emision']) or ''
                
                if not numero_doc:
                    self._add_warning('numero_documento', 'No se encontró número de documento', severity='warning')
                
                fecha_venc_str = self._extract_match('fecha_vencimiento')
                forma_pago = self._extract_match('forma_pago')
                medio_pago = self._extract_match('medio_pago')
                
                # Extraer datos del proveedor
                supplier = self._extract_supplier(doc_type)
                
                if not supplier['nit']:
                    self._add_warning('supplier_nit', 'No se encontró NIT del proveedor', severity='error')
                    logger.warning("No se encontró NIT del proveedor")
                if not supplier['razon_social']:
                    self._add_warning('supplier_razon_social', 'No se encontró razón social del proveedor', severity='warning')
                
                # Extraer items de TODAS las páginas
                items = self._extract_items_from_tables(pdf, doc_type)
                if not items:
                    self._add_warning('items', 'No se encontraron productos en el documento', severity='warning')
                    logger.warning("No se encontraron items/productos")
                else:
                    logger.info(f"Items extraídos: {len(items)}")
                
                # Extraer totales
                totals = self._extract_totals(pdf)
                
                # Validar consistencia de totales
                items_total = sum(item.valor_total for item in items)
                if totals['total_neto'] > 0 and items_total > 0:
                    diff = abs(items_total - totals['total_neto'])
                    if diff > 100:  # Tolerancia de $100
                        self._add_warning(
                            'totals',
                            f"La suma de items (${items_total:,}) difiere del total (${totals['total_neto']:,})",
                            original_value=str(items_total),
                            suggested_value=str(totals['total_neto']),
                            severity='warning'
                        )
                
                # Determinar si es válido
                has_critical_errors = any(w.severity == 'error' for w in self.warnings)
                
                extracted = ExtractedInvoiceData(
                    cufe_cude=cufe_cude,
                    document_type=doc_type,
                    numero_documento=numero_doc,
                    fecha_emision=fecha_str,
                    fecha_vencimiento=fecha_venc_str,
                    forma_pago=forma_pago,
                    medio_pago=medio_pago,
                    supplier_nit=supplier['nit'],
                    supplier_razon_social=supplier['razon_social'],
                    supplier_direccion=supplier['direccion'],
                    supplier_telefono=supplier['telefono'],
                    supplier_correo=supplier['correo'],
                    supplier_ciudad=supplier['ciudad'],
                    supplier_departamento=supplier['departamento'],
                    subtotal=totals['subtotal'],
                    descuento=totals['descuento'],
                    total_bruto=totals['total_bruto'],
                    total_iva=totals['total_iva'],
                    total_neto=totals['total_neto'],
                    items=items,
                    is_valid=not has_critical_errors,
                    is_duplicate=False,
                    warnings=self.warnings,
                    archivo_nombre=filename
                )
                
                logger.info(f"Extracción completada. Válido: {extracted.is_valid}, Warnings: {len(self.warnings)}")
                return extracted, self.warnings
                
        except Exception as e:
            logger.error(f"Error extrayendo datos del PDF: {e}", exc_info=True)
            self._add_warning('general', f'Error procesando el archivo: {str(e)}', severity='error')
            
            return ExtractedInvoiceData(
                cufe_cude='',
                document_type=DocumentTypeEnum.FACTURA,
                numero_documento='',
                fecha_emision='',
                supplier_nit='',
                supplier_razon_social='',
                items=[],
                is_valid=False,
                warnings=self.warnings,
                archivo_nombre=filename
            ), self.warnings
