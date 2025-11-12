# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Generadores
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

import random
import string
from typing import Set

def generate_access_code(existing_codes: Set[str] = None) -> str:
    """
    Genera código de acceso único de 4 caracteres
    Excluye el número 0 y la letra O
    """
    if existing_codes is None:
        existing_codes = set()
    
    # Caracteres permitidos (sin 0 y O)
    allowed_chars = string.ascii_uppercase.replace('O', '') + string.digits.replace('0', '')
    
    while True:
        code = ''.join(random.choices(allowed_chars, k=4))
        if code not in existing_codes:
            return code

def generate_baroti(existing_barotis: Set[str] = None) -> str:
    """
    Genera posición Baroti única de 2 dígitos (00-99)
    """
    if existing_barotis is None:
        existing_barotis = set()
    
    while True:
        baroti = f"{random.randint(0, 99):02d}"
        if baroti not in existing_barotis:
            return baroti

def generate_tracking_number(prefix: str = "PK") -> str:
    """
    Genera número de guía único con prefijo
    """
    # Generar sufijo alfanumérico de 8 caracteres
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{suffix}"
