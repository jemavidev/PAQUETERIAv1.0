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
            
            # Buscar NIT (formato: NIT: 900.123.456-7 o similar)
            nit_patterns = [
                r'NIT[:\s]*(\d{3}\.?\d{3}\.?\d{3}[-\s]?\d)',
                r'N\.?I\.?T\.?[:\s]*(\d{9,12}[-\s]?\d?)',
            ]
            for pattern in nit_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    nit = re.sub(r'[^\d]', '', match.group(1))
                    if len(nit) >= 9:
                        info['supplier_nit'] = nit[:10]  # Max 10 dígitos
                        break
            
            # Buscar fecha (formatos comunes colombianos)
            date_patterns = [
                r'Fecha[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
                r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        date_str = match.group(1)
                        # Intentar parsear diferentes formatos
                        for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d', '%d/%m/%y']:
                            try:
                                info['invoice_date'] = datetime.strptime(date_str, fmt)
                                break
                            except:
                                continue
                        if info['invoice_date']:
                            break
                    except:
                        continue
            
            # Buscar número de factura
            invoice_patterns = [
                r'Factura\s*(?:No\.?|Nro\.?|#|N°)?\s*[:\s]*([A-Z0-9-]+)',
                r'(?:FV|FE|FA)[:\s-]*(\d+)',
                r'Número[:\s]*([A-Z0-9-]+)',
            ]
            for pattern in invoice_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    info['invoice_number'] = match.group(1).strip()[:50]
                    break
            
            # Buscar nombre del proveedor (líneas cerca del NIT)
            if info['supplier_nit']:
                # Buscar razón social cerca del NIT
                razon_patterns = [
                    r'Razón\s*Social[:\s]*([^\n]+)',
                    r'Nombre[:\s]*([^\n]+)',
                ]
                for pattern in razon_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        name = match.group(1).strip()[:255]
                        if len(name) > 3:
                            info['supplier_name'] = name.upper()
                            break
            
            return info
            
        except Exception as e:
            logger.error(f"Error extrayendo info básica: {e}")
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
        user_id: int = None
    ) -> Tuple[SupplierInvoice, Dict[str, Any]]:
        """
        Procesa un archivo PDF subido.
        
        Returns:
            Tuple de (SupplierInvoice, info_dict)
        """
        result_info = {
            'cufe_found': False,
            'cufe_source': None,
            'is_duplicate': False,
            'duplicate_id': None,
            'warnings': [],
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
        
        # Extraer información básica del PDF
        basic_info = self.extract_basic_info_from_pdf(pdf_path)
        
        # Determinar estado inicial
        if cufe:
            status = SupplierInvoiceStatus.CUFE_EXTRACTED
        else:
            status = SupplierInvoiceStatus.NO_CUFE
        
        # Crear registro
        supplier_invoice = SupplierInvoice(
            original_filename=filename,
            original_file_hash=file_hash,
            supplier_name=basic_info.get('supplier_name'),
            supplier_nit=basic_info.get('supplier_nit'),
            invoice_number=basic_info.get('invoice_number'),
            invoice_date=basic_info.get('invoice_date'),
            total_amount=basic_info.get('total_amount'),
            cufe=cufe,
            cufe_source=cufe_source,
            status=status,
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
        
        invoices = query.order_by(desc(SupplierInvoice.uploaded_at))\
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
