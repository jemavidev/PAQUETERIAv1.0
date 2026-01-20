# ========================================
# PAQUETES EL CLUB - Extractor Mejorado de PDFs
# ========================================
"""
Extractor mejorado con scores de confianza y múltiples estrategias.
Retorna datos con nivel de confianza para cada campo extraído.
"""

import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum

import pdfplumber

logger = logging.getLogger(__name__)


class ExtractionSource(Enum):
    """Fuente de extracción del dato"""
    REGEX = "regex"
    POSITION = "position"
    PATTERN_LIBRARY = "pattern_library"
    MANUAL = "manual"
    UNKNOWN = "unknown"


@dataclass
class FieldExtraction:
    """Resultado de extracción de un campo con confianza"""
    value: Any
    confidence: float  # 0.0 - 1.0
    source: ExtractionSource
    alternatives: List[Any] = field(default_factory=list)
    raw_matches: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'confidence': self.confidence,
            'source': self.source.value,
            'alternatives': self.alternatives,
            'has_alternatives': len(self.alternatives) > 0
        }


@dataclass
class EnhancedInvoiceData:
    """Datos extraídos con información de confianza"""
    supplier_name: FieldExtraction
    supplier_nit: FieldExtraction
    invoice_number: FieldExtraction
    invoice_date: FieldExtraction
    total_amount: FieldExtraction
    cufe: FieldExtraction
    
    @property
    def overall_quality(self) -> float:
        """Calcula calidad general de la extracción"""
        confidences = [
            self.supplier_name.confidence,
            self.supplier_nit.confidence,
            self.invoice_number.confidence,
            self.invoice_date.confidence,
            self.total_amount.confidence,
            self.cufe.confidence,
        ]
        return sum(confidences) / len(confidences)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'supplier_name': self.supplier_name.to_dict(),
            'supplier_nit': self.supplier_nit.to_dict(),
            'invoice_number': self.invoice_number.to_dict(),
            'invoice_date': self.invoice_date.to_dict(),
            'total_amount': self.total_amount.to_dict(),
            'cufe': self.cufe.to_dict(),
            'overall_quality': self.overall_quality,
        }


