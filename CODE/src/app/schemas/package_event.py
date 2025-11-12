# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Esquemas de Eventos de Paquete
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum
from decimal import Decimal
from uuid import UUID


class EventType(str, Enum):
    """Tipos de eventos del ciclo de vida del paquete"""
    ANUNCIO = "ANUNCIO"
    RECEPCION = "RECEPCION"
    ENTREGA = "ENTREGA"
    CANCELACION = "CANCELACION"
    MODIFICACION = "MODIFICACION"
    IMAGEN_AGREGADA = "IMAGEN_AGREGADA"
    NOTA_AGREGADA = "NOTA_AGREGADA"


class PackageEventBase(BaseModel):
    """Esquema base para eventos de paquete"""
    event_type: EventType
    tracking_number: Optional[str] = None
    guide_number: Optional[str] = None
    access_code: Optional[str] = None
    tracking_code: Optional[str] = None
    status_before: Optional[str] = None
    status_after: str
    package_type: Optional[str] = None
    package_condition: Optional[str] = None
    baroti: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    observations: Optional[str] = None
    
    class Config:
        from_attributes = True


class PackageEventCreate(BaseModel):
    """Esquema para crear un evento de paquete"""
    package_id: Optional[int] = None
    announcement_id: Optional[UUID] = None
    event_type: EventType
    tracking_number: Optional[str] = None
    guide_number: Optional[str] = None
    access_code: Optional[str] = None
    tracking_code: Optional[str] = None
    status_before: Optional[str] = None
    status_after: str
    package_type: Optional[str] = None
    package_condition: Optional[str] = None
    baroti: Optional[str] = None
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    base_fee: Optional[Decimal] = None
    storage_fee: Optional[Decimal] = None
    storage_days: Optional[int] = None
    total_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    payment_amount: Optional[Decimal] = None
    payment_received: Optional[bool] = False
    operator_id: Optional[int] = None
    operator_name: Optional[str] = None
    operator_role: Optional[str] = None
    file_ids: Optional[Dict[str, List[int]]] = None
    observations: Optional[str] = None
    cancellation_reason: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class PackageEventResponse(BaseModel):
    """Esquema de respuesta para eventos de paquete"""
    id: UUID
    package_id: Optional[int] = None
    announcement_id: Optional[UUID] = None
    event_type: EventType
    event_timestamp: datetime
    
    # Identificadores
    tracking_number: Optional[str] = None
    guide_number: Optional[str] = None
    access_code: Optional[str] = None
    tracking_code: Optional[str] = None
    
    # Estados
    status_before: Optional[str] = None
    status_after: str
    package_type: Optional[str] = None
    package_condition: Optional[str] = None
    baroti: Optional[str] = None
    
    # Cliente
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    
    # Financiero
    base_fee: Optional[Decimal] = None
    storage_fee: Optional[Decimal] = None
    storage_days: Optional[int] = None
    total_amount: Optional[Decimal] = None
    payment_method: Optional[str] = None
    payment_amount: Optional[Decimal] = None
    payment_received: Optional[bool] = None
    
    # Operador
    operator_id: Optional[int] = None
    operator_name: Optional[str] = None
    operator_role: Optional[str] = None
    
    # Archivos y observaciones
    file_ids: Optional[Dict[str, List[int]]] = None
    observations: Optional[str] = None
    cancellation_reason: Optional[str] = None
    
    # Adicionales
    additional_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PackageEventListResponse(BaseModel):
    """Esquema de respuesta para lista de eventos"""
    total: int
    events: List[PackageEventResponse]
    page: int = 1
    page_size: int = 50


class PackageEventFilter(BaseModel):
    """Esquema para filtrar eventos"""
    package_id: Optional[int] = None
    tracking_number: Optional[str] = None
    guide_number: Optional[str] = None
    tracking_code: Optional[str] = None
    event_type: Optional[EventType] = None
    customer_phone: Optional[str] = None
    operator_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


class PackageEventStats(BaseModel):
    """Estadísticas de eventos"""
    total_events: int
    events_by_type: Dict[str, int]
    events_today: int
    events_this_week: int
    events_this_month: int
    revenue_today: Decimal
    revenue_this_week: Decimal
    revenue_this_month: Decimal


class PackageHistoryResponse(BaseModel):
    """Respuesta con el historial completo de un paquete"""
    package_id: int
    tracking_number: str
    guide_number: Optional[str] = None
    current_status: str
    timeline: List[PackageEventResponse]
    total_events: int
    
    class Config:
        from_attributes = True


