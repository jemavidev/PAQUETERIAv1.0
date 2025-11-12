# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Esquemas de Paquete
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
from decimal import Decimal
from uuid import UUID

from .base import BaseSchema, TimestampSchema, IDSchema


class PackageType(str, Enum):
    """Tipos de paquete disponibles"""
    NORMAL = "NORMAL"
    EXTRA_DIMENSIONADO = "EXTRA_DIMENSIONADO"


class PackageStatus(str, Enum):
    """Estados posibles del paquete"""
    ANUNCIADO = "ANUNCIADO"
    RECIBIDO = "RECIBIDO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class PackageCondition(str, Enum):
    """Condiciones del paquete"""
    BUENO = "BUENO"
    ABIERTO = "ABIERTO"
    REGULAR = "REGULAR"


class PaymentMethod(str, Enum):
    """Métodos de pago disponibles"""
    CASH = "efectivo"
    CARD = "tarjeta"
    TRANSFER = "transferencia"


class CancellationReason(str, Enum):
    """Razones de cancelación de paquetes"""
    CLIENT_REQUEST = "cliente_solicita"
    CLIENT_NOT_PICKUP = "cliente_no_reclama"
    DAMAGED_PACKAGE = "paquete_danado"
    LOST_PACKAGE = "paquete_perdido"
    EXPIRED_ANNOUNCEMENT = "anuncio_expirado"
    OPERATOR_ERROR = "error_operador"
    OTHER = "otro"


class PackageBase(BaseSchema):
    """Esquema base para paquetes"""
    tracking_number: str = Field(..., pattern=r'^PAP\d{8}[A-Z0-9]{4}$', description="Número de tracking único")
    customer_name: str = Field(..., min_length=2, max_length=100, description="Nombre del cliente")
    customer_phone: str = Field(..., pattern=r'^\+57\s?\d{3}\s?\d{3}\s?\d{4}$', description="Teléfono del cliente")
    package_type: PackageType = Field(default=PackageType.NORMAL, description="Tipo de paquete")
    status: PackageStatus = Field(default=PackageStatus.ANUNCIADO, description="Estado del paquete")
    package_condition: PackageCondition = Field(default=PackageCondition.BUENO, description="Condición del paquete")
    access_code: str = Field(..., min_length=6, max_length=20, description="Código de acceso único")
    baroti: Optional[str] = Field(None, pattern=r'^\d{2}$', description="Posición física (00-99)")
    observations: Optional[str] = Field(None, max_length=500, description="Observaciones del paquete")


class PackageCreate(PackageBase):
    """Esquema para crear paquetes"""
    guide_number: str = Field(..., min_length=3, max_length=50, description="Número de guía del transportador")

    @validator('tracking_number')
    def validate_tracking_format(cls, v):
        """Valida el formato del tracking number"""
        import re
        if not re.match(r'^PAP\d{8}[A-Z0-9]{4}$', v):
            raise ValueError('El número de tracking debe tener formato PAP + 8 dígitos + 4 caracteres alfanuméricos')
        return v


class PackageUpdate(BaseSchema):
    """Esquema para actualizar paquetes"""
    status: Optional[PackageStatus] = None
    package_condition: Optional[PackageCondition] = None
    baroti: Optional[str] = Field(None, pattern=r'^\d{2}$')
    observations: Optional[str] = Field(None, max_length=500)


class PackageStatusUpdate(BaseSchema):
    """Esquema para actualizar solo el estado del paquete"""
    status: PackageStatus = Field(..., description="Nuevo estado del paquete")
    package_type: Optional[PackageType] = Field(None, description="Tipo de paquete (al recibir)")
    package_condition: Optional[PackageCondition] = Field(None, description="Condición del paquete (al recibir)")
    observations: Optional[str] = Field(None, max_length=500, description="Observaciones del cambio")


class PackageResponse(IDSchema, PackageBase, TimestampSchema):
    """Esquema de respuesta para paquetes"""
    announced_at: datetime
    received_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    base_fee: Decimal = Field(default=Decimal('1500.00'), description="Tarifa base")
    storage_fee: Decimal = Field(default=Decimal('0.00'), description="Tarifa de almacenamiento")
    total_amount: Decimal = Field(default=Decimal('0.00'), description="Monto total")

    # Información del cliente (opcional para respuestas)
    customer_id: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class PackageStats(BaseSchema):
    """Esquema para estadísticas de paquetes"""
    total_packages: int
    announced_count: int
    received_count: int
    delivered_count: int
    cancelled_count: int
    total_revenue: Decimal


