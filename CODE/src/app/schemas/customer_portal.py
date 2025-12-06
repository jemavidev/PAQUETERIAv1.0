# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Esquemas para Portal de Clientes
Versión: 1.0.0
Fecha: 2025-01-30
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID


# ========================================
# OTP Requests/Responses
# ========================================

class OTPRequest(BaseModel):
    """Solicitud de código OTP"""
    phone: str = Field(..., min_length=10, max_length=20, description="Número de teléfono")

    @validator('phone')
    def validate_phone(cls, v):
        # Limpiar el teléfono
        clean = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not clean.replace('+', '').isdigit():
            raise ValueError('Teléfono debe contener solo números')
        return clean


class OTPResponse(BaseModel):
    """Respuesta de solicitud OTP"""
    success: bool
    message: str
    expires_in_seconds: Optional[int] = 300  # 5 minutos


class OTPVerifyRequest(BaseModel):
    """Verificación de código OTP"""
    phone: str = Field(..., min_length=10, max_length=20)
    code: str = Field(..., min_length=6, max_length=6, description="Código de 6 dígitos")

    @validator('code')
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError('El código debe contener solo números')
        return v


class OTPVerifyResponse(BaseModel):
    """Respuesta de verificación OTP"""
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    expires_in: Optional[int] = 3600  # 1 hora


# ========================================
# Customer Portal Data
# ========================================

class CustomerPortalData(BaseModel):
    """Datos del cliente para el portal (solo lectura/edición limitada)"""
    id: UUID
    first_name: str
    last_name: Optional[str]
    full_name: str
    phone: str  # Solo lectura
    email: Optional[str]
    
    # Dirección
    address_street: Optional[str]
    address_city: Optional[str]
    address_state: Optional[str]
    address_country: str = "Colombia"
    
    # Edificio
    building_name: Optional[str]
    tower: Optional[str]
    apartment: Optional[str]
    floor: Optional[str]
    
    # Metadata (solo lectura)
    created_at: datetime
    updated_at: datetime
    
    # Estadísticas (solo lectura)
    total_packages_received: int
    total_packages_delivered: int

    class Config:
        from_attributes = True


class CustomerPortalUpdate(BaseModel):
    """Actualización de datos del cliente (campos editables)"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    
    # Dirección
    address_street: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=50)
    address_state: Optional[str] = Field(None, max_length=50)
    
    # Edificio
    building_name: Optional[str] = Field(None, max_length=100)
    tower: Optional[str] = Field(None, max_length=10)
    apartment: Optional[str] = Field(None, max_length=10)
    floor: Optional[str] = Field(None, max_length=10)


# ========================================
# Package History
# ========================================

class CustomerPackageHistory(BaseModel):
    """Historial de paquetes del cliente"""
    id: int  # Package usa Integer ID, no UUID
    tracking_number: str
    guide_number: Optional[str]
    status: str
    
    # Fechas
    announced_at: Optional[datetime]
    received_at: Optional[datetime]
    delivered_at: Optional[datetime]
    
    # Información adicional
    package_type: Optional[str]
    carrier: Optional[str]
    
    class Config:
        from_attributes = True


class CustomerPackageHistoryResponse(BaseModel):
    """Respuesta con historial de paquetes"""
    packages: List[CustomerPackageHistory]
    total: int
