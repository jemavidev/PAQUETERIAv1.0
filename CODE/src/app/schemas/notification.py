# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Esquemas de Notificaciones SMS
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from uuid import UUID

from .base import TimestampSchema
from app.models.notification import NotificationType, NotificationStatus, NotificationEvent, NotificationPriority

class NotificationBase(BaseModel):
    """Esquema base para notificaciones"""
    notification_type: NotificationType
    event_type: NotificationEvent
    priority: NotificationPriority = NotificationPriority.MEDIA
    recipient: str = Field(..., min_length=1, max_length=100, description="Destinatario (teléfono, email, etc.)")
    recipient_name: Optional[str] = Field(None, max_length=100, description="Nombre del destinatario")
    subject: Optional[str] = Field(None, max_length=200, description="Asunto (para emails)")
    message: str = Field(..., min_length=1, max_length=1000, description="Contenido del mensaje")
    message_template: Optional[str] = Field(None, max_length=100, description="ID de plantilla usada")

class NotificationCreate(NotificationBase):
    """Esquema para crear notificaciones"""
    package_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    announcement_id: Optional[UUID] = None
    is_scheduled: bool = False
    scheduled_at: Optional[datetime] = None
    is_test: bool = False

class NotificationUpdate(BaseModel):
    """Esquema para actualizar notificaciones"""
    status: Optional[NotificationStatus] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    provider_id: Optional[str] = None
    cost_cents: Optional[int] = None

class NotificationResponse(TimestampSchema, NotificationBase):
    """Esquema de respuesta para notificaciones"""
    id: UUID
    package_id: Optional[UUID]
    customer_id: Optional[UUID]
    announcement_id: Optional[UUID]
    status: NotificationStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    error_code: Optional[str]
    provider_id: Optional[str]
    provider_response: Optional[str]
    cost_cents: int
    retry_count: int
    max_retries: int
    next_retry_at: Optional[datetime]
    is_scheduled: bool
    scheduled_at: Optional[datetime]
    is_test: bool

    # Propiedades calculadas
    is_successful: bool
    can_retry: bool

class NotificationListResponse(BaseModel):
    """Esquema para lista de notificaciones"""
    notifications: List[NotificationResponse]
    total: int
    skip: int
    limit: int
    search_term: Optional[str] = None

class NotificationStatsResponse(BaseModel):
    """Esquema para estadísticas de notificaciones"""
    total_notifications: int
    sent_notifications: int
    delivered_notifications: int
    failed_notifications: int
    pending_notifications: int
    total_cost_cents: int
    average_cost_per_sms: float
    notifications_by_type: Dict[str, int]
    notifications_by_event: Dict[str, int]
    recent_failures: List[Dict[str, Any]]

# ========================================
# ESQUEMAS PARA PLANTILLAS SMS
# ========================================

class SMSMessageTemplateBase(BaseModel):
    """Esquema base para plantillas SMS"""
    template_id: str = Field(..., min_length=1, max_length=50, description="ID único de la plantilla")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre de la plantilla")
    event_type: NotificationEvent
    language: str = Field("es", max_length=10, description="Idioma de la plantilla")
    subject: Optional[str] = Field(None, max_length=200, description="Asunto (para emails)")
    message_template: str = Field(..., min_length=1, max_length=1000, description="Plantilla con placeholders")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la plantilla")
    available_variables: Optional[str] = Field(None, description="Variables disponibles en JSON")

class SMSMessageTemplateCreate(SMSMessageTemplateBase):
    """Esquema para crear plantillas SMS"""
    is_default: bool = False

class SMSMessageTemplateUpdate(BaseModel):
    """Esquema para actualizar plantillas SMS"""
    name: Optional[str] = Field(None, max_length=100)
    message_template: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = Field(None, max_length=500)
    available_variables: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

class SMSMessageTemplateResponse(TimestampSchema, SMSMessageTemplateBase):
    """Esquema de respuesta para plantillas SMS"""
    id: UUID
    is_active: bool
    is_default: bool

class SMSMessageTemplateListResponse(BaseModel):
    """Esquema para lista de plantillas SMS"""
    templates: List[SMSMessageTemplateResponse]
    total: int

# ========================================
# ESQUEMAS PARA CONFIGURACIÓN SMS
# ========================================

class SMSConfigurationBase(BaseModel):
    """Esquema base para configuración SMS"""
    provider: str = Field("liwa", max_length=50, description="Proveedor de SMS")
    api_key: Optional[str] = Field(None, max_length=255, description="API Key del proveedor")
    account_id: Optional[str] = Field(None, max_length=100, description="ID de cuenta")
    password: Optional[str] = Field(None, max_length=255, description="Contraseña")
    auth_url: Optional[str] = Field(None, max_length=255, description="URL de autenticación")
    api_url: Optional[str] = Field(None, max_length=255, description="URL de API")
    default_sender: str = Field("PAQUETES", max_length=20, description="Remitente por defecto")
    max_message_length: int = Field(160, ge=1, le=1000, description="Longitud máxima de mensaje")
    enable_delivery_reports: bool = Field(True, description="Habilitar reportes de entrega")
    enable_test_mode: bool = Field(False, description="Modo de pruebas")
    daily_limit: int = Field(1000, ge=1, description="Límite diario de SMS")
    monthly_limit: int = Field(30000, ge=1, description="Límite mensual de SMS")
    cost_per_sms_cents: int = Field(50, ge=0, description="Costo por SMS en centavos")