class PackageSearch(BaseSchema):
    """Esquema para búsqueda de paquetes"""
    query: str = Field(..., description="Término de búsqueda (tracking, nombre, teléfono)")
    status: Optional[PackageStatus] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PackageAnnouncement(BaseSchema):
    """Esquema para anuncio de paquetes (versión simplificada)"""
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_phone: str = Field(..., pattern=r'^\+57\s?\d{3}\s?\d{3}\s?\d{4}$')
    guide_number: str = Field(..., min_length=3, max_length=50)
    tracking_number: Optional[str] = Field(None, description="Número de tracking (opcional, se genera si no se proporciona)")

    @validator('customer_phone')
    def validate_phone_format(cls, v):
        """Valida el formato del teléfono colombiano"""
        import re
        if not re.match(r'^\+57\s?\d{3}\s?\d{3}\s?\d{4}$', v):
            raise ValueError('El teléfono debe tener formato +57 300 123 4567')
        return v


# ========================================
# NUEVOS ESQUEMAS PARA TRANSICIONES AVANZADAS
# ========================================

class PackageReceiveRequest(BaseSchema):
    """Esquema para solicitud de recepción de paquete desde anuncio"""
    announcement_id: str = Field(..., description="Tracking code del anuncio a procesar")
    package_type: PackageType = Field(..., description="Tipo de paquete determinado físicamente")
    package_condition: PackageCondition = Field(..., description="Condición física del paquete")
    baroti: Optional[str] = Field(None, description="Posición física en bodega (00-99) - Se genera automáticamente")
    observations: Optional[str] = Field(None, max_length=500, description="Observaciones de recepción")
    operator_id: int = Field(..., description="ID del operador que recibe el paquete")


class PackageDeliverRequest(BaseSchema):
    """Esquema para solicitud de entrega de paquete"""
    customer_id: Optional[UUID] = Field(None, description="ID del cliente que reclama el paquete (UUID)")
    payment_method: PaymentMethod = Field(..., description="Método de pago utilizado")
    payment_amount: Decimal = Field(..., ge=0, description="Monto pagado por el cliente")
    operator_id: int = Field(..., description="ID del operador que entrega el paquete")
    customer_signature: Optional[str] = Field(None, description="Firma digital del cliente (base64)")


class PackageCancelRequest(BaseSchema):
    """Esquema para solicitud de cancelación de paquete"""
    reason: CancellationReason = Field(..., description="Razón de la cancelación")
    observations: Optional[str] = Field(None, max_length=500, description="Observaciones detalladas")
    refund_amount: Decimal = Field(default=Decimal('0.00'), ge=0, description="Monto a reembolsar")
    operator_id: int = Field(..., description="ID del operador que procesa la cancelación")


class PackageReceiveResponse(BaseSchema):
    """Esquema de respuesta para recepción de paquete"""
    success: bool
    package_id: int
    tracking_number: str
    access_code: str
    baroti: str  # Número BAROTI generado
    total_amount: Decimal
    base_fee: Decimal
    storage_fee: Decimal
    storage_days: int
    message: str
    received_at: datetime


class PackageDeliverResponse(BaseSchema):
    """Esquema de respuesta para entrega de paquete"""
    success: bool
    package_id: int
    tracking_number: str
    delivered_at: datetime
    payment_method: PaymentMethod
    payment_amount: Decimal
    operator_name: str
    message: str


class PackageCancelResponse(BaseSchema):
    """Esquema de respuesta para cancelación de paquete"""
    success: bool
    package_id: int
    tracking_number: str
    cancelled_at: datetime
    reason: CancellationReason
    refund_amount: Decimal
    message: str


class PackageFeeCalculation(BaseSchema):
    """Esquema para cálculo detallado de tarifas"""
    base_fee: Decimal
    storage_fee: Decimal
    storage_days: int
    total_amount: Decimal
    breakdown: dict
    calculated_at: datetime