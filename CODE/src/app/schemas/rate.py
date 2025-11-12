# ========================================
# PAQUETES EL CLUB v4.0 - Esquemas de Tarifas
# ========================================

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from uuid import UUID

from .base import TimestampSchema
from app.models.rate import RateType

class RateBase(BaseModel):
    """Esquema base de tarifa"""
    rate_type: RateType
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    base_price: Decimal = Field(..., gt=0)
    daily_storage_rate: Decimal = Field(default=Decimal('0'), ge=0)
    delivery_rate: Decimal = Field(default=Decimal('0'), ge=0)
    package_type_multiplier: Decimal = Field(default=Decimal('1.0'), ge=0)

    @validator('base_price', 'daily_storage_rate', 'delivery_rate', 'package_type_multiplier')
    def validate_positive_amounts(cls, v):
        if v < 0:
            raise ValueError('Los montos deben ser positivos')
        return v

class RateCreate(RateBase):
    """Esquema para crear tarifa"""
    pass

class RateUpdate(BaseModel):
    """Esquema para actualizar tarifa"""
    rate_type: Optional[RateType] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    base_price: Optional[Decimal] = Field(None, gt=0)
    daily_storage_rate: Optional[Decimal] = Field(None, ge=0)
    delivery_rate: Optional[Decimal] = Field(None, ge=0)
    package_type_multiplier: Optional[Decimal] = Field(None, ge=0)

class RateResponse(TimestampSchema, RateBase):
    """Esquema de respuesta de tarifa"""
    id: UUID
    is_active: bool
    valid_from: datetime
    valid_to: Optional[datetime]
    created_by_id: Optional[UUID]
    updated_by_id: Optional[UUID]

class RateListResponse(BaseModel):
    """Esquema de respuesta para lista de tarifas"""
    rates: List[RateResponse]
    total: int
    skip: int
    limit: int

class RateCalculationRequest(BaseModel):
    """Esquema para solicitud de cálculo de tarifa"""
    package_type: str = Field(..., description="Tipo de paquete")
    storage_days: Optional[int] = Field(0, ge=0, description="Días de almacenamiento")
    delivery_required: bool = Field(True, description="Requiere entrega")

class RateCalculationResponse(BaseModel):
    """Esquema de respuesta de cálculo de tarifa"""
    base_cost: Decimal
    storage_cost: Decimal
    delivery_cost: Decimal
    total_cost: Decimal
    breakdown: dict
    applied_rates: dict

class RateSummaryResponse(BaseModel):
    """Esquema de resumen de tarifas"""
    active_rates: int
    total_rates: int
    rates_by_type: dict
    last_updated: Optional[datetime]

class RateHistoryResponse(BaseModel):
    """Esquema de historial de tarifas"""
    rate_id: UUID
    rate_type: RateType
    changes: List[dict]
    total_changes: int

class BulkRateUpdateRequest(BaseModel):
    """Esquema para actualización masiva de tarifas"""
    rate_ids: List[UUID]
    updates: RateUpdate
    reason: Optional[str] = Field(None, max_length=255)

class BulkRateUpdateResponse(BaseModel):
    """Esquema de respuesta de actualización masiva"""
    updated_count: int
    failed_count: int
    errors: List[dict]