class SMSConfigurationCreate(SMSConfigurationBase):
    """Esquema para crear configuración SMS"""
    pass

class SMSConfigurationUpdate(BaseModel):
    """Esquema para actualizar configuración SMS"""
    provider: Optional[str] = Field(None, max_length=50)
    api_key: Optional[str] = Field(None, max_length=255)
    account_id: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, max_length=255)
    auth_url: Optional[str] = Field(None, max_length=255)
    api_url: Optional[str] = Field(None, max_length=255)
    default_sender: Optional[str] = Field(None, max_length=20)
    max_message_length: Optional[int] = Field(None, ge=1, le=1000)
    enable_delivery_reports: Optional[bool] = None
    enable_test_mode: Optional[bool] = None
    daily_limit: Optional[int] = Field(None, ge=1)
    monthly_limit: Optional[int] = Field(None, ge=1)
    cost_per_sms_cents: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class SMSConfigurationResponse(TimestampSchema, SMSConfigurationBase):
    """Esquema de respuesta para configuración SMS"""
    id: UUID
    is_active: bool
    last_test_at: Optional[datetime]
    last_test_result: Optional[str]

# ========================================
# ESQUEMAS PARA ENVÍO DE SMS
# ========================================

class SMSSendRequest(BaseModel):
    """Esquema para enviar SMS individual"""
    recipient: str = Field(..., pattern=r'^\+57\s?\d{3}\s?\d{3}\s?\d{4}$', description="Número de teléfono colombiano")
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje a enviar")
    priority: NotificationPriority = NotificationPriority.MEDIA
    is_test: bool = False

class SMSBulkSendRequest(BaseModel):
    """Esquema para envío masivo de SMS"""
    recipients: List[str] = Field(..., min_items=1, max_items=100, description="Lista de números de teléfono")
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje a enviar")
    priority: NotificationPriority = NotificationPriority.MEDIA
    is_test: bool = False

class SMSByEventRequest(BaseModel):
    """Esquema para enviar SMS por evento"""
    event_type: NotificationEvent
    package_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    announcement_id: Optional[UUID] = None
    custom_variables: Optional[Dict[str, Any]] = Field(None, description="Variables personalizadas")
    priority: NotificationPriority = NotificationPriority.MEDIA
    is_test: bool = False

class SMSSendResponse(BaseModel):
    """Esquema de respuesta para envío de SMS"""
    notification_id: int
    status: str
    message: str
    cost_cents: int

class SMSBulkSendResponse(BaseModel):
    """Esquema de respuesta para envío masivo"""
    sent_count: int
    failed_count: int
    total_cost_cents: int
    results: List[Dict[str, Any]]

# ========================================
# ESQUEMAS PARA WEBHOOKS Y CALLBACKS
# ========================================

class SMSWebhookPayload(BaseModel):
    """Esquema para payload de webhook SMS"""
    message_id: str
    status: str
    recipient: str
    timestamp: datetime
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    provider_data: Optional[Dict[str, Any]] = None

class SMSWebhookResponse(BaseModel):
    """Esquema de respuesta para webhooks"""
    received: bool
    message: str
    processed_at: datetime

# ========================================
# ESQUEMAS PARA REPORTES Y ANALYTICS
# ========================================

class SMSReportRequest(BaseModel):
    """Esquema para solicitar reportes SMS"""
    start_date: datetime
    end_date: datetime
    event_type: Optional[NotificationEvent] = None
    status: Optional[NotificationStatus] = None
    recipient: Optional[str] = None

class SMSReportResponse(BaseModel):
    """Esquema de respuesta para reportes SMS"""
    total_sent: int
    total_delivered: int
    total_failed: int
    total_cost_cents: int
    average_delivery_rate: float
    messages_by_day: List[Dict[str, Any]]
    failures_by_reason: Dict[str, int]
    top_recipients: List[Dict[str, Any]]

# ========================================
# ESQUEMAS PARA TESTING
# ========================================

class SMSTestRequest(BaseModel):
    """Esquema para probar configuración SMS"""
    recipient: str = Field(..., pattern=r'^\+57\s?\d{3}\s?\d{3}\s?\d{4}$', description="Número de teléfono para prueba")
    message: str = Field("Test SMS from PAQUETES EL CLUB v1.0", min_length=1, max_length=160, description="Mensaje de prueba")

class SMSTestResponse(BaseModel):
    """Esquema de respuesta para pruebas SMS"""
    success: bool
    message: str
    notification_id: Optional[UUID]
    provider_response: Optional[Dict[str, Any]]
    error_details: Optional[str]