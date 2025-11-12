# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Esquemas de Anuncios
Versión: 1.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from .base import TimestampSchema, IDSchema

class AnnouncementBase(BaseModel):
    """Esquema base para anuncios"""
    customer_name: str
    customer_phone: str
    guide_number: str
    tracking_code: Optional[str] = None
    is_active: bool = True
    is_processed: bool = False

    @validator('customer_phone')
    def validate_phone_format(cls, v):
        """Validar formato de teléfono colombiano"""
        if not v:
            raise ValueError('El teléfono es requerido')
        # Remover espacios y caracteres especiales
        phone = ''.join(c for c in v if c.isdigit())
        if len(phone) < 10:
            raise ValueError('El teléfono debe tener al menos 10 dígitos')
        return phone

    @validator('customer_name')
    def validate_customer_name(cls, v):
        """Validar y convertir nombre del cliente a mayúsculas"""
        if not v or not v.strip():
            raise ValueError('El nombre del cliente es requerido')
        return v.strip().upper()

    @validator('guide_number')
    def validate_guide_number(cls, v):
        """Validar número de guía"""
        if not v or not v.strip():
            raise ValueError('El número de guía es requerido')
        return v.strip().upper()

class AnnouncementCreate(AnnouncementBase):
    """Esquema para crear anuncios"""
    pass

class AnnouncementUpdate(BaseModel):
    """Esquema para actualizar anuncios"""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    guide_number: Optional[str] = None
    tracking_code: Optional[str] = None
    is_active: Optional[bool] = None
    is_processed: Optional[bool] = None

    @validator('customer_name')
    def validate_customer_name(cls, v):
        """Validar y convertir nombre del cliente a mayúsculas"""
        if v is not None and v.strip():
            return v.strip().upper()
        return v

    @validator('guide_number')
    def validate_guide_number(cls, v):
        """Validar y convertir número de guía a mayúsculas"""
        if v is not None and v.strip():
            return v.strip().upper()
        return v

class AnnouncementResponse(IDSchema, AnnouncementBase, TimestampSchema):
    """Esquema de respuesta para anuncios"""
    processed_at: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True

class AnnouncementListResponse(BaseModel):
    """Esquema de respuesta para lista de anuncios"""
    announcements: list[AnnouncementResponse]
    total: int
    skip: int = 0
    limit: int = 50

class AnnouncementSearchRequest(BaseModel):
    """Esquema para búsqueda de anuncios"""
    query: Optional[str] = None
    status: Optional[str] = None  # pending, processed, cancelled
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class AnnouncementStatsResponse(BaseModel):
    """Esquema de estadísticas de anuncios"""
    total_announcements: int
    pending_count: int
    processed_count: int
    cancelled_count: int
    today_count: int
    this_week_count: int
    this_month_count: int