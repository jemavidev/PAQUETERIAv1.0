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
        r'(?:N[uú]mero|Numero|No\.?|#)[\s:]*(?:de\s+)?(?:factura|documento)?[\s:]*([A-Z0-9\-]+)',  # Número: 123, No. factura: ABC-123
        r'(?:Factura|FACTURA)[\s:]+(?:No\.?|N[uú]mero)?[\s:]*([A-Z0-9\-]+)',  # Factura: 123, FACTURA No. 456
        r'(?:FEV|FV|AD|GRMZ?|POS)[\s\-]?(\d+)',  # FEV123, FV-456, AD789, GRM123, GRMZ456, POS789
        r'Documento[\s:]+([A-Z0-9\-]+)',  # Documento: 123
        r'(?:^|\n)([A-Z]{2,4}[\s\-]?\d{4,})',  # Patrón genérico: ABC1234, XY-5678
    ]
    
    # Patrones de total
    TOTAL_PATTERNS = [
        r'(?:Total\s+a\s+pagar|Valor\s+a\s+pagar|Total\s+factura|Total\s+documento)[\s:$COP]*([0-9,.]+)',  # Más específico primero
        r'(?:Total\s+neto|Neto\s+a\s+pagar)[\s:$COP]*([0-9,.]+)',
        r'(?:TOTAL|Total|T\s*O\s*T\s*A\s*L)[\s:$COP]*([0-9,.]+)',  # Genérico al final
        r'(?:Valor\s+total|Total\s+general)[\s:$COP]*([0-9,.]+)',
    ]
    
    # Patrones de NIT
    NIT_PATTERN = r'(?:NIT|Nit)[\s:]+(\d{9,10}[-\d]?)'
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str, max_pages: int = 5) -> str:
        """
        Extrae texto de un PDF usando pdfplumber
        OPTIMIZADO: Solo procesa las primeras páginas (donde está la info importante)
        Para documentos DIAN, usar max_pages=999 para procesar todas las páginas
        """
        if not PDF_LIBRARY_AVAILABLE:
            logger.error("❌ pdfplumber no está disponible - instalar con: pip install pdfplumber")
            return ""
        
        try:
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                # Procesar páginas según el límite especificado
                pages_to_process = min(len(pdf.pages), max_pages)
                logger.info(f"📄 Procesando {pages_to_process} de {len(pdf.pages)} páginas del PDF")
                
                for i in range(pages_to_process):
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text_parts.append(page_text)
                        logger.debug(f"   Página {i+1}: {len(page_text)} caracteres extraídos")
            
            total_text = '\n'.join(text_parts)
            logger.info(f"📊 Total extraído: {len(total_text)} caracteres")
            return total_text
        except Exception as e:
            logger.error(f"❌ Error extracting text from PDF: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ""
    
    @staticmethod
    def extract_cufe(text: str) -> Optional[str]:
        """
        Extrae el código CUFE/CUDE/CUDS (96 caracteres hexadecimales)
        Soporta múltiples formatos:
        - 96 caracteres consecutivos
        - CUFE dividido en múltiples líneas
        - CUFE con espacios o separadores
        """
        if not text:
            logger.warning("⚠️ Texto vacío, no se puede extraer CUFE")
            return None
        
        logger.info(f"🔍 Buscando CUFE en texto de {len(text)} caracteres")
        
        # ESTRATEGIA 1: Patrón estándar (96 caracteres consecutivos)
        matches = re.findall(PDFParserService.CUFE_PATTERN, text, re.IGNORECASE)
        if matches:
            logger.info(f"✅ Encontrados {len(matches)} patrones de 96 caracteres hex")
            cufe = matches[0].strip().replace('\n', '').replace(' ', '').lower()
            if len(cufe) == 96:
                logger.info(f"✅ CUFE válido extraído (estándar): {cufe[:20]}...{cufe[-20:]}")
                return cufe
        
        # ESTRATEGIA 2: CUFE después de palabra clave (dividido en líneas)
        logger.info("🔍 Buscando CUFE dividido después de palabra clave...")
        keywords = ['CUFE:', 'CUDE:', 'CUDS:', 'Cufe:', 'Cude:', 'Cuds:']
        for keyword in keywords:
            if keyword in text:
                # Encontrar posición de la palabra clave
                idx = text.find(keyword)
                # Saltar la palabra clave y cualquier espacio/salto de línea
                start_idx = idx + len(keyword)
                # Extraer las siguientes 300 caracteres (suficiente para CUFE dividido)
                section = text[start_idx:start_idx+300]
                
                # Extraer solo caracteres hexadecimales (ignorar espacios, saltos de línea, etc)
                hex_chars = re.findall(r'[0-9a-fA-F]', section, re.IGNORECASE)
                cufe = ''.join(hex_chars)
                
                # Tomar los primeros 96 caracteres
                if len(cufe) >= 96:
                    cufe = cufe[:96].lower()
                    logger.info(f"✅ CUFE válido extraído (después de '{keyword}'): {cufe[:20]}...{cufe[-20:]}")
                    return cufe
                else:
                    logger.info(f"   Encontrados {len(cufe)} caracteres hex después de '{keyword}' (insuficiente)")
        
        # ESTRATEGIA 3: Buscar múltiples fragmentos de 32 caracteres y unirlos
        logger.info("🔍 Buscando fragmentos de CUFE para unir...")
        shorter_matches = re.findall(r'[0-9a-fA-F]{32}', text, re.IGNORECASE)
        if len(shorter_matches) >= 3:
            # Intentar unir los primeros 3 fragmentos de 32 caracteres
            cufe = ''.join(shorter_matches[:3]).lower()
            if len(cufe) == 96:
                logger.info(f"✅ CUFE válido extraído (uniendo 3 fragmentos): {cufe[:20]}...{cufe[-20:]}")
                return cufe
            else:
                logger.info(f"   Unión de fragmentos resultó en {len(cufe)} caracteres (esperado: 96)")
        
        # ESTRATEGIA 4: CUFE con espacios (eliminar espacios y unir)
        logger.info("🔍 Buscando CUFE con espacios...")
        # Buscar secuencias de hex con espacios opcionales
        pattern = r'([0-9a-fA-F\s]{100,200})'
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned = re.sub(r'[^0-9a-fA-F]', '', match)
            if len(cleaned) >= 96:
                cufe = cleaned[:96].lower()
                logger.info(f"✅ CUFE válido extraído (con espacios): {cufe[:20]}...{cufe[-20:]}")
                return cufe
        
        # No se encontró CUFE
        logger.warning("❌ No se pudo extraer CUFE con ninguna estrategia")
        shorter_matches = re.findall(r'[0-9a-fA-F]{16,}', text, re.IGNORECASE)
        if shorter_matches:
            logger.info(f"ℹ️ Encontrados {len(shorter_matches)} patrones hex:")
            for i, match in enumerate(shorter_matches[:5]):
                logger.info(f"   {i+1}. {match[:40]}... (longitud: {len(match)})")
        
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
    def extract_dian_date(text: str) -> Optional[datetime]:
        """
        Extrae fecha específicamente de documentos DIAN
        Busca en orden de prioridad:
        1. "Fecha y hora de expedición:" (formato ISO)
        2. "Fecha de Emisión:" (primera página)
        3. "Documento generado el:" (última página)
        """
        # ESTRATEGIA 1: Buscar "Fecha y hora de expedición:" (formato ISO más confiable)
        pattern_expedicion = r'Fecha\s+y\s+hora\s+de\s+expedici[oó]n[\s:]+(\d{4})-(\d{1,2})-(\d{1,2})'
        match = re.search(pattern_expedicion, text, re.IGNORECASE)
        if match:
            try:
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                fecha = datetime(year, month, day)
                logger.info(f"✅ Fecha extraída de 'Fecha y hora de expedición': {fecha.strftime('%Y-%m-%d')}")
                return fecha
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parseando fecha de expedición: {e}")
        
        # ESTRATEGIA 2: Buscar "Fecha de Emisión:" (más confiable)
        patterns_emision = [
            r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY o DD-MM-YYYY
            r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD o YYYY-MM-DD
        ]
        
        for pattern in patterns_emision:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                    else:  # DD-MM-YYYY
                        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                    
                    fecha = datetime(year, month, day)
                    logger.info(f"✅ Fecha extraída de 'Fecha de Emisión': {fecha.strftime('%Y-%m-%d')}")
                    return fecha
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parseando fecha de emisión: {e}")
                    continue
        
        # ESTRATEGIA 3: Buscar "Documento generado el:" (alternativa)
        patterns_generado = [
            r'Documento\s+generado\s+el[\s:]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
            r'Documento\s+generado\s+el[\s:]+(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD
        ]
        
        for pattern in patterns_generado:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    groups = match.groups()
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                    else:  # DD-MM-YYYY
                        day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                    
                    fecha = datetime(year, month, day)
                    logger.info(f"✅ Fecha extraída de 'Documento generado el': {fecha.strftime('%Y-%m-%d')}")
                    return fecha
                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parseando fecha generada: {e}")
                    continue
        
        # ESTRATEGIA 4: Fallback a patrones genéricos (si no encuentra las anteriores)
        logger.warning("⚠️ No se encontró 'Fecha y hora de expedición', 'Fecha de Emisión' ni 'Documento generado el', usando patrones genéricos")
        for pattern in PDFParserService.DATE_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    match = matches[0]
                    if len(match[0]) == 4:  # YYYY-MM-DD
                        year, month, day = int(match[0]), int(match[1]), int(match[2])
                    else:  # DD-MM-YYYY
                        day, month, year = int(match[0]), int(match[1]), int(match[2])
                    
                    fecha = datetime(year, month, day)
                    logger.info(f"✅ Fecha extraída (genérico): {fecha.strftime('%Y-%m-%d')}")
                    return fecha
                except (ValueError, IndexError):
                    continue
        
        logger.warning("❌ No se pudo extraer fecha del documento DIAN")
        return None
    
    @staticmethod
    def extract_invoice_number(text: str) -> Optional[str]:
        """
        Extrae número de factura usando múltiples patrones
        """
        for pattern in PDFParserService.INVOICE_NUMBER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                numero = match.group(1).strip()
                # Validar que no sea muy corto o solo texto genérico
                if len(numero) >= 3 and numero.upper() not in ['ELECTR', 'FACTURA', 'NUMERO', 'DOCUMENT']:
                    return numero
        
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
                    
                    # Remover puntos de miles y reemplazar coma decimal
                    # Formato colombiano: 1.234.567,89 -> 1234567.89
                    if ',' in total_str and '.' in total_str:
                        # Tiene ambos: puntos son miles, coma es decimal
                        total_str = total_str.replace('.', '').replace(',', '.')
                    elif ',' in total_str:
                        # Solo coma: es decimal
                        total_str = total_str.replace(',', '.')
                    elif total_str.count('.') > 1:
                        # Múltiples puntos: son miles
                        total_str = total_str.replace('.', '')
                    
                    # Eliminar caracteres no numéricos excepto punto decimal
                    total_str = re.sub(r'[^\d.]', '', total_str)
                    
                    if total_str:
                        total = Decimal(total_str)
                        # Validar que sea un valor razonable (mayor a 0, menor a 1 billón)
                        if 0 < total < 1000000000000:
                            return total
                except (ValueError, IndexError, Exception):
                    continue
        
        return None
    
    @staticmethod
    def extract_provider_name(text: str) -> Optional[str]:
        """
        Extrae nombre del proveedor usando heurísticas mejoradas
        """
        # Buscar después de palabras clave específicas
        patterns = [
            r'(?:Vendedor|Razón\s+Social|Razon\s+Social|Emisor|Proveedor)[\s:]+([A-ZÁÉÍÓÚÑ][A-ZÁ-Ú\s&.]+(?:LTDA|SAS|S\.A\.S|S\.A\.|SA|E\.U\.|EU))',
            r'(?:Datos\s+del\s+Emisor|Datos\s+del\s+vendedor)[\s\S]{0,200}?([A-ZÁÉÍÓÚÑ][A-ZÁ-Ú\s&.]+(?:LTDA|SAS|S\.A\.S|S\.A\.|SA|E\.U\.|EU))',
            r'(?:Nombre|Empresa)[\s:]+([A-ZÁÉÍÓÚÑ][A-ZÁ-Ú\s&.]+(?:LTDA|SAS|S\.A\.S|S\.A\.|SA|E\.U\.|EU))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                nombre = match.group(1).strip()
                # Validar longitud mínima y que no sea solo siglas
                if len(nombre) > 5 and not nombre.isupper() or len(nombre) > 15:
                    # Limpiar espacios múltiples
                    nombre = re.sub(r'\s+', ' ', nombre)
                    return nombre
        
        # Si no encuentra, buscar líneas con NIT y tomar la anterior
        nit_match = re.search(PDFParserService.NIT_PATTERN, text)
        if nit_match:
            # Buscar líneas antes del NIT
            lines_before = text[:nit_match.start()].split('\n')
            for line in reversed(lines_before[-10:]):  # Últimas 10 líneas antes del NIT
                line = line.strip()
                # Buscar línea con razón social (mayúsculas, con tipo de sociedad)
                if len(line) > 10 and any(keyword in line.upper() for keyword in ['LTDA', 'SAS', 'S.A.S', 'S.A', 'E.U']):
                    # Limpiar y validar
                    line = re.sub(r'\s+', ' ', line)
                    if len(line) > 5 and line.upper() not in ['LISA', 'ELECTR', 'FACTURA']:
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
        # Para documentos DIAN, necesitamos TODAS las páginas porque el total está en la última
        text = cls.extract_text_from_pdf(pdf_path, max_pages=999)
        
        if not text:
            return {'error': 'No se pudo extraer texto del PDF'}
        
        # Extraer totales
        totales_raw = cls._extract_totales(text)
        
        result = {
            'cufe': cls.extract_cufe(text),
            'tipo_documento': cls._extract_document_type(text),
            'numero_documento': cls.extract_invoice_number(text),
            'fecha_emision': cls.extract_dian_date(text),  # Usar método específico para DIAN
            
            # Emisor
            'emisor': cls._extract_emisor(text),
            
            # Adquiriente
            'adquiriente': cls._extract_adquiriente(text),
            
            # Condiciones comerciales
            'forma_pago': cls._extract_forma_pago(text),
            'medio_pago': cls._extract_medio_pago(text),
            'moneda': cls._extract_moneda(text),
            
            # Totales (estructura actualizada para coincidir con XML)
            'totales': {
                'subtotal': totales_raw.get('subtotal'),
                'total_impuestos': totales_raw.get('total_iva'),
                'total_pagar': totales_raw.get('total_pagar'),
            },
            
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
        """Extrae datos del emisor/vendedor (NO del adquiriente)"""
        emisor = {}
        
        # IMPORTANTE: Buscar específicamente en la sección "Datos del vendedor"
        # NO en "Datos del adquiriente" que aparece primero
        vendor_section_match = re.search(
            r'(?:Datos del vendedor|DATOS DEL VENDEDOR|Datos del emisor|DATOS DEL EMISOR)([\s\S]{0,800}?)(?:Detalles de productos|Detalle|DETALLE|Condiciones|CONDICIONES)',
            text,
            re.IGNORECASE
        )
        
        search_text = vendor_section_match.group(1) if vendor_section_match else text
        
        # Razón social - buscar en la sección del vendedor
        match = re.search(r'(?:Razón social|Razon Social)[\s:]+([^\n]+)', search_text, re.IGNORECASE)
        emisor['razon_social'] = match.group(1).strip() if match else None
        
        # NIT - buscar en la sección del vendedor
        match = re.search(r'(?:NIT|Nit|Número de documento)[\s:]+(\d{9,10}[-\d]?)', search_text)
        emisor['nit'] = match.group(1).strip() if match else None
        
        # Dirección
        match = re.search(r'(?:Dirección|Direccion)[\s:]+([^\n]+)', search_text, re.IGNORECASE)
        emisor['direccion'] = match.group(1).strip() if match else None
        
        # Teléfono
        match = re.search(r'(?:Teléfono|Telefono|Móvil|Movil)[\s:]+([^\n]+)', search_text, re.IGNORECASE)
        emisor['telefono'] = match.group(1).strip() if match else None
        
        # Email
        match = re.search(r'(?:Correo|Email)[\s:]+([^\n]+)', search_text, re.IGNORECASE)
        emisor['email'] = match.group(1).strip() if match else None
        
        # Régimen fiscal
        match = re.search(r'(?:Régimen fiscal|Regimen fiscal)[\s:]+([^\n]+)', search_text, re.IGNORECASE)
        emisor['regimen_fiscal'] = match.group(1).strip() if match else None
        
        return emisor
    
    @staticmethod
    def _extract_adquiriente(text: str) -> Dict[str, Optional[str]]:
        """Extrae datos del adquiriente/comprador (NO del vendedor)"""
        adquiriente = {}
        
        # Buscar específicamente en la sección de adquiriente
        match = re.search(r'(?:Datos del adquiriente|Datos del Cliente|DATOS DEL CLIENTE|DATOS DEL ADQUIRIENTE)([\s\S]{0,500}?)(?:Datos del vendedor|DATOS DEL VENDEDOR|Detalles|DETALLES)', text, re.IGNORECASE)
        if match:
            section = match.group(1)
            
            # Razón social
            match = re.search(r'(?:Razón social|Nombre)[\s:]+([^\n]+)', section, re.IGNORECASE)
            adquiriente['razon_social'] = match.group(1).strip() if match else None
            
            # NIT
            match = re.search(r'(?:NIT|Nit|NIT del adquiriente)[\s:]+(\d{9,10}[-\d]?)', section)
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
        """
        Extrae todos los totales financieros
        MEJORADO: Prioriza "Total factura (=)" como valor definitivo (última hoja)
        Estructura idéntica al XML para consistencia
        """
        totales = {}
        
        # PRIORIDAD 1: "Total factura (=)" o "Total documento" (VALOR DEFINITIVO)
        # Este es el valor que aparece en la última hoja y coincide con PayableAmount del XML
        patterns_definitivos = [
            r'Total\s+factura\s*\(=\)[\s\$COP\u3164]*([0-9,.]+)',
            r'Total\s+factura\s*\(\s*=\s*\)[\s\$COP\u3164]*([0-9,.]+)',
            r'Total\s+documento[\s\$COP\u3164]*([0-9,.]+)',
            r'Total\s+neto\s+factura[\s\$COP\u3164]*([0-9,.]+)',
        ]
        
        for pattern in patterns_definitivos:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace('.', '').replace(',', '.')
                    value_str = re.sub(r'[^\d.]', '', value_str)
                    totales['total_pagar'] = Decimal(value_str)
                    logger.info(f"✅ Total definitivo encontrado: ${totales['total_pagar']:,.2f}")
                    break
                except Exception as e:
                    logger.warning(f"Error parseando total definitivo: {e}")
                    continue
        
        # Si no se encontró el total definitivo, buscar alternativas
        if 'total_pagar' not in totales or totales['total_pagar'] is None:
            fallback_patterns = [
                r'TOTAL\s+A\s+PAGAR[\s\$COP\u3164]*([0-9,.]+)',
                r'Total\s+a\s+pagar[\s\$COP\u3164]*([0-9,.]+)',
                r'Valor\s+total[\s\$COP\u3164]*([0-9,.]+)',
                r'Total\s+general[\s\$COP\u3164]*([0-9,.]+)',
            ]
            
            for pattern in fallback_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        value_str = match.group(1).replace('.', '').replace(',', '.')
                        value_str = re.sub(r'[^\d.]', '', value_str)
                        totales['total_pagar'] = Decimal(value_str)
                        logger.info(f"✅ Total (fallback) encontrado: ${totales['total_pagar']:,.2f}")
                        break
                    except:
                        continue
        
        # Subtotal (antes de impuestos) - LineExtensionAmount en XML
        patterns_subtotal = [
            r'Subtotal[\s\$COP]*([0-9,.]+)',
            r'SUBTOTAL[\s\$COP]*([0-9,.]+)',
            r'Total\s+bruto[\s\$COP]*([0-9,.]+)',
            r'Base\s+imponible[\s\$COP]*([0-9,.]+)',
        ]
        
        for pattern in patterns_subtotal:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace('.', '').replace(',', '.')
                    value_str = re.sub(r'[^\d.]', '', value_str)
                    totales['subtotal'] = Decimal(value_str)
                    break
                except:
                    continue
        
        # Total IVA - TaxAmount en XML
        patterns_iva = [
            r'Total\s+IVA[\s\$COP]*([0-9,.]+)',
            r'Total\s+impuesto[\s\$COP]*([0-9,.]+)',
            r'IVA[\s\$COP]*([0-9,.]+)',
            r'Impuestos[\s\$COP]*([0-9,.]+)',
        ]
        
        for pattern in patterns_iva:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace('.', '').replace(',', '.')
                    value_str = re.sub(r'[^\d.]', '', value_str)
                    # Validar que sea un valor razonable (no capturar porcentajes)
                    valor = Decimal(value_str)
                    if valor > 100:  # IVA debe ser mayor a 100 para ser un monto
                        totales['total_iva'] = valor
                        break
                except:
                    continue
        
        # Asegurar que todos los campos existan (aunque sean None)
        if 'total_pagar' not in totales:
            totales['total_pagar'] = None
        if 'subtotal' not in totales:
            totales['subtotal'] = None
        if 'total_iva' not in totales:
            totales['total_iva'] = None
        
        # Logging para debugging
        logger.info(f"📊 Totales extraídos: Subtotal=${totales.get('subtotal', 0) or 0:,.2f}, IVA=${totales.get('total_iva', 0) or 0:,.2f}, Total=${totales.get('total_pagar', 0) or 0:,.2f}")
        
        return totales
    
    @staticmethod
    def _extract_iva_producto(line: str, next_line: str = None, precio_unitario: float = None, total_item: float = None, cantidad: float = None) -> tuple:
        """
        Extrae IVA del producto usando 3 estrategias
        
        Returns:
            tuple: (iva_porcentaje, iva_valor)
        """
        iva_porcentaje = 0.0
        iva_valor = 0.0
        
        # ESTRATEGIA 1: Buscar "19.00 %" o "19,00 %" en la línea actual
        iva_match = re.search(r'(\d{1,2})[.,]00\s*%', line)
        if iva_match:
            iva_porcentaje = float(iva_match.group(1))
            logger.debug(f"IVA encontrado (estrategia 1): {iva_porcentaje}%")
        
        # ESTRATEGIA 2: Buscar "IVA 19%" en línea siguiente
        if iva_porcentaje == 0.0 and next_line:
            iva_match = re.search(r'IVA\s+(\d{1,2})%', next_line, re.IGNORECASE)
            if iva_match:
                iva_porcentaje = float(iva_match.group(1))
                logger.debug(f"IVA encontrado (estrategia 2): {iva_porcentaje}%")
        
        # ESTRATEGIA 3: Calcular IVA desde precio_unitario y total_item
        if iva_porcentaje == 0.0 and precio_unitario and total_item and cantidad:
            try:
                subtotal_calculado = precio_unitario * cantidad
                if total_item > subtotal_calculado:
                    iva_valor = total_item - subtotal_calculado
                    if subtotal_calculado > 0:
                        iva_porcentaje = (iva_valor / subtotal_calculado) * 100
                        # Redondear a valores comunes (0, 5, 19)
                        if 18 <= iva_porcentaje <= 20:
                            iva_porcentaje = 19.0
                        elif 4 <= iva_porcentaje <= 6:
                            iva_porcentaje = 5.0
                        elif iva_porcentaje < 1:
                            iva_porcentaje = 0.0
                        logger.debug(f"IVA calculado (estrategia 3): {iva_porcentaje}%")
            except Exception as e:
                logger.debug(f"Error calculando IVA: {e}")
        
        # Calcular valor del IVA si tenemos porcentaje y precio
        if iva_porcentaje > 0 and precio_unitario and cantidad:
            subtotal = precio_unitario * cantidad
            iva_valor = subtotal * (iva_porcentaje / 100)
        
        return round(iva_porcentaje, 2), round(iva_valor, 2)
    
    @staticmethod
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
            r'Detalles de Productos([\s\S]+?)(?:Notas Finales|Datos Totales|Hoja \d+ de \d+)',
            r'DETALLE DE PRODUCTOS([\s\S]+?)(?:Notas Finales|Datos Totales)',
            r'Descripción\s+U/M\s+Cantidad([\s\S]+?)(?:Notas Finales|Datos Totales)',
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
                logger.info("Fin de productos detectado")
                break
            
            # Saltar encabezados de tabla
            if any(header in line for header in ['IMPUESTOS', 'Precio unitario', 'Descuento detalle', 'Nro. Código Descripción']):
                i += 1
                continue
            
            # FORMATO 1A: Con código largo (10-13 dígitos) Y descripción
            match1a = re.match(
                r'^(\d{1,3})\s+(\d{10,13})\s+(.+?)\s+(NIU|PK|BX|UND|UN|EA|PC)\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
                line
            )
            
            # FORMATO 1B: Con código largo (10-13 dígitos) SIN descripción
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
                    
                    # Extraer valores monetarios de la línea
                    valores = re.findall(r'\$\s*([0-9.,]+)', line)
                    total_item = precio_unitario * cantidad
                    if valores:
                        try:
                            total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                        except:
                            pass
                    
                    # Extraer IVA usando función mejorada
                    next_line = lines[i+1] if i + 1 < len(lines) else None
                    iva_porcentaje, iva_valor = PDFParserService._extract_iva_producto(
                        line, next_line, precio_unitario, total_item, cantidad
                    )
                    
                    productos.append({
                        'codigo_producto': codigo,
                        'descripcion': descripcion[:250],
                        'cantidad': cantidad,
                        'unidad_medida': unidad,
                        'precio_unitario': precio_unitario,
                        'iva_porcentaje': iva_porcentaje,
                        'iva_valor': iva_valor,
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
                        if prev_line and not re.match(r'^\d+\s', prev_line):
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                                descripcion = prev_line
                    
                    if i + 1 < len(lines):
                        next_line = lines[i+1].strip()
                        if next_line and not re.match(r'^\d+\s', next_line):
                            if not any(h in next_line for h in ['Hoja ', 'IMPUESTOS', 'Precio']):
                                descripcion = f"{descripcion} {next_line}".strip()
                    
                    # Extraer valores monetarios de la línea
                    valores = re.findall(r'\$\s*([0-9.,]+)', line)
                    total_item = precio_unitario * cantidad
                    if valores:
                        try:
                            total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                        except:
                            pass
                    
                    # Extraer IVA usando función mejorada
                    next_line_for_iva = lines[i+1] if i + 1 < len(lines) else None
                    iva_porcentaje, iva_valor = PDFParserService._extract_iva_producto(
                        line, next_line_for_iva, precio_unitario, total_item, cantidad
                    )
                    
                    productos.append({
                        'codigo_producto': codigo,
                        'descripcion': descripcion[:250],
                        'cantidad': cantidad,
                        'unidad_medida': unidad,
                        'precio_unitario': precio_unitario,
                        'iva_porcentaje': iva_porcentaje,
                        'iva_valor': iva_valor,
                        'total_item': total_item,
                    })
                    
                    logger.info(f"Producto {nro}: {codigo} - {descripcion[:30]}...")
                    i += 1
                    continue
                    
                except Exception as e:
                    logger.warning(f"Error FORMATO 1B: {e}")
            
            # FORMATO 2A: Con código corto (3-9 dígitos) Y descripción
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
                    
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        if prev_line and not re.match(r'^\d+\s', prev_line):
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                                descripcion = f"{prev_line} {descripcion}".strip()
                    
                    if i + 1 < len(lines):
                        next_line = lines[i+1].strip()
                        if next_line and not re.match(r'^\d+\s', next_line):
                            if not any(h in next_line for h in ['Hoja ', 'IMPUESTOS', 'Precio']):
                                descripcion = f"{descripcion} {next_line}".strip()
                    
                    # Extraer valores monetarios de la línea
                    valores = re.findall(r'\$\s*([0-9.,]+)', line)
                    total_item = precio_unitario * cantidad
                    if valores:
                        try:
                            total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                        except:
                            pass
                    
                    # Extraer IVA usando función mejorada
                    next_line_for_iva = lines[i+1] if i + 1 < len(lines) else None
                    iva_porcentaje, iva_valor = PDFParserService._extract_iva_producto(
                        line, next_line_for_iva, precio_unitario, total_item, cantidad
                    )
                    
                    productos.append({
                        'codigo_producto': codigo,
                        'descripcion': descripcion[:250],
                        'cantidad': cantidad,
                        'unidad_medida': unidad,
                        'precio_unitario': precio_unitario,
                        'iva_porcentaje': iva_porcentaje,
                        'iva_valor': iva_valor,
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
                        if prev_line and not re.match(r'^\d+\s', prev_line):
                            if not any(h in prev_line for h in ['IMPUESTOS', 'Precio', 'Descuento', 'Código']):
                                descripcion = prev_line
                    
                    # Extraer valores monetarios de la línea
                    valores = re.findall(r'\$\s*([0-9.,]+)', line)
                    total_item = precio_unitario * cantidad
                    if valores:
                        try:
                            total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                        except:
                            pass
                    
                    # Extraer IVA usando función mejorada
                    next_line = lines[i+1] if i + 1 < len(lines) else None
                    iva_porcentaje, iva_valor = PDFParserService._extract_iva_producto(
                        line, next_line, precio_unitario, total_item, cantidad
                    )
                    
                    productos.append({
                        'codigo_producto': codigo,
                        'descripcion': descripcion[:250],
                        'cantidad': cantidad,
                        'unidad_medida': unidad,
                        'precio_unitario': precio_unitario,
                        'iva_porcentaje': iva_porcentaje,
                        'iva_valor': iva_valor,
                        'total_item': total_item,
                    })
                    
                    logger.info(f"Producto {nro}: {codigo} - {descripcion[:30]}...")
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
                    
                    # Extraer valores monetarios de la línea
                    valores = re.findall(r'\$\s*([0-9.,]+)', line)
                    total_item = precio_unitario * cantidad
                    if valores:
                        try:
                            total_item = float(valores[-1].replace('.', '').replace(',', '.'))
                        except:
                            pass
                    
                    # Extraer IVA usando función mejorada
                    next_line = lines[i+1] if i + 1 < len(lines) else None
                    iva_porcentaje, iva_valor = PDFParserService._extract_iva_producto(
                        line, next_line, precio_unitario, total_item, cantidad
                    )
                    
                    productos.append({
                        'codigo_producto': codigo,
                        'descripcion': descripcion[:250],
                        'cantidad': cantidad,
                        'unidad_medida': unidad,
                        'precio_unitario': precio_unitario,
                        'iva_porcentaje': iva_porcentaje,
                        'iva_valor': iva_valor,
                        'total_item': total_item,
                    })
                    
                    logger.info(f"Producto {nro}: {codigo} - {descripcion[:30]}...")
                    i += 1
                    continue
                    
                except Exception as e:
                    logger.warning(f"Error FORMATO 3: {e}")
            
            i += 1
        
        logger.info(f"Total productos extraídos: {len(productos)}")
        return productos
    
    @staticmethod
    def validate_cufe_format(cufe: Optional[str]) -> bool:
        """
        Valida que un CUFE sea un código válido (96 caracteres hexadecimales)
        Soporta CUFE de 96 caracteres y CUDE de variable longitud
        """
        if not cufe:
            return False

        cleaned = re.sub(r'[^0-9a-fA-F]', '', cufe)

        if len(cleaned) == 96:
            return True

        if len(cleaned) >= 20 and len(cleaned) <= 50:
            logger.info(f"ℹ️ Código {len(cleaned)} caracteres (posible CUDE corto): {cleaned}")
            return True

        return False

    @staticmethod
    def extract_cufe_from_filename(filename: str) -> Optional[str]:
        """
        Extrae CUFE de nombres de archivo no-estándar

        Maneja patrones:
        1. f-[CUFE96]_timestamp.pdf → extrae CUFE96 después del "f-"
        2. [CUFE96]_timestamp.pdf → estándar
        3. [CUFE96]_(1).pdf / [CUFE96]_(2).pdf → duplicados
        4. [CUFE_SHORT].pdf → CUDE corto (variable longitud)
        5. FV[NUMERIC].pdf / AD[NUMERIC].pdf → códigos específicos
        """
        if not filename:
            return None

        base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        base_name = base_name.strip()

        logger.info(f"🔍 Extrayendo CUFE de filename: {filename}")

        CUFE_STANDARD_PATTERN = r'[0-9a-fA-F]{96}'

        try:
            # Patrón 1: Prefijo "f-" seguido de CUFE96 (ej: f-a1b2c3...xyz_20250101120000.pdf)
            if base_name.startswith('f-') or base_name.startswith('F-'):
                remainder = base_name[2:]
                matches = re.findall(CUFE_STANDARD_PATTERN, remainder, re.IGNORECASE)
                if matches:
                    cufe = matches[0].lower()
                    logger.info(f"✅ CUFE extraído de prefijo 'f-': {cufe[:20]}...{cufe[-20:]}")
                    return cufe

            # Patrón 2: CUFE estándar directo (sin prefijo)
            matches = re.findall(CUFE_STANDARD_PATTERN, base_name, re.IGNORECASE)
            if matches:
                cufe = matches[0].lower()
                logger.info(f"✅ CUFE extraído (estándar): {cufe[:20]}...{cufe[-20:]}")
                return cufe

            # Patrón 3: Eliminar duplicados (1), (2) y reintentar
            cleaned_base = re.sub(r'\s*\(\d\)\s*$', '', base_name).strip()
            if cleaned_base != base_name:
                matches = re.findall(CUFE_STANDARD_PATTERN, cleaned_base, re.IGNORECASE)
                if matches:
                    cufe = matches[0].lower()
                    logger.info(f"✅ CUFE extraído (después de eliminar duplicado): {cufe[:20]}...{cufe[-20:]}")
                    return cufe

            # Patrón 4: CUDE corto (código numérico de 20-50 caracteres hex)
            shorter_matches = re.findall(r'[0-9a-fA-F]{20,}', base_name, re.IGNORECASE)
            if shorter_matches:
                # Tomar el primero (más probable de ser el código)
                cude = shorter_matches[0].lower()
                if len(cude) <= 50:
                    logger.info(f"ℹ️ CUDE corto encontrado ({len(cude)} caracteres): {cude}")
                    return cude

            # Patrón 5: Códigos específicos (FV, AD, GRM, POS, etc.)
            specific_patterns = [
                (r'^(?:FV|fv)(\d+)', 'FV'),
                (r'^(?:AD|ad)(\d+)', 'AD'),
                (r'^(?:GRM|grm)(\d+)', 'GRM'),
                (r'^(?:POS|pos)(\d+)', 'POS'),
                (r'^(?:FE|fe)(\d+)', 'FE'),
            ]
            for pattern, code_type in specific_patterns:
                match = re.search(pattern, base_name)
                if match:
                    specific_code = match.group(0)
                    logger.info(f"ℹ️ Código específico {code_type} encontrado: {specific_code}")
                    return specific_code

            logger.warning(f"⚠️ No se encontró CUFE válido en filename: {filename}")
            return None

        except Exception as e:
            logger.error(f"❌ Error extrayendo CUFE de filename: {e}")
            return None

    @staticmethod
    def extract_cufe_combined(filename: str, pdf_text: str) -> tuple[Optional[str], str]:
        """
        Estrategia combinada: intenta extraer CUFE primero del nombre de archivo,
        luego del contenido del PDF.

        Returns:
            tuple: (cufe_extraído, estrategia_usada)
            estrategia_usada puede ser: 'filename', 'pdf_text', o 'manual_required'
        """
        # Intento 1: Extraer del nombre de archivo
        cufe_from_filename = PDFParserService.extract_cufe_from_filename(filename)
        if cufe_from_filename and PDFParserService.validate_cufe_format(cufe_from_filename):
            return cufe_from_filename, 'filename'

        # Intento 2: Extraer del texto del PDF
        cufe_from_pdf = PDFParserService.extract_cufe(pdf_text)
        if cufe_from_pdf and PDFParserService.validate_cufe_format(cufe_from_pdf):
            return cufe_from_pdf, 'pdf_text'

        # Fallback: Requiere entrada manual
        logger.warning(f"⚠️ CUFE no extraído automáticamente para: {filename}")
        return None, 'manual_required'

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
