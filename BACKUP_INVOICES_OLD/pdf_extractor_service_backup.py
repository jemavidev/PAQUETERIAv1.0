# ========================================
# PAQUETES EL CLUB - Servicio de Extracción de PDFs
# ========================================
"""
Servicio para extraer datos de facturas electrónicas y documentos POS.
Soporta múltiples formatos de PDF con detección automática de estructura.

Variantes soportadas:
- Variante 1: 10 columnas (sin descuento por item)
- Variante 2: 13 columnas (con descuento, recargo, IVA, INC)
- Variante 3: 13 columnas (productos sin IVA)

Características:
- Detección automática de estructura de columnas
- Normalización de datos formato Colombia
- Soporte para PDFs de múltiples páginas
- Validación de integridad de datos
"""

import re
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from dataclasses import dataclass

import pdfplumber

from app.schemas.invoice import (
    DocumentTypeEnum,
    ExtractedInvoiceData,
    InvoiceItemReview,
    ExtractionWarning,
)

logger = logging.getLogger(__name__)


class TableStructure(Enum):
    """Tipos de estructura de tabla detectados"""
    VARIANT_10_COLS = "10_cols"  # Sin descuento por item
    VARIANT_13_COLS = "13_cols"  # Con descuento, recargo, IVA, INC
    UNKNOWN = "unknown"


@dataclass
class ColumnMapping:
    """Mapeo de columnas según la estructura detectada"""
    nro: int = -1
    codigo: int = -1
    descripcion: int = -1
    unidad: int = -1
    cantidad: int = -1
    precio_unitario: int = -1
    descuento: int = -1
    recargo: int = -1
    iva_valor: int = -1
    iva_porcentaje: int = -1
    inc_valor: int = -1
    inc_porcentaje: int = -1
    valor_total: int = -1


# Mapeos predefinidos para cada variante
COLUMN_MAPPINGS = {
    TableStructure.VARIANT_10_COLS: ColumnMapping(
        nro=0,
        codigo=1,
        descripcion=2,
        unidad=3,
        cantidad=4,
        precio_unitario=5,
        descuento=-1,  # No existe
        recargo=-1,    # No existe
        iva_valor=6,
        iva_porcentaje=7,
        inc_valor=-1,  # No existe
        inc_porcentaje=-1,  # No existe
        valor_total=8,
    ),
    TableStructure.VARIANT_13_COLS: ColumnMapping(
        nro=0,
        codigo=1,
        descripcion=2,
        unidad=3,
        cantidad=4,
        precio_unitario=5,
        descuento=6,
        recargo=7,
        iva_valor=8,
        iva_porcentaje=9,
        inc_valor=10,
        inc_porcentaje=11,
        valor_total=12,
    ),
}


