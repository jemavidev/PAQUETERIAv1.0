# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Utilidades de Teléfono
Normalización y validación de números telefónicos
Formato: Internacional con Colombia (+57) por defecto

@version 1.0.0
@date 2025-11-14
@author Equipo de Desarrollo
"""

import re
from typing import Optional


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    """
    Normaliza un número de teléfono a formato internacional
    
    Comportamiento:
    - Si empieza con +57 o +: mantiene el formato internacional
    - Si NO tiene código de país: agrega +57 (Colombia por defecto)
    - Elimina espacios, guiones, paréntesis
    - Resultado: +[código][número] (ej: +573001234567)
    
    Args:
        phone: Número de teléfono a normalizar
        
    Returns:
        Número normalizado en formato +[código][número] o None si es inválido
        
    Examples:
        >>> normalize_phone("3001234567")
        '+573001234567'
        >>> normalize_phone("+57 300 123 4567")
        '+573001234567'
        >>> normalize_phone("+1 202 555 0123")
        '+12025550123'
    """
    if not phone:
        return None
    
    # Convertir a string y limpiar
    cleaned = str(phone).strip()
    
    # Eliminar espacios, guiones, paréntesis
    cleaned = re.sub(r'[\s\-()]', '', cleaned)
    
    # Si ya tiene +, solo limpiar
    if cleaned.startswith('+'):
        return cleaned
    
    # Si NO tiene +, agregar código de Colombia (+57)
    # Eliminar cualquier + que no esté al inicio
    cleaned = cleaned.replace('+', '')
    
    # Si empieza con 57 (posible código sin +), verificar longitud
    if cleaned.startswith('57') and len(cleaned) >= 12:
        # Probablemente ya tiene código de país sin +
        return '+' + cleaned
    
    # Agregar +57 por defecto (Colombia)
    return '+57' + cleaned


def validate_phone(phone: Optional[str]) -> bool:
    """
    Valida si un número de teléfono es válido
    
    Reglas:
    - Debe tener entre 10 y 15 dígitos (sin contar el +)
    - Números colombianos móviles: 3XXXXXXXXX (10 dígitos)
    - Números colombianos fijos: 60XXXXXXXX (10 dígitos)
    - Números internacionales: debe empezar con + y tener código válido
    
    Args:
        phone: Número a validar
        
    Returns:
        True si es válido, False si no
        
    Examples:
        >>> validate_phone("+573001234567")
        True
        >>> validate_phone("3001234567")
        True
        >>> validate_phone("+12025550123")
        True
        >>> validate_phone("123")
        False
    """
    if not phone:
        return False
    
    normalized = normalize_phone(phone)
    if not normalized:
        return False
    
    # Debe empezar con +
    if not normalized.startswith('+'):
        return False
    
    # Extraer solo dígitos (sin el +)
    digits = normalized[1:]
    
    # Debe tener solo dígitos
    if not digits.isdigit():
        return False
    
    # Debe tener entre 10 y 15 dígitos
    if len(digits) < 10 or len(digits) > 15:
        return False
    
    # Validación específica para Colombia (+57)
    if normalized.startswith('+57'):
        colombian_number = digits[2:]  # Quitar "57"
        
        # Debe tener exactamente 10 dígitos después del +57
        if len(colombian_number) != 10:
            return False
        
        # Móvil: debe empezar con 3
        # Fijo: debe empezar con 6
        first_digit = colombian_number[0]
        if first_digit not in ['3', '6']:
            return False
    
    return True


def format_phone_display(phone: Optional[str]) -> str:
    """
    Formatea un número de teléfono para visualización
    Devuelve el formato normalizado sin espacios: +573001234567
    
    Args:
        phone: Número a formatear
        
    Returns:
        Número formateado o cadena vacía
        
    Examples:
        >>> format_phone_display("3001234567")
        '+573001234567'
        >>> format_phone_display("+57 300 123 4567")
        '+573001234567'
    """
    if not phone:
        return ''
    normalized = normalize_phone(phone)
    return normalized or ''


def format_phone_link(phone: Optional[str]) -> str:
    """
    Formatea un número de teléfono para enlaces tel: y WhatsApp
    Devuelve el número sin + para compatibilidad: 573001234567
    
    Args:
        phone: Número a formatear
        
    Returns:
        Número sin + para enlaces
        
    Examples:
        >>> format_phone_link("+573001234567")
        '573001234567'
        >>> format_phone_link("3001234567")
        '573001234567'
    """
    if not phone:
        return ''
    normalized = normalize_phone(phone)
    if not normalized:
        return ''
    # Quitar el + para enlaces
    return normalized.replace('+', '')


def clean_phone_for_comparison(phone: Optional[str]) -> str:
    """
    Limpia un número de teléfono para comparación
    Útil para buscar duplicados
    
    Args:
        phone: Número a limpiar
        
    Returns:
        Número limpio solo con dígitos
        
    Examples:
        >>> clean_phone_for_comparison("+57 300 123 4567")
        '573001234567'
    """
    if not phone:
        return ''
    # Quitar todo excepto dígitos
    return re.sub(r'\D', '', str(phone))


def is_colombian_mobile(phone: Optional[str]) -> bool:
    """
    Verifica si es un número móvil colombiano
    
    Args:
        phone: Número a verificar
        
    Returns:
        True si es móvil colombiano, False si no
        
    Examples:
        >>> is_colombian_mobile("+573001234567")
        True
        >>> is_colombian_mobile("+576012345678")
        False
    """
    if not phone:
        return False
    
    normalized = normalize_phone(phone)
    if not normalized or not normalized.startswith('+57'):
        return False
    
    digits = normalized[1:]  # Quitar +
    colombian_number = digits[2:]  # Quitar 57
    
    # Móvil: 10 dígitos empezando con 3
    return len(colombian_number) == 10 and colombian_number[0] == '3'


def is_colombian_landline(phone: Optional[str]) -> bool:
    """
    Verifica si es un número fijo colombiano
    
    Args:
        phone: Número a verificar
        
    Returns:
        True si es fijo colombiano, False si no
        
    Examples:
        >>> is_colombian_landline("+576012345678")
        True
        >>> is_colombian_landline("+573001234567")
        False
    """
    if not phone:
        return False
    
    normalized = normalize_phone(phone)
    if not normalized or not normalized.startswith('+57'):
        return False
    
    digits = normalized[1:]  # Quitar +
    colombian_number = digits[2:]  # Quitar 57
    
    # Fijo: 10 dígitos empezando con 6
    return len(colombian_number) == 10 and colombian_number[0] == '6'

