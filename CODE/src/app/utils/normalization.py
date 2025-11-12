# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Utilidades de Normalización de Datos
Objetivo: Alinear valores entre DB, backend y frontend usando nomenclatura unificada.
"""

from typing import Dict, Any, Optional


STATUS_MAP = {
    # Español oficial
    "ANUNCIADO": "ANUNCIADO",
    "RECIBIDO": "RECIBIDO",
    "ENTREGADO": "ENTREGADO",
    "CANCELADO": "CANCELADO",
    # Variantes comunes
    "announced": "ANUNCIADO",
    "received": "RECIBIDO",
    "delivered": "ENTREGADO",
    "cancelled": "CANCELADO",
    "cancelado": "CANCELADO",
}

TYPE_MAP = {
    # Español oficial
    "NORMAL": "NORMAL",
    "EXTRA_DIMENSIONADO": "EXTRA_DIMENSIONADO",
    # Variantes
    "extra_dimensioned": "EXTRA_DIMENSIONADO",
    "EXTRA_DIMENSIONED": "EXTRA_DIMENSIONADO",
    "normal": "NORMAL",
}

CONDITION_MAP = {
    # Español oficial
    "BUENO": "BUENO",
    "ABIERTO": "ABIERTO",
    "REGULAR": "REGULAR",
    # Variantes
    "OK": "BUENO",
    "ok": "BUENO",
    "OPENED": "ABIERTO",
    "opened": "ABIERTO",
    "incompleto": "REGULAR",
}


def normalize_status(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return STATUS_MAP.get(str(value), STATUS_MAP.get(str(value).upper(), str(value).upper()))


def normalize_type(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return TYPE_MAP.get(str(value), TYPE_MAP.get(str(value).upper(), str(value).upper()))


def normalize_condition(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return CONDITION_MAP.get(str(value), CONDITION_MAP.get(str(value).upper(), str(value).upper()))


def normalize_package_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza campos de un dict de paquete/anuncio para respuestas JSON unificadas."""
    item = dict(item or {})
    if "status" in item:
        item["status"] = normalize_status(item["status"]) or item["status"]
    if "package_type" in item:
        item["package_type"] = normalize_type(item["package_type"]) or item["package_type"]
    if "package_condition" in item:
        item["package_condition"] = normalize_condition(item["package_condition"]) or item["package_condition"]
    return item


def normalize_history_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event or {})
    if "status" in event:
        event["status"] = normalize_status(event["status"]) or event["status"]
    details = event.get("details")
    if isinstance(details, dict):
        details = dict(details)
        if "package_type" in details:
            details["package_type"] = normalize_type(details["package_type"]) or details["package_type"]
        if "package_condition" in details:
            details["package_condition"] = normalize_condition(details["package_condition"]) or details["package_condition"]
        event["details"] = details
    return event