class PDFExtractorService:
    """Servicio para extraer y normalizar datos de PDFs de facturas"""
    
    # Patrones de regex compilados
    PATTERNS = {
        # CUFE/CUDE (64-96 caracteres hex)
        'cufe': re.compile(r'CUFE\s*:?\s*\n?\s*([a-f0-9]{64,96})', re.IGNORECASE),
        'cude': re.compile(r'CUDE\s*:?\s*\n?\s*([a-f0-9]{64,96})', re.IGNORECASE),
        'cufe_alt': re.compile(r'(?:Código\s+único|CUFE|Clave)\s*:?\s*\n?\s*([a-f0-9]{64,96})', re.IGNORECASE),
        
        # Número de factura
        'numero_factura': re.compile(r'(?:Número\s+de\s+Factura|No\.\s*Factura|Factura\s+No\.?|N[úu]mero)\s*:?\s*([A-Z0-9\-]+)', re.IGNORECASE),
        'numero_documento_pos': re.compile(r'(?:Número\s+de\s+documento|Doc(?:umento)?\.?\s*No\.?)\s*:?\s*([A-Z0-9\-]+)', re.IGNORECASE),
        
        # Fechas
        'fecha_emision': re.compile(r'(?:Fecha\s+de\s+Emisi[oó]n|Fecha\s+Emisi[oó]n|Fecha)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', re.IGNORECASE),
        'fecha_expedicion': re.compile(r'(?:Fecha\s+y\s+hora\s+de\s+expedici[oó]n|Fecha\s+expedici[oó]n)\s*:?\s*([^\n]+)', re.IGNORECASE),
        'fecha_vencimiento': re.compile(r'(?:Fecha\s+de\s+Vencimiento|Vencimiento)\s*:?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', re.IGNORECASE),
        
        # Forma y medio de pago
        'forma_pago': re.compile(r'(?:Forma\s+de\s+pago|Condici[oó]n\s+de\s+pago)\s*:?\s*([^\n]+)', re.IGNORECASE),
        'medio_pago': re.compile(r'(?:Medio\s+de\s+Pago|M[ée]todo\s+de\s+pago)\s*:?\s*([^\n]+)', re.IGNORECASE),
        
        # Datos del emisor/vendedor
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
        
        # Totales
        'subtotal': re.compile(r'(?:Sub\s*total|Subtotal)\s*:?\s*\$?\s*([\d\.,]+)', re.IGNORECASE),
        'total_iva': re.compile(r'(?:Total\s+)?IVA\s*(?:\d+%?)?\s*:?\s*\$?\s*([\d\.,]+)', re.IGNORECASE),
        'total_neto': re.compile(r'(?:Total\s+(?:neto|a\s+pagar|factura)|Gran\s+Total|TOTAL)\s*:?\s*\$?\s*([\d\.,]+)', re.IGNORECASE),
        'descuento': re.compile(r'(?:Descuento|Dcto\.?)\s*:?\s*\$?\s*([\d\.,]+)', re.IGNORECASE),
    }
    
    def __init__(self):
        self.warnings: List[ExtractionWarning] = []
        self.full_text: str = ""
        self.detected_structure: TableStructure = TableStructure.UNKNOWN
        self.column_mapping: Optional[ColumnMapping] = None


    # ========================================
    # Métodos de Normalización de Datos
    # ========================================
    
    @staticmethod
    def normalize_money(value: str) -> int:
        """
        Convierte un valor monetario a entero (pesos colombianos sin decimales).
        Maneja formatos: $1.234,56 | $ 1.234,56 | 1234.56 | 1,234.56 | 1234
        También maneja texto como "IVA 222.632,00" extrayendo solo el número.
        Si hay múltiples números (ej: "IVA 222.632,00\nINC 0,00"), toma el primero.
        """
        if not value:
            return 0
        
        # Convertir a string
        value_str = str(value)
        
        # Si hay saltos de línea, tomar solo la primera línea
        if '\n' in value_str:
            value_str = value_str.split('\n')[0]
        
        # Extraer solo números, puntos, comas y signo negativo
        cleaned = re.sub(r'[^\d.,\-]', '', value_str)
        
        if not cleaned or cleaned in ['.', ',', '-']:
            return 0
        
        try:
            # Detectar formato colombiano (1.234,56) vs americano (1,234.56)
            if ',' in cleaned and '.' in cleaned:
                # Si la coma está después del punto, es formato colombiano
                if cleaned.rfind(',') > cleaned.rfind('.'):
                    # Formato colombiano: 1.234.567,89 -> 1234567.89
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    # Formato americano: 1,234,567.89 -> 1234567.89
                    cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                parts = cleaned.split(',')
                # Si hay 2 o menos dígitos después de la coma, es separador decimal
                if len(parts[-1]) <= 2:
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Es separador de miles
                    cleaned = cleaned.replace(',', '')
            elif '.' in cleaned:
                parts = cleaned.split('.')
                # Si hay exactamente 3 dígitos después del punto, es separador de miles
                if len(parts[-1]) == 3 and len(parts) > 1:
                    cleaned = cleaned.replace('.', '')
                # Si hay más de 3 dígitos o múltiples puntos, asumir separador de miles
                elif len(parts) > 2:
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
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    @staticmethod
    def normalize_code(value: str) -> str:
        """Normaliza código de producto"""
        if not value:
            return ""
        cleaned = str(value).strip()
        cleaned = re.sub(r'[^\w\-\./]', '', cleaned)
        return cleaned[:50]
    
    @staticmethod
    def normalize_text(value: str) -> str:
        """Normaliza texto: trim, espacios múltiples, saltos de línea"""
        if not value:
            return ""
        cleaned = str(value).strip()
        cleaned = re.sub(r'[\n\r]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned[:500]
    
    @staticmethod
    def normalize_nit(value: str) -> str:
        """Normaliza NIT: solo dígitos"""
        if not value:
            return ""
        return re.sub(r'[^\d]', '', str(value))[:15]


    @staticmethod
    def parse_date(value: str) -> Optional[datetime]:
        """Parsea fecha en varios formatos"""
        if not value:
            return None
        
        cleaned = re.sub(r'[+-]\d{2}:\d{2}$', '', str(value).strip())
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%y',
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S',
            '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M',
        ]
        
        for fmt in formats:
            try:
                date_part = cleaned.split()[0] if ' ' in cleaned and fmt.count(' ') == 0 else cleaned
                return datetime.strptime(date_part, fmt)
            except ValueError:
                continue
        
        # Intentar extraer solo la fecha
        date_match = re.search(r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', cleaned)
        if date_match:
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']:
                try:
                    return datetime.strptime(date_match.group(1), fmt)
                except ValueError:
                    continue
        
        return None

    # ========================================
    # Métodos de Extracción de Texto
    # ========================================
    
    def _extract_all_text(self, pdf: pdfplumber.PDF) -> str:
        """Extrae texto de TODAS las páginas del PDF"""
        all_text = []
        for i, page in enumerate(pdf.pages):
            try:
                text = page.extract_text() or ''
                all_text.append(f"--- PÁGINA {i+1} ---\n{text}")
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
    
    def _extract_with_fallback(self, primary: str, fallbacks: List[str], text: str = None) -> Optional[str]:
        """Intenta extraer con patrón primario, luego con fallbacks"""
        result = self._extract_match(primary, text)
        if result:
            return result
        for pattern in fallbacks:
            result = self._extract_match(pattern, text)
            if result:
                return result
        return None
    
    def _add_warning(self, field: str, message: str, original_value: str = None,
                     suggested_value: str = None, severity: str = "warning"):
        """Agrega una advertencia a la lista"""
        self.warnings.append(ExtractionWarning(
            field=field, message=message, original_value=original_value,
            suggested_value=suggested_value, severity=severity
        ))


    # ========================================
    # Detección de Tipo de Documento
    # ========================================
    
    def _detect_document_type(self, text: str) -> DocumentTypeEnum:
        """Detecta el tipo de documento"""
        text_upper = text.upper()
        
        factura_indicators = [
            'FACTURA ELECTRÓNICA', 'FACTURA ELECTRONICA',
            'FACTURA ELECTRÓNICA DE VENTA', 'FACTURA DE VENTA',
            'CUFE:', 'CUFE :',
        ]
        pos_indicators = [
            'DOCUMENTO EQUIVALENTE POS', 'DOCUMENTO POS',
            'CUDE:', 'CUDE :', 'TIQUETE POS',
        ]
        
        for indicator in factura_indicators:
            if indicator in text_upper:
                return DocumentTypeEnum.FACTURA
        
        for indicator in pos_indicators:
            if indicator in text_upper:
                return DocumentTypeEnum.POS
        
        self._add_warning("document_type", "No se pudo detectar el tipo de documento, asumiendo Factura", severity="warning")
        return DocumentTypeEnum.FACTURA
    
    def _extract_cufe_cude(self, doc_type: DocumentTypeEnum) -> str:
        """Extrae CUFE o CUDE"""
        if doc_type == DocumentTypeEnum.FACTURA:
            cufe = self._extract_with_fallback('cufe', ['cufe_alt'])
            if cufe:
                return cufe
        else:
            cude = self._extract_match('cude')
            if cude:
                return cude
        
        # Búsqueda agresiva de cadena hex larga
        hex_pattern = re.compile(r'\b([a-f0-9]{64,96})\b', re.IGNORECASE)
        matches = hex_pattern.findall(self.full_text)
        if matches:
            return max(matches, key=len)
        return ""
    
    def _extract_supplier(self, doc_type: DocumentTypeEnum) -> Dict[str, str]:
        """Extrae datos del proveedor"""
        supplier = {
            'nit': '', 'razon_social': '', 'direccion': '',
            'telefono': '', 'correo': '', 'departamento': '', 'ciudad': '',
        }
        
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
        
        supplier['direccion'] = self.normalize_text(self._extract_match('vendedor_direccion') or '')
        supplier['telefono'] = self.normalize_text(self._extract_match('vendedor_telefono') or '')
        supplier['correo'] = self.normalize_text(self._extract_match('vendedor_correo') or '')
        supplier['departamento'] = self.normalize_text(self._extract_match('vendedor_departamento') or '')
        supplier['ciudad'] = self.normalize_text(self._extract_match('vendedor_ciudad') or '')
        
        return supplier


    # ========================================
    # Detección de Estructura de Tabla
    # ========================================
    
    def _detect_table_structure(self, headers: List[str]) -> Tuple[TableStructure, ColumnMapping]:
        """
        Detecta la estructura de la tabla basándose en los encabezados.
        Retorna el tipo de estructura y el mapeo de columnas.
        """
        num_cols = len(headers)
        headers_lower = [h.lower().replace('\n', ' ').strip() for h in headers]
        
        logger.debug(f"Detectando estructura para {num_cols} columnas: {headers_lower}")
        
        # Crear mapeo dinámico basado en encabezados
        mapping = ColumnMapping()
        
        for idx, header in enumerate(headers_lower):
            if 'nro' in header or header == '#':
                mapping.nro = idx
            elif 'código' in header or 'codigo' in header:
                mapping.codigo = idx
            elif 'descripción' in header or 'descripcion' in header:
                mapping.descripcion = idx
            elif 'u/m' in header or 'unidad' in header:
                mapping.unidad = idx
            elif 'cantidad' in header:
                mapping.cantidad = idx
            elif 'precio unitario' in header and 'venta' not in header:
                mapping.precio_unitario = idx
            elif 'descuento' in header:
                mapping.descuento = idx
            elif 'recargo' in header:
                mapping.recargo = idx
            elif 'iva' in header and '%' not in header:
                mapping.iva_valor = idx
            elif 'inc' in header and '%' not in header:
                mapping.inc_valor = idx
            elif header == '%' or 'porcentaje' in header:
                # El % puede ser de IVA o INC, depende de la posición
                if mapping.iva_valor >= 0 and idx == mapping.iva_valor + 1:
                    mapping.iva_porcentaje = idx
                elif mapping.inc_valor >= 0 and idx == mapping.inc_valor + 1:
                    mapping.inc_porcentaje = idx
            elif 'valor' in header and 'venta' in header:
                mapping.valor_total = idx
            elif 'precio' in header and 'venta' in header:
                mapping.valor_total = idx
        
        # Si no encontramos valor_total, buscar la última columna numérica
        if mapping.valor_total < 0:
            # Última columna no vacía suele ser el total
            for idx in range(num_cols - 1, -1, -1):
                if headers_lower[idx].strip() == '' or 'total' in headers_lower[idx] or 'valor' in headers_lower[idx]:
                    mapping.valor_total = idx
                    break
        
        # Determinar tipo de estructura
        if num_cols >= 12 and mapping.descuento >= 0:
            structure = TableStructure.VARIANT_13_COLS
        elif num_cols >= 8 and num_cols <= 11:
            structure = TableStructure.VARIANT_10_COLS
        else:
            structure = TableStructure.UNKNOWN
        
        logger.info(f"Estructura detectada: {structure.value} con {num_cols} columnas")
        logger.debug(f"Mapeo: nro={mapping.nro}, codigo={mapping.codigo}, desc={mapping.descripcion}, "
                    f"cant={mapping.cantidad}, precio={mapping.precio_unitario}, desc={mapping.descuento}, "
                    f"iva_val={mapping.iva_valor}, iva_pct={mapping.iva_porcentaje}, total={mapping.valor_total}")
        
        return structure, mapping


    # ========================================
    # Extracción de Items de Tablas
    # ========================================
    
    def _extract_items_from_tables(self, pdf: pdfplumber.PDF, doc_type: DocumentTypeEnum) -> List[InvoiceItemReview]:
        """Extrae items de las tablas de TODAS las páginas del PDF"""
        items = []
        item_number = 0
        structure_detected = False
        
        for page_num, page in enumerate(pdf.pages):
            try:
                tables = page.extract_tables()
                logger.debug(f"Página {page_num + 1}: {len(tables)} tablas encontradas")
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Buscar fila de encabezado
                    header_row_idx = None
                    header_keywords = ['código', 'codigo', 'descripcion', 'descripción', 'cantidad', 'nro']
                    
                    for i, row in enumerate(table):
                        if not row:
                            continue
                        row_text = ' '.join([str(c or '').lower() for c in row])
                        if any(kw in row_text for kw in header_keywords):
                            header_row_idx = i
                            
                            # Detectar estructura si no lo hemos hecho
                            if not structure_detected:
                                headers = [str(c or '') for c in row]
                                self.detected_structure, self.column_mapping = self._detect_table_structure(headers)
                                structure_detected = True
                            break
                    
                    # Si no hay encabezado pero ya detectamos estructura, puede ser continuación
                    if header_row_idx is None and structure_detected:
                        if len(table) > 0 and len(table[0]) >= 4:
                            first_cell = str(table[0][0] or '').strip()
                            if first_cell.isdigit() and int(first_cell) > 0:
                                header_row_idx = -1  # Sin encabezado, empezar desde fila 0
                    
                    if header_row_idx is None:
                        continue
                    
                    # Procesar filas de datos
                    start_row = header_row_idx + 1 if header_row_idx >= 0 else 0
                    
                    for row in table[start_row:]:
                        if not row or len(row) < 3:
                            continue
                        
                        # Saltar filas de totales
                        first_cell = str(row[0] or '').lower().strip()
                        skip_keywords = ['subtotal', 'total', 'iva', 'descuento', 'neto', 'bruto', 'base', 'impuesto']
                        if any(kw in first_cell for kw in skip_keywords):
                            continue
                        
                        # Saltar filas vacías
                        non_empty = [c for c in row if c and str(c).strip()]
                        if len(non_empty) < 3:
                            continue
                        
                        item = self._parse_item_row(row, item_number + 1)
                        if item:
                            items.append(item)
                            item_number += 1
                            
            except Exception as e:
                logger.warning(f"Error procesando tablas de página {page_num + 1}: {e}")
                continue
        
        logger.info(f"Total items extraídos: {len(items)}")
        return items


    def _safe_get_cell(self, row: List, index: int) -> str:
        """Obtiene una celda de forma segura"""
        if index < 0 or index >= len(row):
            return ""
        return self.normalize_text(str(row[index] or ''))
    
    def _parse_item_row(self, row: List, item_number: int) -> Optional[InvoiceItemReview]:
        """
        Parsea una fila de la tabla de productos usando el mapeo de columnas detectado.
        """
        try:
            mapping = self.column_mapping
            if not mapping:
                logger.warning("No hay mapeo de columnas definido")
                return None
            
            # Extraer valores usando el mapeo
            codigo = self.normalize_code(self._safe_get_cell(row, mapping.codigo))
            descripcion = self._safe_get_cell(row, mapping.descripcion)
            unidad = self._safe_get_cell(row, mapping.unidad)
            
            # Limpiar unidad (quitar texto adicional como "| número de unidades...")
            if '|' in unidad:
                unidad = unidad.split('|')[0].strip()
            
            cantidad = self.normalize_quantity(self._safe_get_cell(row, mapping.cantidad))
            precio_unitario = self.normalize_money(self._safe_get_cell(row, mapping.precio_unitario))
            
            # Descuento (puede no existir en algunas variantes)
            descuento = 0
            if mapping.descuento >= 0:
                descuento = self.normalize_money(self._safe_get_cell(row, mapping.descuento))
            
            # Recargo (puede no existir)
            recargo = 0
            if mapping.recargo >= 0:
                recargo = self.normalize_money(self._safe_get_cell(row, mapping.recargo))
            
            # IVA valor y porcentaje
            iva_valor = 0
            iva_porcentaje = 0.0
            if mapping.iva_valor >= 0:
                iva_valor = self.normalize_money(self._safe_get_cell(row, mapping.iva_valor))
            if mapping.iva_porcentaje >= 0:
                iva_porcentaje = self.normalize_percentage(self._safe_get_cell(row, mapping.iva_porcentaje))
            
            # INC valor y porcentaje
            inc_valor = 0
            inc_porcentaje = 0.0
            if mapping.inc_valor >= 0:
                inc_valor = self.normalize_money(self._safe_get_cell(row, mapping.inc_valor))
            if mapping.inc_porcentaje >= 0:
                inc_porcentaje = self.normalize_percentage(self._safe_get_cell(row, mapping.inc_porcentaje))
            
            # Valor total (última columna generalmente)
            valor_total = 0
            if mapping.valor_total >= 0:
                valor_total = self.normalize_money(self._safe_get_cell(row, mapping.valor_total))
            
            # Si no hay valor total, intentar la última celda no vacía
            if valor_total == 0:
                for i in range(len(row) - 1, -1, -1):
                    val = self.normalize_money(str(row[i] or ''))
                    if val > 0:
                        valor_total = val
                        break
            
            # Validar descripción
            if not descripcion or len(descripcion.strip()) < 2:
                return None
            
            # Determinar si el IVA está incluido en el precio
            # Esto es crítico para calcular correctamente el valor_total
            iva_incluido = None  # Por defecto desconocido
            
            # Si tenemos valor_total del PDF, usarlo para detectar
            if iva_porcentaje > 0 and precio_unitario > 0 and valor_total > 0:
                # Calcular lo que sería el total sin IVA
                base_calculada = (precio_unitario * cantidad) - descuento + recargo
                total_con_iva = base_calculada + iva_valor
                
                # Si el valor_total coincide con total_con_iva, el IVA NO está incluido en el precio
                if abs(valor_total - total_con_iva) < 10:  # Tolerancia de $10
                    iva_incluido = False
                # Si el valor_total coincide con base_calculada, el IVA SÍ está incluido
                elif abs(valor_total - base_calculada) < 10:
                    iva_incluido = True
            
            # Calcular valores faltantes
            if valor_total == 0 and precio_unitario > 0 and cantidad > 0:
                # Calcular subtotal base (precio * cantidad - descuento + recargo)
                subtotal_item = (precio_unitario * cantidad) - descuento + recargo
                
                # REGLA IMPORTANTE: En facturas colombianas, cuando el IVA se lista por separado
                # en la tabla de items, generalmente significa que NO está incluido en el precio
                # Por lo tanto, valor_total debe ser el subtotal SIN IVA
                if iva_valor > 0:
                    # IVA listado por separado = NO incluido en precio
                    iva_incluido = False
                    valor_total = subtotal_item + inc_valor
                else:
                    # Sin IVA o IVA incluido en precio
                    valor_total = subtotal_item + inc_valor
            
            if precio_unitario == 0 and valor_total > 0 and cantidad > 0:
                # Calcular precio unitario aproximado
                # Asumimos que valor_total NO incluye IVA si hay iva_valor listado
                if iva_valor > 0:
                    precio_unitario = (valor_total - inc_valor + descuento - recargo) // cantidad
                else:
                    precio_unitario = (valor_total - inc_valor + descuento - recargo) // cantidad

            
            # Calcular precio base (sin IVA) si es posible
            precio_base = precio_unitario
            if iva_incluido is True and iva_porcentaje > 0:
                precio_base = int(precio_unitario / (1 + iva_porcentaje / 100))
            
            item = InvoiceItemReview(
                numero_item=item_number,
                codigo=codigo,
                descripcion=descripcion[:500],
                unidad_medida=unidad[:50] if unidad else '',
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                precio_base=precio_base,
                descuento=descuento,
                recargo=recargo,
                iva_porcentaje=iva_porcentaje,
                iva_valor=iva_valor,
                iva_incluido=iva_incluido,
                inc_porcentaje=inc_porcentaje,
                inc_valor=inc_valor,
                valor_total=valor_total,
                has_warning=False,
                warning_message=None,
                suggested_fix=None,
                irregularities=[]
            )
            
            # Agregar warnings si hay datos faltantes
            if not codigo:
                item.has_warning = True
                item.warning_message = "Producto sin código"
            if precio_unitario == 0 and valor_total == 0:
                item.has_warning = True
                item.warning_message = "Sin precio ni valor total"
            if iva_porcentaje > 0 and iva_valor == 0:
                item.has_warning = True
                item.warning_message = f"IVA {iva_porcentaje}% sin valor calculado"
            
            return item
            
        except Exception as e:
            logger.warning(f"Error parseando fila de item {item_number}: {e}")
            return None


    # ========================================
    # Extracción de Totales
    # ========================================
    
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
                        
                        # Descuento general
                        if ('descuento' in row_text or 'dcto' in row_text) and 'detalle' not in row_text:
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
        self.detected_structure = TableStructure.UNKNOWN
        self.column_mapping = None
        
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
                if not supplier['razon_social']:
                    self._add_warning('supplier_razon_social', 'No se encontró razón social del proveedor', severity='warning')
                
                # Extraer items de TODAS las páginas
                items = self._extract_items_from_tables(pdf, doc_type)
                if not items:
                    self._add_warning('items', 'No se encontraron productos en el documento', severity='warning')
                else:
                    logger.info(f"Items extraídos: {len(items)}, Estructura: {self.detected_structure.value}")
                
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
