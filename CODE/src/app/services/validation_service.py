"""
Servicio de validación para detectar inconsistencias en datos extraídos de PDF
"""
from typing import Dict, List, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Detecta inconsistencias en campos extraídos de PDF
    Identifica campos que requieren revisión manual
    """
    
    # Campos críticos que deben validarse
    CRITICAL_FIELDS = {
        'dian_total_neto': 'Total a pagar',
        'dian_subtotal': 'Subtotal',
        'dian_total_iva': 'Total IVA',
        'fecha_emision': 'Fecha de emisión',
        'numero_factura': 'Número de factura',
    }
    
    @staticmethod
    def validate_invoice(invoice) -> Dict[str, any]:
        """
        Valida una factura y detecta inconsistencias
        
        Returns:
            {
                'has_warnings': bool,
                'warnings': [
                    {
                        'field': 'dian_total_neto',
                        'field_label': 'Total a pagar',
                        'severity': 'critical',
                        'message': 'Campo no extraído del PDF',
                        'current_value': None,
                        'suggestion': 'Verificar manualmente'
                    }
                ],
                'validation_score': 95  # Porcentaje de campos OK
            }
        """
        warnings = []
        total_fields = 0
        valid_fields = 0
        
        # Solo validar si es PDF (no XML)
        fuente = invoice.dian_datos_raw.get('fuente') if invoice.dian_datos_raw else None
        if fuente == 'XML':
            return {
                'has_warnings': False,
                'warnings': [],
                'validation_score': 100,
                'source': 'XML'
            }
        
        # VALIDACIÓN 1: Total a pagar
        total_fields += 1
        if invoice.dian_total_neto is None:
            warnings.append({
                'field': 'dian_total_neto',
                'field_label': 'Total a pagar',
                'severity': 'critical',
                'message': 'Total no extraído del PDF',
                'current_value': None,
                'suggestion': 'Ingresar total manualmente'
            })
        elif invoice.dian_total_neto <= 0:
            warnings.append({
                'field': 'dian_total_neto',
                'field_label': 'Total a pagar',
                'severity': 'critical',
                'message': 'Total inválido (≤ 0)',
                'current_value': float(invoice.dian_total_neto),
                'suggestion': 'Verificar y corregir'
            })
        else:
            valid_fields += 1
        
        # VALIDACIÓN 2: Subtotal
        total_fields += 1
        if invoice.dian_subtotal is None:
            warnings.append({
                'field': 'dian_subtotal',
                'field_label': 'Subtotal',
                'severity': 'high',
                'message': 'Subtotal no extraído',
                'current_value': None,
                'suggestion': 'Ingresar subtotal manualmente'
            })
        else:
            valid_fields += 1
        
        # VALIDACIÓN 3: IVA
        total_fields += 1
        if invoice.dian_total_iva is None:
            warnings.append({
                'field': 'dian_total_iva',
                'field_label': 'Total IVA',
                'severity': 'high',
                'message': 'IVA no extraído',
                'current_value': None,
                'suggestion': 'Ingresar IVA manualmente'
            })
        else:
            valid_fields += 1
        
        # VALIDACIÓN 4: Consistencia de totales
        if invoice.dian_total_neto and invoice.dian_subtotal and invoice.dian_total_iva:
            total_calculado = invoice.dian_subtotal + invoice.dian_total_iva
            diferencia = abs(invoice.dian_total_neto - total_calculado)
            
            if diferencia > 1:  # Diferencia mayor a $1
                warnings.append({
                    'field': 'totales_inconsistentes',
                    'field_label': 'Totales',
                    'severity': 'high',
                    'message': f'Total no coincide: {invoice.dian_total_neto} ≠ {invoice.dian_subtotal} + {invoice.dian_total_iva}',
                    'current_value': {
                        'total': float(invoice.dian_total_neto),
                        'subtotal': float(invoice.dian_subtotal),
                        'iva': float(invoice.dian_total_iva),
                        'diferencia': float(diferencia)
                    },
                    'suggestion': 'Verificar cálculos'
                })
        
        # VALIDACIÓN 5: Fecha de emisión
        total_fields += 1
        if invoice.fecha_emision is None:
            warnings.append({
                'field': 'fecha_emision',
                'field_label': 'Fecha de emisión',
                'severity': 'critical',
                'message': 'Fecha no extraída',
                'current_value': None,
                'suggestion': 'Ingresar fecha manualmente'
            })
        else:
            # Validar que la fecha no sea futura ni muy antigua
            from datetime import datetime, timedelta
            now = datetime.now()
            fecha = invoice.fecha_emision
            
            if fecha > now:
                warnings.append({
                    'field': 'fecha_emision',
                    'field_label': 'Fecha de emisión',
                    'severity': 'high',
                    'message': 'Fecha en el futuro (posible error OCR)',
                    'current_value': fecha.isoformat(),
                    'suggestion': 'Verificar año'
                })
            elif fecha < now - timedelta(days=365*5):  # Más de 5 años
                warnings.append({
                    'field': 'fecha_emision',
                    'field_label': 'Fecha de emisión',
                    'severity': 'medium',
                    'message': 'Fecha muy antigua',
                    'current_value': fecha.isoformat(),
                    'suggestion': 'Verificar fecha'
                })
            else:
                valid_fields += 1
        
        # VALIDACIÓN 6: Número de factura
        total_fields += 1
        if not invoice.numero_factura:
            warnings.append({
                'field': 'numero_factura',
                'field_label': 'Número de factura',
                'severity': 'high',
                'message': 'Número no extraído',
                'current_value': None,
                'suggestion': 'Ingresar número manualmente'
            })
        else:
            valid_fields += 1
        
        # VALIDACIÓN 7: Productos
        productos_count = len(invoice.productos) if invoice.productos else 0
        if productos_count == 0:
            warnings.append({
                'field': 'productos',
                'field_label': 'Productos',
                'severity': 'critical',
                'message': 'No se extrajeron productos',
                'current_value': 0,
                'suggestion': 'Verificar archivo PDF'
            })
        
        # VALIDACIÓN 8: IVA en productos
        if invoice.productos:
            productos_sin_iva = 0
            for prod in invoice.productos:
                if prod.iva_porcentaje is None or prod.iva_porcentaje == 0:
                    # Verificar si debería tener IVA
                    if prod.total_item and prod.precio_unitario and prod.cantidad:
                        subtotal = prod.precio_unitario * prod.cantidad
                        if prod.total_item > subtotal * Decimal('1.01'):  # Más del 1% de diferencia
                            productos_sin_iva += 1
            
            if productos_sin_iva > 0:
                warnings.append({
                    'field': 'productos_iva',
                    'field_label': 'IVA en productos',
                    'severity': 'medium',
                    'message': f'{productos_sin_iva} producto(s) sin IVA extraído',
                    'current_value': productos_sin_iva,
                    'suggestion': 'Revisar IVA de productos'
                })
        
        # Calcular score de validación
        validation_score = int((valid_fields / total_fields) * 100) if total_fields > 0 else 0
        
        return {
            'has_warnings': len(warnings) > 0,
            'warnings': warnings,
            'validation_score': validation_score,
            'source': 'PDF',
            'total_fields_checked': total_fields,
            'valid_fields': valid_fields
        }
    
    @staticmethod
    def get_severity_color(severity: str) -> str:
        """Retorna color para el badge según severidad"""
        colors = {
            'critical': 'red',
            'high': 'orange',
            'medium': 'yellow',
            'low': 'blue'
        }
        return colors.get(severity, 'gray')
    
    @staticmethod
    def get_severity_icon(severity: str) -> str:
        """Retorna icono según severidad"""
        icons = {
            'critical': '⛔',
            'high': '⚠️',
            'medium': '⚡',
            'low': 'ℹ️'
        }
        return icons.get(severity, '•')