class EnhancedPDFExtractor:
    """Extractor mejorado con múltiples estrategias y scores de confianza"""
    
    # Biblioteca de patrones por proveedor conocido
    PROVIDER_PATTERNS = {
        'EXITO': {
            'nit': '890900608',
            'name_patterns': [r'ALMACENES\s+[ÉE]XITO', r'EXITO\s+S\.?A\.?'],
            'invoice_pattern': r'FV\d{10,}',
        },
        'MAKRO': {
            'nit': '890903407',
            'name_patterns': [r'MAKRO', r'MAKRO\s+SUPERMAYORISTA'],
            'invoice_pattern': r'ad\d{20,}',
        },
        'COLANTA': {
            'nit': '890900200',
            'name_patterns': [r'COLANTA', r'COOPERATIVA\s+COLANTA'],
            'invoice_pattern': r'FC\d{6,}',
        },
    }
    
    def __init__(self):
        self.cufe_pattern = re.compile(r'[a-fA-F0-9]{96}')
    
    def extract_from_pdf(self, pdf_path: str) -> EnhancedInvoiceData:
        """
        Extrae datos del PDF con scores de confianza.
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                # Extraer texto de primeras 2 páginas
                for page in pdf.pages[:2]:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            lines = text.split('\n')
            
            # Extraer cada campo con su confianza
            supplier_name = self._extract_supplier_name(text, lines)
            supplier_nit = self._extract_nit(text, supplier_name)
            invoice_number = self._extract_invoice_number(text)
            invoice_date = self._extract_date(text)
            total_amount = self._extract_total(text)
            cufe = self._extract_cufe(text)
            
            return EnhancedInvoiceData(
                supplier_name=supplier_name,
                supplier_nit=supplier_nit,
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                total_amount=total_amount,
                cufe=cufe,
            )
            
        except Exception as e:
            logger.error(f"Error en extracción mejorada: {e}", exc_info=True)
            # Retornar datos vacíos con confianza 0
            return self._empty_extraction()

    
    def _extract_supplier_name(self, text: str, lines: List[str]) -> FieldExtraction:
        """Extrae nombre del proveedor con confianza"""
        candidates = []
        
        # Estrategia 1: Buscar en patrones conocidos
        for provider, patterns in self.PROVIDER_PATTERNS.items():
            for pattern in patterns['name_patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    candidates.append((provider, 0.95, ExtractionSource.PATTERN_LIBRARY))
                    break
        
        # Estrategia 2: Buscar con palabras clave
        name_patterns = [
            (r'(?:Razón\s*Social|Nombre\s*Comercial)[:\s]*([^\n]{5,100})', 0.90),
            (r'(?:Proveedor|Vendedor|Emisor)[:\s]*([^\n]{5,100})', 0.85),
        ]
        
        for pattern, confidence in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = self._clean_supplier_name(match.group(1))
                if name:
                    candidates.append((name, confidence, ExtractionSource.REGEX))
        
        # Estrategia 3: Buscar en primeras líneas
        for i, line in enumerate(lines[:15]):
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Saltar líneas con keywords comunes
            if any(kw in line.upper() for kw in ['FACTURA', 'INVOICE', 'FECHA', 'DATE', 'NIT', 'CUFE', 'TOTAL']):
                continue
            
            if 5 < len(line) < 100 and not re.match(r'^[\d\s\-\.]+$', line):
                name = self._clean_supplier_name(line)
                if name:
                    # Confianza basada en posición (más arriba = más confianza)
                    confidence = 0.70 - (i * 0.03)
                    candidates.append((name, max(confidence, 0.40), ExtractionSource.REGEX))
        
        # Seleccionar mejor candidato
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            best = candidates[0]
            alternatives = [c[0] for c in candidates[1:4] if c[0] != best[0]]
            
            return FieldExtraction(
                value=best[0],
                confidence=best[1],
                source=best[2],
                alternatives=alternatives
            )
        
        return FieldExtraction(None, 0.0, ExtractionSource.UNKNOWN, [])
    
    def _clean_supplier_name(self, name: str) -> Optional[str]:
        """Limpia y normaliza nombre de proveedor"""
        if not name:
            return None
        
        # Normalizar espacios
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Quitar NIT, FECHA si están juntos
        name = name.split('NIT')[0].strip()
        name = name.split('FECHA')[0].strip()
        name = name.split('Fecha')[0].strip()
        
        # Validar longitud
        if len(name) < 3 or len(name) > 200:
            return None
        
        return name.upper()
    
    def _extract_nit(self, text: str, supplier_name: FieldExtraction) -> FieldExtraction:
        """Extrae NIT con confianza"""
        candidates = []
        
        # Estrategia 1: Si conocemos el proveedor, usar NIT conocido
        if supplier_name.value and supplier_name.confidence > 0.80:
            for provider, patterns in self.PROVIDER_PATTERNS.items():
                if provider in supplier_name.value:
                    nit = patterns['nit']
                    candidates.append((nit, 0.98, ExtractionSource.PATTERN_LIBRARY))
                    break
        
        # Estrategia 2: Buscar con patrones
        nit_patterns = [
            (r'NIT[:\s]*(\d{3}\.?\d{3}\.?\d{3}[-\s]?\d)', 0.90),
            (r'N\.?I\.?T\.?[:\s]*(\d{9,12}[-\s]?\d?)', 0.85),
            (r'(?:^|\s)(\d{9,10})(?:\s|$)', 0.60),  # NIT sin prefijo (menos confianza)
        ]
        
        for pattern, confidence in nit_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                nit = re.sub(r'[^\d]', '', match.group(1))
                if 9 <= len(nit) <= 12:
                    nit = nit[:10]  # Max 10 dígitos
                    candidates.append((nit, confidence, ExtractionSource.REGEX))
        
        # Seleccionar mejor candidato
        if candidates:
            # Eliminar duplicados manteniendo el de mayor confianza
            unique_candidates = {}
            for nit, conf, source in candidates:
                if nit not in unique_candidates or conf > unique_candidates[nit][0]:
                    unique_candidates[nit] = (conf, source)
            
            # Ordenar por confianza
            sorted_candidates = sorted(
                [(nit, conf, source) for nit, (conf, source) in unique_candidates.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            best = sorted_candidates[0]
            alternatives = [c[0] for c in sorted_candidates[1:3] if c[0] != best[0]]
            
            return FieldExtraction(
                value=best[0],
                confidence=best[1],
                source=best[2],
                alternatives=alternatives
            )
        
        return FieldExtraction(None, 0.0, ExtractionSource.UNKNOWN, [])
    
    def _extract_invoice_number(self, text: str) -> FieldExtraction:
        """Extrae número de factura con confianza"""
        candidates = []
        
        invoice_patterns = [
            (r'Factura\s*(?:No\.?|Nro\.?|#|N°|Número)?\s*[:\s]*([A-Z0-9-]+)', 0.90),
            (r'(?:FV|FE|FA|FC)[:\s-]*(\d+)', 0.85),
            (r'Invoice\s*(?:No\.?|Number)?[:\s]*([A-Z0-9-]+)', 0.85),
            (r'Número\s*(?:de\s*)?Factura[:\s]*([A-Z0-9-]+)', 0.88),
            (r'(?:^|\s)(?:No\.?|Nro\.?|#)\s*([A-Z0-9-]{3,})', 0.70),
        ]
        
        for pattern, confidence in invoice_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                number = match.group(1).strip().upper()
                # Validar longitud
                if 2 <= len(number) <= 50:
                    candidates.append((number, confidence, ExtractionSource.REGEX))
        
        if candidates:
            # Eliminar duplicados
            unique = {}
            for num, conf, source in candidates:
                if num not in unique or conf > unique[num][0]:
                    unique[num] = (conf, source)
            
            sorted_candidates = sorted(
                [(num, conf, source) for num, (conf, source) in unique.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            best = sorted_candidates[0]
            alternatives = [c[0] for c in sorted_candidates[1:3] if c[0] != best[0]]
            
            return FieldExtraction(
                value=best[0],
                confidence=best[1],
                source=best[2],
                alternatives=alternatives
            )
        
        return FieldExtraction(None, 0.0, ExtractionSource.UNKNOWN, [])
    
    def _extract_date(self, text: str) -> FieldExtraction:
        """Extrae fecha con confianza"""
        candidates = []
        
        date_patterns = [
            (r'Fecha\s*(?:de\s*)?(?:Emisión|Expedición)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', 0.95),
            (r'Fecha[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})', 0.85),
            (r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})', 0.80),
            (r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})', 0.70),
            (r'Fecha[:\s]*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})', 0.90),
        ]
        
        for pattern, confidence in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(1)
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    candidates.append((parsed_date, confidence, ExtractionSource.REGEX))
        
        if candidates:
            # Eliminar duplicados
            unique = {}
            for date, conf, source in candidates:
                date_key = date.strftime('%Y-%m-%d')
                if date_key not in unique or conf > unique[date_key][1]:
                    unique[date_key] = (date, conf, source)
            
            sorted_candidates = sorted(
                [(date, conf, source) for date, conf, source in unique.values()],
                key=lambda x: x[1],
                reverse=True
            )
            
            best = sorted_candidates[0]
            alternatives = [c[0] for c in sorted_candidates[1:3] if c[0] != best[0]]
            
            return FieldExtraction(
                value=best[0],
                confidence=best[1],
                source=best[2],
                alternatives=alternatives
            )
        
        return FieldExtraction(None, 0.0, ExtractionSource.UNKNOWN, [])
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Intenta parsear una fecha en múltiples formatos"""
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d',
            '%d/%m/%y', '%d-%m-%y',
            '%d de %B de %Y', '%d de %b de %Y'
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                # Validar rango razonable
                if 2020 <= parsed.year <= 2030:
                    return parsed
            except:
                continue
        
        return None
    
    def _extract_total(self, text: str) -> FieldExtraction:
        """Extrae total con confianza"""
        candidates = []
        
        total_patterns = [
            (r'Total\s*(?:a\s*Pagar|Factura)[:\s]*\$?\s*([\d,\.]+)', 0.95),
            (r'Valor\s*Total[:\s]*\$?\s*([\d,\.]+)', 0.90),
            (r'Total[:\s]*\$?\s*([\d,\.]+)', 0.80),
            (r'TOTAL[:\s]*\$?\s*([\d,\.]+)', 0.85),
        ]
        
        for pattern, confidence in total_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    total_str = match.group(1).replace(',', '').replace('.', '')
                    total = int(total_str)
                    # Validar rango razonable
                    if 100 <= total <= 999999999:
                        candidates.append((total, confidence, ExtractionSource.REGEX))
                except:
                    continue
        
        if candidates:
            # Eliminar duplicados
            unique = {}
            for total, conf, source in candidates:
                if total not in unique or conf > unique[total][0]:
                    unique[total] = (conf, source)
            
            sorted_candidates = sorted(
                [(total, conf, source) for total, (conf, source) in unique.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            best = sorted_candidates[0]
            alternatives = [c[0] for c in sorted_candidates[1:3] if c[0] != best[0]]
            
            return FieldExtraction(
                value=best[0],
                confidence=best[1],
                source=best[2],
                alternatives=alternatives
            )
        
        return FieldExtraction(None, 0.0, ExtractionSource.UNKNOWN, [])
    
    def _extract_cufe(self, text: str) -> FieldExtraction:
        """Extrae CUFE con confianza"""
        matches = self.cufe_pattern.findall(text)
        
        if matches:
            # Validar cada match
            valid_cufes = []
            for match in matches:
                cufe = match.lower()
                if len(cufe) == 96:
                    valid_cufes.append(cufe)
            
            if valid_cufes:
                # El primer CUFE válido tiene alta confianza
                return FieldExtraction(
                    value=valid_cufes[0],
                    confidence=0.98,
                    source=ExtractionSource.REGEX,
                    alternatives=valid_cufes[1:3] if len(valid_cufes) > 1 else []
                )
        
        return FieldExtraction(None, 0.0, ExtractionSource.UNKNOWN, [])
    
    def _empty_extraction(self) -> EnhancedInvoiceData:
        """Retorna extracción vacía"""
        empty_field = FieldExtraction(None, 0.0, ExtractionSource.UNKNOWN, [])
        return EnhancedInvoiceData(
            supplier_name=empty_field,
            supplier_nit=empty_field,
            invoice_number=empty_field,
            invoice_date=empty_field,
            total_amount=empty_field,
            cufe=empty_field,
        )
