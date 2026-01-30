# ========================================
# PAQUETES EL CLUB - Servicio de Facturas de Proveedores
# ========================================
"""
Servicio para gestionar el flujo completo de facturas de proveedores:
1. Subir PDF de proveedor
2. Extraer CUFE (del nombre o contenido)
3. Generar link DIAN para descarga
4. Procesar PDF de DIAN e importar
"""

import os
import re
import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.invoice import SupplierInvoice, SupplierInvoiceStatus, Invoice
from app.services.pdf_extractor_service import PDFExtractorService
from app.services.enhanced_pdf_extractor import EnhancedPDFExtractor

logger = logging.getLogger(__name__)


class SupplierInvoiceService:
    """Servicio para gestión de facturas de proveedores"""
    
    # Patrón para detectar CUFE (96 caracteres hexadecimales)
    CUFE_PATTERN = re.compile(r'[a-fA-F0-9]{96}')
    
    # Patrón para extraer CUFE del nombre de archivo
    # Formatos: f-{cufe}_{fecha}.pdf o {cufe}_{fecha}.pdf
    FILENAME_CUFE_PATTERN = re.compile(r'^f?-?([a-fA-F0-9]{96})(?:_\d+)?\.pdf$', re.IGNORECASE)
    
    def __init__(self, db: Session):
        self.db = db
        self.extractor = PDFExtractorService()
        self.enhanced_extractor = EnhancedPDFExtractor()
    
    @staticmethod
    def calculate_file_hash(content: bytes) -> str:
        """Calcula hash SHA256 del archivo"""
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def validate_cufe(cufe: str) -> Tuple[bool, str]:
        """
        Valida formato de CUFE.
        Returns: (is_valid, cleaned_cufe_or_error)
        """
        if not cufe:
            return False, "CUFE vacío"
        
        # Limpiar caracteres no hexadecimales
        clean = re.sub(r'[^a-fA-F0-9]', '', cufe).lower()
        
        if len(clean) != 96:
            return False, f"CUFE debe tener 96 caracteres (tiene {len(clean)})"
        
        return True, clean
    
    def extract_cufe_from_filename(self, filename: str) -> Optional[str]:
        """Extrae CUFE del nombre del archivo si existe"""
        match = self.FILENAME_CUFE_PATTERN.match(filename)
        if match:
            cufe = match.group(1).lower()
            is_valid, result = self.validate_cufe(cufe)
            if is_valid:
                return result
        return None
    
    def extract_cufe_from_content(self, pdf_path: str) -> Optional[str]:
        """Extrae CUFE del contenido del PDF usando pdfplumber"""
        try:
            import pdfplumber
            
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Buscar patrón CUFE en el texto
            matches = self.CUFE_PATTERN.findall(text)
            
            if matches:
                # Validar cada match y retornar el primero válido
                for match in matches:
                    is_valid, result = self.validate_cufe(match)
                    if is_valid:
                        return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo CUFE del contenido: {e}")
            return None

    def extract_basic_info_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrae información básica del PDF: proveedor, fecha, NIT
        MEJORADO: Extracción más robusta y precisa
        """
        try:
            import pdfplumber
            
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                # Solo primeras 2 páginas
                for page_num, page in enumerate(pdf.pages[:2]):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            info = {
                'supplier_name': None,
                'supplier_nit': None,
                'invoice_number': None,
                'invoice_date': None,
                'total_amount': None,
            }
            
            # ===== EXTRAER NOMBRE DEL PROVEEDOR =====
            # Buscar en las primeras líneas (generalmente el proveedor está arriba)
            lines = text.split('\n')
            
            # Patrones para identificar el nombre del proveedor
            supplier_patterns = [
                r'(?:Razón\s*Social|Nombre\s*Comercial|Empresa)[:\s]*([^\n]+)',
                r'(?:Proveedor|Vendedor|Emisor)[:\s]*([^\n]+)',
            ]
            
            for pattern in supplier_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # Limpiar el nombre
                    name = re.sub(r'\s+', ' ', name)  # Normalizar espacios
                    name = name.split('NIT')[0].strip()  # Quitar NIT si está junto
                    name = name.split('FECHA')[0].strip()  # Quitar FECHA si está junto
                    if len(name) > 3 and len(name) < 200:
                        info['supplier_name'] = name.upper()
                        break
            
            # Si no se encontró con patrones, buscar en las primeras 10 líneas
            # El proveedor suele estar en las primeras líneas, antes del NIT
            if not info['supplier_name']:
                for i, line in enumerate(lines[:15]):
                    line = line.strip()
                    # Saltar líneas vacías, muy cortas o que parecen títulos
                    if not line or len(line) < 5:
                        continue
                    if any(keyword in line.upper() for keyword in ['FACTURA', 'INVOICE', 'FECHA', 'DATE', 'NIT', 'CUFE', 'TOTAL']):
                        continue
                    # Si la línea tiene entre 5 y 100 caracteres y parece un nombre de empresa
                    if 5 < len(line) < 100:
                        # Verificar que no sea un número o código
                        if not re.match(r'^[\d\s\-\.]+$', line):
                            # Limpiar
                            name = re.sub(r'\s+', ' ', line)
                            name = name.split('NIT')[0].strip()
                            name = name.split('FECHA')[0].strip()
                            if len(name) > 3:
                                info['supplier_name'] = name.upper()
                                break
            
            # ===== EXTRAER NIT =====
            nit_patterns = [
                r'NIT[:\s]*(\d{3}\.?\d{3}\.?\d{3}[-\s]?\d)',
                r'N\.?I\.?T\.?[:\s]*(\d{9,12}[-\s]?\d?)',
                r'(?:^|\s)(\d{9,10})(?:\s|$)',  # NIT sin prefijo
            ]
            for pattern in nit_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    nit = re.sub(r'[^\d]', '', match.group(1))
                    if 9 <= len(nit) <= 12:
                        info['supplier_nit'] = nit[:10]  # Max 10 dígitos
                        break
            
            # ===== EXTRAER FECHA =====
            date_patterns = [
                r'Fecha\s*(?:de\s*)?(?:Emisión|Expedición)?[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Fecha[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
                r'Fecha[:\s]*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        date_str = match.group(1)
                        # Intentar parsear diferentes formatos
                        formats = [
                            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d', 
                            '%d/%m/%y', '%d-%m-%y',
                            '%d de %B de %Y', '%d de %b de %Y'
                        ]
                        for fmt in formats:
                            try:
                                parsed_date = datetime.strptime(date_str, fmt)
                                # Validar que la fecha sea razonable (no muy antigua ni futura)
                                if 2020 <= parsed_date.year <= 2030:
                                    info['invoice_date'] = parsed_date
                                    break
                            except:
                                continue
                        if info['invoice_date']:
                            break
                    except:
                        continue
            
            # ===== EXTRAER NÚMERO DE FACTURA =====
            invoice_patterns = [
                r'Factura\s*(?:No\.?|Nro\.?|#|N°|Número)?\s*[:\s]*([A-Z0-9-]+)',
                r'(?:FV|FE|FA|FC)[:\s-]*(\d+)',
                r'(?:^|\s)(?:No\.?|Nro\.?|#)\s*([A-Z0-9-]+)',
                r'Número\s*(?:de\s*)?Factura[:\s]*([A-Z0-9-]+)',
                r'Invoice\s*(?:No\.?|Number)?[:\s]*([A-Z0-9-]+)',
            ]
            for pattern in invoice_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    number = match.group(1).strip()
                    # Validar que no sea muy largo ni muy corto
                    if 2 <= len(number) <= 50:
                        info['invoice_number'] = number.upper()
                        break
            
            # ===== EXTRAER TOTAL =====
            total_patterns = [
                r'Total\s*(?:a\s*Pagar|Factura)?[:\s]*\$?\s*([\d,\.]+)',
                r'Valor\s*Total[:\s]*\$?\s*([\d,\.]+)',
                r'Total[:\s]*\$?\s*([\d,\.]+)',
            ]
            for pattern in total_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        total_str = match.group(1).replace(',', '').replace('.', '')
                        total = int(total_str)
                        if 100 <= total <= 999999999:  # Validar rango razonable
                            info['total_amount'] = total
                            break
                    except:
                        continue
            
            logger.info(f"Información extraída: Proveedor={info['supplier_name']}, Fecha={info['invoice_date']}, Número={info['invoice_number']}")
            return info
            
        except Exception as e:
            logger.error(f"Error extrayendo info básica: {e}", exc_info=True)
            return {}
    
    def check_duplicate_cufe(self, cufe: str) -> Optional[SupplierInvoice]:
        """Verifica si ya existe una factura con este CUFE"""
        return self.db.query(SupplierInvoice).filter(
            SupplierInvoice.cufe == cufe.lower()
        ).first()
    
    def check_duplicate_hash(self, file_hash: str) -> Optional[SupplierInvoice]:
        """Verifica si ya existe un archivo con este hash"""
        return self.db.query(SupplierInvoice).filter(
            SupplierInvoice.original_file_hash == file_hash
        ).first()

    def process_uploaded_file(
        self, 
        filename: str, 
        content: bytes, 
        pdf_path: str,
        user_id: int = None,
        use_enhanced: bool = True
    ) -> Tuple[SupplierInvoice, Dict[str, Any]]:
        """
        Procesa un archivo PDF subido con extracción mejorada.
        
        Args:
            filename: Nombre del archivo
            content: Contenido binario del PDF
            pdf_path: Ruta temporal del PDF
            user_id: ID del usuario que sube
            use_enhanced: Si True, usa extractor mejorado con confianza
        
        Returns:
            Tuple de (SupplierInvoice, info_dict)
        """
        result_info = {
            'cufe_found': False,
            'cufe_source': None,
            'is_duplicate': False,
            'duplicate_id': None,
            'warnings': [],
            'extraction_quality': 0.0,
            'field_confidences': {},
        }
        
        # Calcular hash
        file_hash = self.calculate_file_hash(content)
        
        # Verificar duplicado por hash
        existing = self.check_duplicate_hash(file_hash)
        if existing:
            result_info['is_duplicate'] = True
            result_info['duplicate_id'] = existing.id
            result_info['warnings'].append(f"Archivo ya existe (ID: {existing.id})")
            return existing, result_info
        
        # Intentar extraer CUFE del nombre del archivo
        cufe = self.extract_cufe_from_filename(filename)
        cufe_source = 'filename' if cufe else None
        
        # Si no está en el nombre, buscar en el contenido
        if not cufe:
            cufe = self.extract_cufe_from_content(pdf_path)
            cufe_source = 'content' if cufe else None
        
        # Verificar duplicado por CUFE
        if cufe:
            existing_cufe = self.check_duplicate_cufe(cufe)
            if existing_cufe:
                result_info['is_duplicate'] = True
                result_info['duplicate_id'] = existing_cufe.id
                result_info['warnings'].append(f"CUFE ya existe (ID: {existing_cufe.id})")
        
        result_info['cufe_found'] = cufe is not None
        result_info['cufe_source'] = cufe_source
        
        # Extraer información con extractor mejorado
        if use_enhanced:
            try:
                enhanced_data = self.enhanced_extractor.extract_from_pdf(pdf_path)
                
                # Usar datos extraídos con confianza
                supplier_name = enhanced_data.supplier_name.value
                supplier_nit = enhanced_data.supplier_nit.value
                invoice_number = enhanced_data.invoice_number.value
                invoice_date = enhanced_data.invoice_date.value
                total_amount = enhanced_data.total_amount.value
                
                # Si no se extrajo CUFE antes, usar el del extractor mejorado
                if not cufe and enhanced_data.cufe.value:
                    cufe = enhanced_data.cufe.value
                    cufe_source = 'enhanced_extractor'
                    result_info['cufe_found'] = True
                    result_info['cufe_source'] = cufe_source
                
                # Guardar calidad de extracción
                extraction_quality = enhanced_data.overall_quality
                result_info['extraction_quality'] = extraction_quality
                result_info['field_confidences'] = {
                    'supplier_name': enhanced_data.supplier_name.confidence,
                    'supplier_nit': enhanced_data.supplier_nit.confidence,
                    'invoice_number': enhanced_data.invoice_number.confidence,
                    'invoice_date': enhanced_data.invoice_date.confidence,
                    'total_amount': enhanced_data.total_amount.confidence,
                    'cufe': enhanced_data.cufe.confidence,
                }
                
                # Agregar warnings para campos con baja confianza
                if enhanced_data.supplier_name.confidence < 0.5:
                    result_info['warnings'].append("Proveedor: Baja confianza en extracción")
                if enhanced_data.invoice_date.confidence < 0.5:
                    result_info['warnings'].append("Fecha: Baja confianza en extracción")
                if enhanced_data.invoice_number.confidence < 0.5:
                    result_info['warnings'].append("Número: Baja confianza en extracción")
                
            except Exception as e:
                logger.error(f"Error en extractor mejorado, usando básico: {e}")
                # Fallback a extractor básico
                basic_info = self.extract_basic_info_from_pdf(pdf_path)
                supplier_name = basic_info.get('supplier_name')
                supplier_nit = basic_info.get('supplier_nit')
                invoice_number = basic_info.get('invoice_number')
                invoice_date = basic_info.get('invoice_date')
                total_amount = basic_info.get('total_amount')
                extraction_quality = 0.5  # Calidad media para extractor básico
        else:
            # Usar extractor básico
            basic_info = self.extract_basic_info_from_pdf(pdf_path)
            supplier_name = basic_info.get('supplier_name')
            supplier_nit = basic_info.get('supplier_nit')
            invoice_number = basic_info.get('invoice_number')
            invoice_date = basic_info.get('invoice_date')
            total_amount = basic_info.get('total_amount')
            extraction_quality = 0.5
        
        # Determinar estado inicial
        if cufe:
            status = SupplierInvoiceStatus.CUFE_EXTRACTED
        else:
            status = SupplierInvoiceStatus.NO_CUFE
        
        # Crear registro
        supplier_invoice = SupplierInvoice(
            original_filename=filename,
            original_file_hash=file_hash,
            supplier_name=supplier_name,
            supplier_nit=supplier_nit,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            total_amount=total_amount,
            cufe=cufe,
            cufe_source=cufe_source,
            status=status,
            extraction_quality=extraction_quality,
            uploaded_by=user_id,
        )
        
        self.db.add(supplier_invoice)
        self.db.commit()
        self.db.refresh(supplier_invoice)
        
        return supplier_invoice, result_info
    
    def get_all(
        self, 
        status: SupplierInvoiceStatus = None,
        page: int = 1,
        per_page: int = 50
    ) -> Tuple[List[SupplierInvoice], int]:
        """Obtiene todas las facturas de proveedores con paginación"""
        query = self.db.query(SupplierInvoice)
        
        if status:
            query = query.filter(SupplierInvoice.status == status)
        
        total = query.count()
        
        # Ordenar por fecha de factura (descendente), luego por fecha de subida
        # Las facturas sin fecha van al final
        invoices = query.order_by(
            desc(SupplierInvoice.invoice_date.is_(None)),
            desc(SupplierInvoice.invoice_date),
            desc(SupplierInvoice.uploaded_at)
        )\
            .offset((page - 1) * per_page)\
            .limit(per_page)\
            .all()
        
        return invoices, total
    
    def get_by_id(self, invoice_id: int) -> Optional[SupplierInvoice]:
        """Obtiene una factura por ID"""
        return self.db.query(SupplierInvoice).filter(
            SupplierInvoice.id == invoice_id
        ).first()
    
    def get_pending_cufe_extraction(self) -> List[SupplierInvoice]:
        """Obtiene facturas con CUFE extraído pendientes de procesar"""
        return self.db.query(SupplierInvoice).filter(
            SupplierInvoice.status == SupplierInvoiceStatus.CUFE_EXTRACTED
        ).order_by(SupplierInvoice.uploaded_at).all()
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de facturas de proveedores"""
        # Primero sincronizar estados con facturas ya procesadas
        self.sync_processed_status()
        
        stats = {
            'total': 0,
            'pending': 0,
            'no_cufe': 0,
            'cufe_extracted': 0,
            'dian_downloaded': 0,
            'processed': 0,
            'error': 0,
            'duplicate': 0,
        }
        
        results = self.db.query(
            SupplierInvoice.status,
            func.count(SupplierInvoice.id)
        ).group_by(SupplierInvoice.status).all()
        
        for status, count in results:
            stats['total'] += count
            if status and hasattr(status, 'value'):
                stats[status.value] = count
        
        return stats
    
    def sync_processed_status(self) -> int:
        """
        Sincroniza el estado de supplier_invoices con facturas ya procesadas.
        Busca CUFEs que existen en la tabla invoices y actualiza el estado.
        """
        # Obtener supplier_invoices con CUFE que no están marcadas como procesadas
        pending = self.db.query(SupplierInvoice).filter(
            SupplierInvoice.cufe.isnot(None),
            SupplierInvoice.status.notin_([
                SupplierInvoiceStatus.PROCESSED,
                SupplierInvoiceStatus.ERROR
            ])
        ).all()
        
        updated = 0
        for si in pending:
            # Buscar si el CUFE existe en invoices
            invoice = self.db.query(Invoice).filter(
                Invoice.cufe_cude == si.cufe,
                Invoice.is_active == True
            ).first()
            
            if invoice:
                si.status = SupplierInvoiceStatus.PROCESSED
                si.processed_invoice_id = invoice.id
                if not si.processed_at:
                    si.processed_at = datetime.now()
                updated += 1
        
        if updated > 0:
            self.db.commit()
            logger.info(f"Sincronizadas {updated} facturas de proveedor con estado procesado")
        
        return updated

    def update_status(
        self, 
        invoice_id: int, 
        status: SupplierInvoiceStatus,
        message: str = None,
        **kwargs
    ) -> Optional[SupplierInvoice]:
        """Actualiza el estado de una factura"""
        invoice = self.get_by_id(invoice_id)
        if not invoice:
            return None
        
        invoice.status = status
        if message:
            invoice.status_message = message
        
        for key, value in kwargs.items():
            if hasattr(invoice, key):
                setattr(invoice, key, value)
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    def update_cufe(
        self, 
        invoice_id: int, 
        cufe: str,
        source: str = 'manual'
    ) -> Tuple[bool, str]:
        """Actualiza el CUFE de una factura manualmente"""
        is_valid, result = self.validate_cufe(cufe)
        if not is_valid:
            return False, result
        
        # Verificar duplicado
        existing = self.check_duplicate_cufe(result)
        if existing and existing.id != invoice_id:
            return False, f"CUFE ya existe en factura ID {existing.id}"
        
        invoice = self.get_by_id(invoice_id)
        if not invoice:
            return False, "Factura no encontrada"
        
        invoice.cufe = result
        invoice.cufe_source = source
        invoice.status = SupplierInvoiceStatus.CUFE_EXTRACTED
        invoice.status_message = None
        
        self.db.commit()
        return True, "CUFE actualizado correctamente"
    
    def mark_dian_downloaded(
        self, 
        invoice_id: int,
        dian_file_hash: str = None
    ) -> Optional[SupplierInvoice]:
        """Marca una factura como descargada de DIAN"""
        return self.update_status(
            invoice_id,
            SupplierInvoiceStatus.DIAN_DOWNLOADED,
            dian_file_hash=dian_file_hash,
            dian_downloaded_at=datetime.now()
        )
    
    def mark_processed(
        self, 
        invoice_id: int,
        processed_invoice_id: int
    ) -> Optional[SupplierInvoice]:
        """Marca una factura como procesada"""
        return self.update_status(
            invoice_id,
            SupplierInvoiceStatus.PROCESSED,
            processed_invoice_id=processed_invoice_id,
            processed_at=datetime.now()
        )
    
    def delete(self, invoice_id: int) -> bool:
        """Elimina una factura de proveedor"""
        invoice = self.get_by_id(invoice_id)
        if not invoice:
            return False
        
        self.db.delete(invoice)
        self.db.commit()
        return True
    
    def get_cufes_for_dian(self) -> List[Dict[str, Any]]:
        """Obtiene lista de CUFEs pendientes para descargar de DIAN"""
        invoices = self.db.query(SupplierInvoice).filter(
            SupplierInvoice.status == SupplierInvoiceStatus.CUFE_EXTRACTED,
            SupplierInvoice.cufe.isnot(None)
        ).order_by(SupplierInvoice.uploaded_at).all()
        
        return [
            {
                'id': inv.id,
                'cufe': inv.cufe,
                'cufe_short': inv.cufe_short,
                'supplier_name': inv.supplier_name,
                'invoice_number': inv.invoice_number,
                'invoice_date': inv.invoice_date.isoformat() if inv.invoice_date else None,
                'dian_url': inv.dian_url,
            }
            for inv in invoices
        ]
