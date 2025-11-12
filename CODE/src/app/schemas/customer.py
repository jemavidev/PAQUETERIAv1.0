# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Esquemas de Cliente Expandidos
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from uuid import UUID

from .base import TimestampSchema
from app.models.customer import Customer

class CustomerBase(BaseModel):
    """Esquema base para clientes"""
    first_name: str = Field(..., min_length=1, max_length=50, description="Nombre del cliente")
    last_name: str = Field(..., min_length=1, max_length=50, description="Apellido del cliente")
    phone: str = Field(..., min_length=7, max_length=20, description="Teléfono principal")
    email: Optional[EmailStr] = Field(None, description="Email principal")

    # Información adicional opcional
    document_type: Optional[str] = Field(None, max_length=10, description="Tipo de documento")
    document_number: Optional[str] = Field(None, max_length=20, description="Número de documento")
    birth_date: Optional[datetime] = Field(None, description="Fecha de nacimiento")

    # Dirección
    address_street: Optional[str] = Field(None, max_length=100, description="Dirección")
    address_city: Optional[str] = Field(None, max_length=50, description="Ciudad")
    address_state: Optional[str] = Field(None, max_length=50, description="Estado/Departamento")
    address_zip: Optional[str] = Field(None, max_length=10, description="Código postal")
    address_country: str = Field("Colombia", description="País")

    # Información del edificio
    building_name: Optional[str] = Field(None, max_length=100, description="Nombre del edificio")
    tower: Optional[str] = Field(None, max_length=10, description="Torre")
    apartment: Optional[str] = Field(None, max_length=10, description="Apartamento")
    floor: Optional[str] = Field(None, max_length=10, description="Piso")

    # Información adicional
    notes: Optional[str] = Field(None, max_length=1000, description="Notas adicionales")
    preferred_language: str = Field("es", description="Idioma preferido")
    is_vip: bool = Field(False, description="Cliente VIP")

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.replace(' ', '').replace('+', '').replace('-', '').isdigit():
            raise ValueError('El teléfono debe contener solo números, espacios, + o -')
        return v

    @validator('document_number')
    def validate_document(cls, v):
        if v and not v.replace(' ', '').replace('-', '').replace('.', '').isdigit():
            raise ValueError('El número de documento debe contener solo números, espacios, - o .')
        return v

class CustomerCreate(CustomerBase):
    """Esquema para crear clientes"""
    pass

class CustomerUpdate(BaseModel):
    """Esquema para actualizar clientes"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[EmailStr] = None
    document_type: Optional[str] = Field(None, max_length=10)
    document_number: Optional[str] = Field(None, max_length=20)
    birth_date: Optional[datetime] = None
    address_street: Optional[str] = Field(None, max_length=100)
    address_city: Optional[str] = Field(None, max_length=50)
    address_state: Optional[str] = Field(None, max_length=50)
    address_zip: Optional[str] = Field(None, max_length=10)
    address_country: Optional[str] = Field(None, max_length=50)
    building_name: Optional[str] = Field(None, max_length=100)
    tower: Optional[str] = Field(None, max_length=10)
    apartment: Optional[str] = Field(None, max_length=10)
    floor: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = Field(None, max_length=1000)
    preferred_language: Optional[str] = Field(None, max_length=10)
    is_vip: Optional[bool] = None

class CustomerResponse(TimestampSchema, CustomerBase):
    """Esquema de respuesta para clientes"""
    id: UUID
    full_name: str
    is_active: bool
    total_packages_received: int
    total_packages_delivered: int
    total_spent: float  # En pesos (no centavos)

    # Información calculada
    display_name: str
    full_address: str
    contact_info: Dict[str, Any]
    package_stats: Dict[str, Any]

class CustomerListResponse(BaseModel):
    """Esquema para lista de clientes"""
    customers: List[CustomerResponse]
    total: int
    skip: int
    limit: int
    search_term: Optional[str] = None

class CustomerSearchRequest(BaseModel):
    """Esquema para búsqueda de clientes"""
    query: str = Field(..., min_length=1, max_length=100, description="Término de búsqueda")
    search_by: str = Field("all", description="Campo de búsqueda: all, name, phone, email, document")

class CustomerStatsResponse(BaseModel):
    """Esquema para estadísticas de clientes"""
    total_customers: int
    active_customers: int
    vip_customers: int
    customers_by_city: Dict[str, int]
    top_customers_by_packages: List[Dict[str, Any]]
    recent_registrations: int

class CustomerMergeRequest(BaseModel):
    """Esquema para fusionar clientes duplicados"""
    primary_customer_id: UUID
    duplicate_customer_id: UUID
    merge_strategy: str = Field("keep_primary", description="Estrategia: keep_primary, keep_most_recent, manual")

class CustomerBulkUpdateRequest(BaseModel):
    """Esquema para actualización masiva de clientes"""
    customer_ids: List[UUID]
    updates: CustomerUpdate
    reason: Optional[str] = Field(None, max_length=255)

class CustomerBulkUpdateResponse(BaseModel):
    """Esquema de respuesta para actualización masiva"""
    updated_count: int
    failed_count: int
    errors: List[Dict[str, Any]]

class CustomerImportRequest(BaseModel):
    """Esquema para importar clientes desde CSV"""
    csv_data: str
    update_existing: bool = Field(False, description="Actualizar clientes existentes")
    skip_duplicates: bool = Field(True, description="Omitir duplicados")

class CustomerImportResponse(BaseModel):
    """Esquema de respuesta para importación"""
    imported_count: int
    updated_count: int
    skipped_count: int
    errors: List[Dict[str, Any]]