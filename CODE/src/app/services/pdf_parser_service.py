"""
Servicio de parseo genérico de PDFs
Extrae datos de facturas de proveedores y archivos DIAN
"""
import re
from datetime import datetime
from typing import Dict, Optional, List, Any
from decimal import Decimal
import logging

try:
    import pdfplumber
    PDF_LIBRARY_AVAILABLE = True
except ImportError:
    PDF_LIBRARY_AVAILABLE = False
    logging.warning("pdfplumber no está disponible - instalar con: pip install pdfplumber")

logger = logging.getLogger(__name__)


class PDFParserService:
    """
    Parser genérico para PDFs de facturas
    Usa estrategias múltiples para adaptarse a diferentes formatos
    """
    
    # Patrones de extracción genéricos
    CUFE_PATTERN = r'[0-9a-fA-F]{96}'
    
    # Patrones de fecha (múltiples formatos)
    DATE_PATTERNS = [
        r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',  # 2025-07-11 o 2025/7/11
        r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # 11-07-2025 o 11/07/2025
        r'(\d{4})(\d{2})(\d{2})',  # 20250711
    ]
    
    # Patrones de número de factura
    INVOICE_NUMBER_PATTERNS = [
        r'(?:GRM|GRMZ)[\s]?(\d+)',  # GRM224813, GRMZ39813
        r'(?:Factura|Número|No\.?|#)[\s:]+([A-Z0-9\-]+)',  # Factura: 23986, No. 004D-6454
        r'(?:FEV|FV|AD)[\s]?([A-Z0-9\-]+)',  # FEV No. 123, FV09006851640112400000125
    ]
    
    # Patrones de total
    TOTAL_PATTERNS = [
        r'(?:TOTAL|Total|T\s*O\s*T\s*A\s*L)[\s:$]*([0-9,.]+)',
        r'(?:Total factura|Total documento|Valor a pagar)[\s:$COP]*([0-9,.]+)',
        r'(?:Total neto|Total a Pagar)[\s:$COP]*([0-9,.]+)',
    ]
    
    # Patrones de NIT
    NIT_PATTERN = r'(?:NIT|Nit)[\s:]+(\d{9,10}[-\d]?)'
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str, max_pages: int = 5) -> str:
        """
        Extrae texto de un PDF usando pdfplumber
        OPTIMIZADO: Solo procesa las primeras páginas (donde está la info importante)
        """
        if not PDF_LIBRARY_AVAILABLE:
            logger.error("pdfplumber no está disponible")
            return ""
        
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                # Solo procesar las primeras páginas (la info importante está al inicio)
                pages_to_process = min(len(pdf.pages), max_pages)
                
                for i in range(pages_to_process):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text_parts.append(page_text)
                    
                    # Si ya encontramos CUFE, podemos parar antes
                    combined_text = '\n'.join(text_parts)
                    if len(combined_text) > 2000 and re.search(r'[0-9a-fA-F]{96}', combined_text):
                        break
            
            return '\n'.join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    @staticmethod
    def extract_cufe(text: str) -> Optional[str]:
        """
        Extrae el código CUFE/CUDE/CUDS (96 caracteres hexadecimales)
        """
        # Buscar patrón de 96 caracteres hex
        matches = re.findall(PDFParserService.CUFE_PATTERN, text, re.IGNORECASE)
        
        if matches:
            # Puede estar dividido en múltiples líneas, intentar unir
            cufe = matches[0]
            
            # Si encontramos múltiples coincidencias cercanas, unirlas
            if len(cufe) < 96 and len(matches) > 1:
                cufe = ''.join(matches[:3])  # Unir hasta 3 fragmentos
            
            # Limpiar y validar
            cufe = cufe.strip().replace('\n', '').replace(' ', '')
            
            if len(cufe) == 96:
                return cufe.lower()
        
        return None
    
    @staticmethod
    def extract_date(text: str) -> Optional[datetime]:
        """
        Extrae fecha usando múltiples patrones
        """
        for pattern in PDFParserService.DATE_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    match = matches[0]
                    if len(match[0]) == 4:  # YYYY-MM-DD
                        year, month, day = int(match[0]), int(match[1]), int(match[2])
                    else:  # DD-MM-YYYY
                        day, month, year = int(match[0]), int(match[1]), int(match[2])
                    
                    return datetime(year, month, day)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    @staticmethod
    def extract_invoice_number(text: str) -> Optional[str]:
        """
        Extrae número de factura usando múltiples patrones
        """
        for pattern in PDFParserService.INVOICE_NUMBER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip() if match.lastindex else match.group(0).strip()
        
        return None
    
    @staticmethod
    def extract_total(text: str) -> Optional[Decimal]:
        """
        Extrae el total de la factura
        """
        for pattern in PDFParserService.TOTAL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Limpiar formato de moneda
                    total_str = match.group(1)
                    total_str = total_str.replace('.', '').replace(',', '.')  # 35.000,00 -> 35000.00
                    total_str = re.sub(r'[^\d.]', '', total_str)  # Eliminar caracteres no numéricos
                    
                    return Decimal(total_str)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    @staticmethod
    def extract_provider_name(text: str) -> Optional[str]:
        """
        Extrae nombre del proveedor usando heurísticas
        """
        # Buscar después de "Vendedor:", "Razón Social:", "Emisor:"
        patterns = [
            r'(?:Vendedor|Razón Social|Emisor)[\s:]+([A-ZÁ-Ú\s]+(?:LTDA|SAS|S\.A\.S|S\.A\.|SA))',
            r'(?:Datos del Emisor|Datos del vendedor)[\s\S]{0,100}?([A-ZÁ-Ú\s]+(?:LTDA|SAS|S\.A\.S|S\.A\.|SA))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Si no encuentra, buscar líneas con NIT y tomar la anterior
        nit_match = re.search(PDFParserService.NIT_PATTERN, text)
        if nit_match:
            # Buscar líneas antes del NIT
            lines_before = text[:nit_match.start()].split('\n')
            for line in reversed(lines_before[-5:]):  # Últimas 5 líneas antes del NIT
                line = line.strip()
                if len(line) > 5 and any(keyword in line.upper() for keyword in ['LTDA', 'SAS', 'S.A.S', 'S.A']):
                    return line
        
        return None
    
    @staticmethod
    def extract_nit(text: str) -> Optional[str]:
        """
        Extrae NIT del proveedor
        """
        match = re.search(PDFParserService.NIT_PATTERN, text)
        if match:
            return match.group(1).strip()
        return None
    
    @classmethod
    def parse_provider_invoice(cls, pdf_path: str) -> Dict[str, Any]:
        """
        Parsea una factura de proveedor (genérico)
        Extrae: CUFE, Proveedor, Fecha, Número, Total
        """
        text = cls.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {'error': 'No se pudo extraer texto del PDF'}
        
        result = {
            'cufe': cls.extract_cufe(text),
            'proveedor_nombre': cls.extract_provider_name(text),
            'proveedor_nit': cls.extract_nit(text),
            'fecha_emision': cls.extract_date(text),
            'numero_factura': cls.extract_invoice_number(text),
            'total_factura': cls.extract_total(text),
            'raw_text': text,  # Guardar texto completo para debugging
        }
        
        return result
    
    @classmethod
    def parse_dian_document(cls, pdf_path: str) -> Dict[str, Any]:
        """
        Parsea un documento DIAN (más estructurado)
        Extrae TODOS los datos posibles
        """
        text = cls.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {'error': 'No se pudo extraer texto del PDF'}
        
        result = {
            'cufe': cls.extract_cufe(text),
            'tipo_documento': cls._extract_document_type(text),
            'numero_documento': cls.extract_invoice_number(text),
            'fecha_emision': cls.extract_date(text),
            
            # Emisor
            'emisor': cls._extract_emisor(text),
            
            # Adquiriente
            'adquiriente': cls._extract_adquiriente(text),
            
            # Condiciones comerciales
            'forma_pago': cls._extract_forma_pago(text),
            'medio_pago': cls._extract_medio_pago(text),
            'moneda': cls._extract_moneda(text),
            
            # Totales
            'totales': cls._extract_totales(text),
            
            # Productos
            'productos': cls._extract_productos(text),
            
            # Información técnica
            'proveedor_tecnologico': cls._extract_proveedor_tecnologico(text),
            'resolucion': cls._extract_resolucion(text),
            
            'raw_text': text,
        }
        
        return result
    
    @staticmethod
    def _extract_document_type(text: str) -> Optional[str]:
        """Extrae tipo de documento (FACTURA, POS, etc)"""
        if 'DOCUMENTO EQUIVALENTE POS' in text.upper():
            return 'POS'
        elif 'FACTURA ELECTRÓNICA' in text.upper() or 'FACTURA ELECTRONICA' in text.upper():
            return 'FACTURA'
        return None
    
    @staticmethod
    def _extract_emisor(text: str) -> Dict[str, Optional[str]]:
        """Extrae datos del emisor/vendedor"""
        emisor = {}
        
        # Razón social
        match = re.search(r'(?:Razón social|Razon Social)[\s:]+([^\n]+)', text, re.IGNORECASE)
        emisor['razon_social'] = match.group(1).strip() if match else None
        
        # NIT
        match = re.search(r'(?:NIT|Nit|Número de documento)[\s:]+(\d{9,10}[-\d]?)', text)
        emisor['nit'] = match.group(1).strip() if match else None
        
        # Dirección
        match = re.search(r'(?:Dirección|Direccion)[\s:]+([^\n]+)', text, re.IGNORECASE)
        emisor['direccion'] = match.group(1).strip() if match else None
        
        # Teléfono
        match = re.search(r'(?:Teléfono|Telefono|Móvil|Movil)[\s:]+([^\n]+)', text, re.IGNORECASE)
        emisor['telefono'] = match.group(1).strip() if match else None
        
        # Email
        match = re.search(r'(?:Correo|Email)[\s:]+([^\n]+)', text, re.IGNORECASE)
        emisor['email'] = match.group(1).strip() if match else None
        
        # Régimen fiscal
        match = re.search(r'(?:Régimen fiscal|Regimen fiscal)[\s:]+([^\n]+)', text, re.IGNORECASE)
        emisor['regimen_fiscal'] = match.group(1).strip() if match else None
        
        return emisor
    
    @staticmethod
    def _extract_adquiriente(text: str) -> Dict[str, Optional[str]]:
        """Extrae datos del adquiriente/comprador"""
        adquiriente = {}
        
        # Buscar sección de adquiriente
        match = re.search(r'(?:Datos del adquiriente|Datos del Cliente|DATOS DEL CLIENTE)([\s\S]{0,500})', text, re.IGNORECASE)
        if match:
            section = match.group(1)
            
            # Razón social
            match = re.search(r'(?:Razón social|Nombre)[\s:]+([^\n]+)', section, re.IGNORECASE)
            adquiriente['razon_social'] = match.group(1).strip() if match else None
            
            # NIT
            match = re.search(r'(?:NIT|Nit)[\s:]+(\d{9,10}[-\d]?)', section)
            adquiriente['nit'] = match.group(1).strip() if match else None
        
        return adquiriente
    
    @staticmethod
    def _extract_forma_pago(text: str) -> Optional[str]:
        """Extrae forma de pago"""
        match = re.search(r'(?:Forma de pago|Condicion de Pago)[\s:]+([^\n]+)', text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    @staticmethod
    def _extract_medio_pago(text: str) -> Optional[str]:
        """Extrae medio de pago"""
        match = re.search(r'(?:Medio de Pago)[\s:]+([^\n]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Buscar en el texto: EFECTIVO, TARJETA CREDITO, etc
        if 'EFECTIVO' in text.upper():
            return 'Efectivo'
        elif 'TARJETA CREDITO' in text.upper() or 'TARJETA CRÉDITO' in text.upper():
            return 'Tarjeta Crédito'
        elif 'TARJETA DEBITO' in text.upper() or 'TARJETA DÉBITO' in text.upper():
            return 'Tarjeta Débito'
        
        return None
    
    @staticmethod
    def _extract_moneda(text: str) -> str:
        """Extrae moneda (por defecto COP)"""
        match = re.search(r'(?:Moneda|MONEDA)[\s:]+([A-Z]{3})', text)
        return match.group(1).strip() if match else 'COP'
    
    @staticmethod
    def _extract_totales(text: str) -> Dict[str, Optional[Decimal]]:
        """Extrae todos los totales financieros"""
        totales = {}
        
        patterns = {
            'subtotal': r'(?:Subtotal|SUBTOTAL)[\s:$COP]*([0-9,.]+)',
            'total_bruto': r'(?:Total bruto|Total Bruto)[\s:$COP]*([0-9,.]+)',
            'total_iva': r'(?:Total IVA|IVA|Total impuesto)[\s:$COP]*([0-9,.]+)',
            'total_neto': r'(?:Total neto|Total documento|Total factura)[\s:$COP]*([0-9,.]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace('.', '').replace(',', '.')
                    value_str = re.sub(r'[^\d.]', '', value_str)
                    totales[key] = Decimal(value_str)
                except:
                    totales[key] = None
            else:
                totales[key] = None
        
        return totales
    
    @staticmethod
    def _extract_productos(text: str) -> List[Dict[str, Any]]:
        """
        Extrae productos del documento DIAN
        OPTIMIZADO: Extracción simplificada y rápida
        """
        productos = []
        
        # Buscar sección de productos (limitar búsqueda)
        match = re.search(r'(?:Detalles de productos|Detalle de Ítems|DETALLE)([\s\S]{0,5000}?)(?:Notas finales|Datos totales|Total|TOTAL)', text, re.IGNORECASE)
        if not match:
            # Intentar buscar tabla simple
            return productos
        
        productos_section = match.group(1)
        lines = productos_section.split('\n')
        
        # Buscar solo códigos EAN/UPC y descripciones básicas
        for line in lines[:100]:  # Limitar a 100 líneas
            line = line.strip()
            if len(line) < 5:
                continue
            
            # Buscar código de producto (EAN/UPC)
            codigo_match = re.search(r'\b(\d{13}|\d{12}|\d{8})\b', line)
            if codigo_match:
                codigo = codigo_match.group(1)
                
                # Extraer descripción (texto después del código)
                desc = line.replace(codigo, '').strip()
                desc = re.sub(r'[\d,.$]+', '', desc).strip()  # Quitar números
                
                if len(desc) > 5:
                    productos.append({
                        'codigo_producto': codigo,
                        'descripcion': desc[:200],  # Limitar longitud
                        'cantidad': None,
                        'precio_unitario': None,
                        'iva_porcentaje': None,
                        'total_item': None,
                    })
                
                # Limitar a 50 productos
                if len(productos) >= 50:
                    break
        
        return productos
    
    @staticmethod
    def _extract_proveedor_tecnologico(text: str) -> Optional[str]:
        """Extrae proveedor tecnológico"""
        match = re.search(r'(?:Proveedor Tecnológico|Proveedor Tecnologico|Fabricante del Software)[\s:]+([^\n]+)', text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    @staticmethod
    def _extract_resolucion(text: str) -> Dict[str, Optional[str]]:
        """Extrae información de resolución DIAN"""
        resolucion = {}
        
        match = re.search(r'(?:Número de Autorización|Numero)[\s:]+(\d+)', text, re.IGNORECASE)
        resolucion['numero'] = match.group(1).strip() if match else None
        
        match = re.search(r'(?:Rango desde)[\s:]+[\'"]?([A-Z0-9]+)[\'"]?', text, re.IGNORECASE)
        resolucion['rango_desde'] = match.group(1).strip() if match else None
        
        match = re.search(r'(?:Rango hasta)[\s:]+[\'"]?([A-Z0-9]+)[\'"]?', text, re.IGNORECASE)
        resolucion['rango_hasta'] = match.group(1).strip() if match else None
        
        return resolucion
