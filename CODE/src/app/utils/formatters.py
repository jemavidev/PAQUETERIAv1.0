# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Formateadores
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from decimal import Decimal
from typing import Optional
from datetime import datetime

def format_phone(phone: str) -> str:
    """
    Formatea número de teléfono para visualización
    """
    # Remover espacios y caracteres especiales
    cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Si no tiene código de país, agregar +57
    if not cleaned.startswith('+'):
        cleaned = '+57' + cleaned
    
    # Formatear con espacios
    if cleaned.startswith('+57'):
        # Formato colombiano: +57 300 123 4567
        if len(cleaned) == 13:  # +57 + 10 dígitos
            return f"{cleaned[:3]} {cleaned[3:6]} {cleaned[6:9]} {cleaned[9:]}"
    else:
        # Formato internacional: +1 555 123 4567
        if len(cleaned) == 12:  # +1 + 10 dígitos
            return f"{cleaned[:2]} {cleaned[2:5]} {cleaned[5:8]} {cleaned[8:]}"
    
    return phone

def format_currency(amount: Decimal, currency: str = "COP") -> str:
    """
    Formatea monto como moneda
    """
    if currency == "COP":
        return f"${amount:,.0f} COP"
    else:
        return f"{currency} {amount:,.2f}"

def format_datetime(dt: Optional[datetime]) -> str:
    """
    Formatea datetime para visualización
    """
    if dt is None:
        return "No disponible"
    
    return dt.strftime("%d/%m/%Y %H:%M")

def format_status(status: str) -> str:
    """
    Formatea estado para visualización
    """
    status_map = {
        "announced": "Anunciado",
        "cancelled": "Cancelado", 
        "received": "Recibido",
        "delivered": "Entregado"
    }
    
    return status_map.get(status, status.title())
