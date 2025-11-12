# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Calculadoras
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

def calculate_storage_fee(received_at: datetime, delivered_at: Optional[datetime] = None) -> Decimal:
    """
    Calcula costo de bodegaje basado en días transcurridos
    Aplica plazo de gracia de 24 horas sin cobro adicional
    """
    if delivered_at is None:
        delivered_at = datetime.utcnow()
    
    # Calcular diferencia en días
    time_diff = delivered_at - received_at
    days = time_diff.days
    
    # Aplicar plazo de gracia de 24 horas
    if days <= 1:
        return Decimal('0.00')
    
    # Calcular días de bodegaje (restar 1 día de gracia)
    storage_days = days - 1
    
    # Costo por día usando configuración
    from app.config import settings
    daily_rate = Decimal(str(settings.base_storage_rate))
    
    return Decimal(storage_days) * daily_rate

def calculate_total_amount(package_type: str, storage_fee: Decimal) -> Decimal:
    """
    Calcula monto total a pagar - CORREGIDO usando configuración
    """
    from app.config import settings
    
    # Tarifa base según tipo de paquete usando configuración
    if package_type == "extra_dimensioned":
        base_fee = Decimal(str(settings.base_delivery_rate_extra_dimensioned))
    else:  # normal
        base_fee = Decimal(str(settings.base_delivery_rate_normal))
    
    return base_fee + storage_fee

def calculate_days_in_storage(received_at: datetime, delivered_at: Optional[datetime] = None) -> int:
    """
    Calcula días en almacén
    """
    if delivered_at is None:
        delivered_at = datetime.utcnow()
    
    time_diff = delivered_at - received_at
    return time_diff.days
