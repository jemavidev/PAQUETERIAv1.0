# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Validadores
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

import re
from typing import Optional

def validate_phone(phone: str) -> bool:
    """
    Valida formato de teléfono colombiano o internacional
    Formatos válidos: +57 300 123 4567, +1 555 123 4567
    """
    # Patrón para teléfonos internacionales
    pattern = r'^\+\d{1,3}\s?\d{3,4}\s?\d{3,4}\s?\d{3,4}$'
    return bool(re.match(pattern, phone))

def validate_email(email: str) -> bool:
    """
    Valida formato de email estándar
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_tracking_number(tracking_number: str) -> bool:
    """
    Valida formato de número de guía
    Debe tener al menos 5 caracteres alfanuméricos
    """
    pattern = r'^[A-Za-z0-9]{5,}$'
    return bool(re.match(pattern, tracking_number))

def validate_access_code(access_code: str) -> bool:
    """
    Valida formato de código de acceso
    Debe ser exactamente 4 caracteres alfanuméricos (sin 0 y O)
    """
    pattern = r'^[A-NP-Z1-9]{4}$'
    return bool(re.match(pattern, access_code))

def validate_baroti(baroti: str) -> bool:
    """
    Valida formato de posición Baroti
    Debe ser un número de 2 dígitos (00-99)
    """
    pattern = r'^[0-9]{2}$'
    return bool(re.match(pattern, baroti))
