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
    
    # Patrones de regex compilados para mejor rendimiento
    PATTERNS = {
        'cufe': re.compile(r'CUFE\s*:\s*\n?([a-f0-9]{96})', re.IGNORECASE),
        'cude': re.compile(r'CUDE:\s*\n?([a-f0-9]{96})', re.IGNORECASE),
        'numero_factura': re.compile(r'Número de Factura:\s*([^\s]+)'),
        'numero_documento_pos': re.compile(r'Número de documento:\s*([A-Z0-9]+)'),
        'fecha_emision': re.compile(r'Fecha de Emisión:\s*(\d{2}/\d{2}/\d{4})'),
        'fecha_expedicion': re.compile(r'Fecha y hora de expedición:\s*([^\n]+)'),
        'fecha_vencimiento': re.compile(r'Fecha de Vencimiento:\s*(\d{2}/\d{2}/\d{4})'),
        'forma_pago': re.compile(r'Forma de pago:\s*([^\n]+)'),
        'medio_pago': re.compile(r'Medio de Pago:\s*([^\n]+)'),
        'vendedor_razon_social': re.compile(r'Datos del Emisor.*?Razón Social:\s*([^\n]+)', re.DOTALL),
        'vendedor_nit': re.compile(r'Nit del Emisor:\s*(\d+)'),
        'vendedor_direccion': re.compile(r'Dirección:\s*([^\n]+)'),
        'vendedor_telefono': re.compile(r'Teléfono / Móvil:\s*([^\n]+)'),
        'vendedor_correo': re.compile(r'Correo:\s*([^\n]+)'),
        'vendedor_departamento': re.compile(r'Departamento:\s*([^\n]+)'),
        'vendedor_ciudad': re.compile(r'Municipio / Ciudad:\s*([^\n]+)'),
        'vendedor_pos_razon': re.compile(r'Datos del vendedor\s*\n.*?Razón social:\s*([^\n]+)', re.DOTALL),
        'vendedor_pos_nit': re.compile(r'Número de documento:\s*(\d{9})'),
        'subtotal': re.compile(r'Subtotal[:\s]*\$?\s*([\d.,]+)', re.IGNORECASE),
        'total_iva': re.compile(r'(?:Total\s+)?IVA[:\s]*\$?\s*([\d.,]+)', re.IGNORECASE),
        'total_neto': re.compile(r'Total\s+(?:neto|a\s+pagar)[:\s]*\$?\s*([\d.,]+)', re.IGNORECASE),
        'descuento': re.compile(r'Descuento[:\s]*\$?\s*([\d.,]+)', re.IGNORECASE),
    }
    
    def __init__(self):
        self.warnings: List[ExtractionWarning] = []

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
            cleaned = re.sub(r'[^\d.,]', '', str(value))
            if ',' in cleaned:
                cleaned = cleaned.replace(',', '.')
            return int(float(cleaned))
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
        cleaned = re.sub(r'[^\w\-]', '', cleaned)
        return cleaned
    
    @staticmethod
    def normalize_text(value: str) -> str:
        """Normaliza texto: trim, espacios múltiples, saltos de línea"""
        if not value:
            return ""
        cleaned = str(value).strip()
        cleaned = re.sub(r'[\n\r]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned
    
    @staticmethod
    def normalize_nit(value: str) -> str:
        """Normaliza NIT: solo dígitos"""
        if not value:
            return ""
        return re.sub(r'[^\d]', '', str(value))
    
    @staticmethod
    def parse_date(value: str) -> Optional[datetime]:
        """Parsea fecha en varios formatos"""
        if not value:
            return None
        
        formats = [
            '%d/%m/%Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S',
        ]
        cleaned = re.sub(r'[+-]\d{2}:\d{2}$', '', value.strip())
        
        for fmt in formats:
            try:
                return datetime.strptime(cleaned, fmt)
            except ValueError:
                continue
        return None

    # ========================================
    # Métodos de Extracción
    # ========================================
    
    def _extract_match(self, pattern_name: str, text: str) -> Optional[str]:
        """Extrae un valor usando un patrón predefinido"""
        pattern = self.PATTERNS.get(pattern_name)
        if not pattern:
            return None
        match = pattern.search(text)
        return match.group(1).strip() if match else None
    
    def _detect_document_type(self, text: str) -> DocumentTypeEnum:
        """Detecta el tipo de documento"""
        if "FACTURA ELECTRÓNICA DE VENTA" in text:
            return DocumentTypeEnum.FACTURA
        elif "DOCUMENTO EQUIVALENTE POS" in text:
            return DocumentTypeEnum.POS
        else:
            self._add_warning("document_type", "No se pudo detectar el tipo de documento", severity="error")
            return DocumentTypeEnum.FACTURA
    
    def _add_warning(self, field: str, message: str, original_value: str = None,
                     suggested_value: str = None, severity: str = "warning"):
        """Agrega una advertencia a la lista"""
        self.warnings.append(ExtractionWarning(
            field=field, message=message, original_value=original_value,
            suggested_value=suggested_value, severity=severity
        ))
    
    def _extract_supplier_factura(self, text: str) -> Dict[str, str]:
        """Extrae datos del proveedor de una factura electrónica"""
        return {
            'nit': self.normalize_nit(self._extract_match('vendedor_nit', text) or ''),
            'razon_social': self.normalize_text(self._extract_match('vendedor_razon_social', text) or ''),
            'direccion': self.normalize_text(self._extract_match('vendedor_direccion', text) or ''),
            'telefono': self.normalize_text(self._extract_match('vendedor_telefono', text) or ''),
            'correo': self.normalize_text(self._extract_match('vendedor_correo', text) or ''),
            'departamento': self.normalize_text(self._extract_match('vendedor_departamento', text) or ''),
            'ciudad': self.normalize_text(self._extract_match('vendedor_ciudad', text) or ''),
        }
    
    def _extract_supplier_pos(self, text: str) -> Dict[str, str]:
        """Extrae datos del proveedor de un documento POS"""
        return {
            'nit': self.normalize_nit(self._extract_match('vendedor_pos_nit', text) or ''),
            'razon_social': self.normalize_text(self._extract_match('vendedor_pos_razon', text) or ''),
            'direccion': '', 'telefono': '', 'correo': '', 'departamento': '', 'ciudad': '',
        }
    
    def _extract_items_from_tables(self, pdf: pdfplumber.PDF, doc_type: DocumentTypeEnum) -> List[InvoiceItemReview]:
        """Extrae items de las tablas del PDF"""
        items = []
        item_number = 0
        
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                
                header_row = None
                for i, row in enumerate(table):
                    row_text = ' '.join([str(c or '') for c in row]).lower()
                    if 'código' in row_text or 'descripcion' in row_text or 'cantidad' in row_text:
                        header_row = i
                        break
                
                if header_row is None:
                    continue
                
                for row in table[header_row + 1:]:
                    if not row or len(row) < 3:
                        continue
                    first_cell = str(row[0] or '').lower()
                    if any(x in first_cell for x in ['subtotal', 'total', 'iva', 'descuento']):
                        continue
                    
                    item = self._parse_item_row(row, doc_type, item_number + 1)
                    if item:
                        items.append(item)
                        item_number += 1
        return items

    def _parse_item_row(self, row: List, doc_type: DocumentTypeEnum, item_number: int) -> Optional[InvoiceItemReview]:
        """Parsea una fila de la tabla de productos"""
        try:
            cells = [self.normalize_text(str(c or '')) for c in row]
            if len(cells) < 5:
                return None
            
            codigo, descripcion, unidad = '', '', ''
            cantidad, precio, iva_pct, iva_valor, valor_total, descuento = 1, 0, 0.0, 0, 0, 0
            
            if cells[0].isdigit() and int(cells[0]) < 1000:
                codigo = self.normalize_code(cells[1])
                descripcion = cells[2]
                unidad = cells[3] if len(cells) > 3 else ''
                cantidad = self.normalize_quantity(cells[4]) if len(cells) > 4 else 1
                precio = self.normalize_money(cells[5]) if len(cells) > 5 else 0
            else:
                codigo = self.normalize_code(cells[0])
                descripcion = cells[1]
                unidad = cells[2] if len(cells) > 2 else ''
                cantidad = self.normalize_quantity(cells[3]) if len(cells) > 3 else 1
                precio = self.normalize_money(cells[4]) if len(cells) > 4 else 0
            
            for i, cell in enumerate(reversed(cells)):
                cell_clean = cell.replace('%', '').strip()
                if i == 0 and cell_clean:
                    valor_total = self.normalize_money(cell)
                elif self.normalize_percentage(cell_clean) in [0, 5, 19]:
                    iva_pct = self.normalize_percentage(cell_clean)
            
            if not descripcion or len(descripcion) < 2:
                return None
            
            if valor_total == 0 and precio > 0:
                valor_total = cantidad * precio
            if iva_pct > 0 and valor_total > 0:
                iva_valor = int(valor_total * iva_pct / (100 + iva_pct))
            
            item = InvoiceItemReview(
                numero_item=item_number, codigo=codigo, descripcion=descripcion,
                unidad_medida=unidad.split('|')[0].strip() if '|' in unidad else unidad,
                cantidad=cantidad, precio_unitario=precio, descuento=descuento, recargo=0,
                iva_porcentaje=iva_pct, iva_valor=iva_valor, inc_porcentaje=0, inc_valor=0,
                valor_total=valor_total, has_warning=False, warning_message=None, suggested_fix=None
            )
            
            if not codigo:
                item.has_warning = True
                item.warning_message = "Producto sin código"
                item.suggested_fix = "Agregar código manualmente"
            if precio == 0:
                item.has_warning = True
                item.warning_message = "Precio unitario es 0"
            
            return item
        except Exception as e:
            logger.warning(f"Error parseando fila de item: {e}")
            return None
    
    def _extract_totals(self, pdf: pdfplumber.PDF) -> Dict[str, int]:
        """Extrae totales del documento"""
        totals = {'subtotal': 0, 'descuento': 0, 'total_bruto': 0, 'total_iva': 0, 'total_neto': 0}
        full_text = ''
        
        for page in pdf.pages:
            text = page.extract_text() or ''
            full_text += text + '\n'
            
            for table in page.extract_tables():
                for row in table:
                    row_text = ' '.join([str(c or '') for c in row])
                    if 'subtotal' in row_text.lower():
                        for cell in row:
                            val = self.normalize_money(str(cell or ''))
                            if val > 0:
                                totals['subtotal'] = max(totals['subtotal'], val)
                    if 'total' in row_text.lower() and 'iva' in row_text.lower():
                        for cell in row:
                            val = self.normalize_money(str(cell or ''))
                            if val > 0 and val < totals.get('subtotal', float('inf')):
                                totals['total_iva'] = max(totals['total_iva'], val)
                    if 'total neto' in row_text.lower() or 'total a pagar' in row_text.lower():
                        for cell in row:
                            val = self.normalize_money(str(cell or ''))
                            if val > 0:
                                totals['total_neto'] = max(totals['total_neto'], val)
        
        if totals['subtotal'] == 0:
            match = self.PATTERNS['subtotal'].search(full_text)
            if match:
                totals['subtotal'] = self.normalize_money(match.group(1))
        if totals['total_iva'] == 0:
            match = self.PATTERNS['total_iva'].search(full_text)
            if match:
                totals['total_iva'] = self.normalize_money(match.group(1))
        if totals['total_neto'] == 0:
            match = self.PATTERNS['total_neto'].search(full_text)
            if match:
                totals['total_neto'] = self.normalize_money(match.group(1))
        if totals['total_bruto'] == 0:
            totals['total_bruto'] = totals['subtotal'] - totals['descuento']
        
        return totals

    # ========================================
    # Método Principal de Extracción
    # ========================================
    
    def extract_from_pdf(self, pdf_path: str, filename: str = None) -> Tuple[ExtractedInvoiceData, List[ExtractionWarning]]:
        """
        Extrae todos los datos de un PDF de factura.
        Returns: Tuple con (datos extraídos, lista de advertencias)
        """
        self.warnings = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page_text = pdf.pages[0].extract_text() or ''
                doc_type = self._detect_document_type(first_page_text)
                
                if doc_type == DocumentTypeEnum.FACTURA:
                    cufe_cude = self._extract_match('cufe', first_page_text) or ''
                else:
                    cufe_cude = self._extract_match('cude', first_page_text) or ''
                
                if not cufe_cude:
                    self._add_warning('cufe_cude', 'No se encontró código CUFE/CUDE', severity='error')
                
                if doc_type == DocumentTypeEnum.FACTURA:
                    numero_doc = self._extract_match('numero_factura', first_page_text) or ''
                    fecha_str = self._extract_match('fecha_emision', first_page_text) or ''
                else:
                    numero_doc = self._extract_match('numero_documento_pos', first_page_text) or ''
                    fecha_str = self._extract_match('fecha_expedicion', first_page_text) or ''
                
                fecha_venc_str = self._extract_match('fecha_vencimiento', first_page_text)
                forma_pago = self._extract_match('forma_pago', first_page_text)
                medio_pago = self._extract_match('medio_pago', first_page_text)
                
                if doc_type == DocumentTypeEnum.FACTURA:
                    supplier = self._extract_supplier_factura(first_page_text)
                else:
                    supplier = self._extract_supplier_pos(first_page_text)
                
                if not supplier['nit']:
                    self._add_warning('supplier_nit', 'No se encontró NIT del proveedor', severity='error')
                if not supplier['razon_social']:
                    self._add_warning('supplier_razon_social', 'No se encontró razón social del proveedor', severity='error')
                
                items = self._extract_items_from_tables(pdf, doc_type)
                if not items:
                    self._add_warning('items', 'No se encontraron productos en el documento', severity='warning')
                
                totals = self._extract_totals(pdf)
                
                items_total = sum(item.valor_total for item in items)
                if totals['total_neto'] > 0 and abs(items_total - totals['total_neto']) > 100:
                    self._add_warning(
                        'totals',
                        f"La suma de items ({items_total:,}) no coincide con el total ({totals['total_neto']:,})",
                        original_value=str(items_total), suggested_value=str(totals['total_neto']), severity='warning'
                    )
                
                extracted = ExtractedInvoiceData(
                    cufe_cude=cufe_cude, document_type=doc_type, numero_documento=numero_doc,
                    fecha_emision=fecha_str, fecha_vencimiento=fecha_venc_str,
                    forma_pago=forma_pago, medio_pago=medio_pago,
                    supplier_nit=supplier['nit'], supplier_razon_social=supplier['razon_social'],
                    supplier_direccion=supplier['direccion'], supplier_telefono=supplier['telefono'],
                    supplier_correo=supplier['correo'], supplier_ciudad=supplier['ciudad'],
                    supplier_departamento=supplier['departamento'],
                    subtotal=totals['subtotal'], descuento=totals['descuento'],
                    total_bruto=totals['total_bruto'], total_iva=totals['total_iva'],
                    total_neto=totals['total_neto'], items=items,
                    is_valid=not any(w.severity == 'error' for w in self.warnings),
                    is_duplicate=False, warnings=self.warnings, archivo_nombre=filename
                )
                return extracted, self.warnings
                
        except Exception as e:
            logger.error(f"Error extrayendo datos del PDF: {e}", exc_info=True)
            self._add_warning('general', f'Error procesando el archivo: {str(e)}', severity='error')
            
            return ExtractedInvoiceData(
                cufe_cude='', document_type=DocumentTypeEnum.FACTURA, numero_documento='',
                fecha_emision='', supplier_nit='', supplier_razon_social='',
                items=[], is_valid=False, warnings=self.warnings, archivo_nombre=filename
            ), self.warnings
