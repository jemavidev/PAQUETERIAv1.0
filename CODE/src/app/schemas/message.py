# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Esquemas de Mensaje Expandidos
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

from .base import BaseSchema, TimestampSchema, IDSchema


class MessageStatus(str, Enum):
    """Estados de los mensajes"""
    ABIERTO = "ABIERTO"
    LEIDO = "LEIDO"
    RESPONDIDO = "RESPONDIDO"
    CERRADO = "CERRADO"


class MessageType(str, Enum):
    """Tipos de mensaje"""
    CONSULTA = "CONSULTA"


class MessagePriority(str, Enum):
    """Prioridad de los mensajes"""
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class MessageBase(BaseSchema):
    """Esquema base para mensajes"""
    subject: str = Field(..., min_length=5, max_length=200, description="Asunto del mensaje")
    content: str = Field(..., min_length=10, max_length=2000, description="Contenido del mensaje")
    message_type: MessageType = Field(default=MessageType.CONSULTA, description="Tipo de mensaje")
    priority: MessagePriority = Field(default=MessagePriority.MEDIA, description="Prioridad del mensaje")
    status: MessageStatus = Field(default=MessageStatus.ABIERTO, description="Estado del mensaje")
    is_read: bool = Field(default=False, description="Si el mensaje ha sido leído")


class MessageSender(BaseSchema):
    """Información del remitente"""
    sender_name: Optional[str] = Field(None, max_length=100, description="Nombre del remitente")
    sender_email: Optional[EmailStr] = Field(None, description="Email del remitente")
    sender_phone: Optional[str] = Field(None, max_length=20, description="Teléfono del remitente")


class MessageRecipient(BaseSchema):
    """Información del destinatario"""
    recipient_id: Optional[int] = Field(None, description="ID del usuario destinatario")
    recipient_role: Optional[str] = Field(None, max_length=50, description="Rol del destinatario")


class MessageCreate(MessageBase, MessageSender, MessageRecipient):
    """Esquema para crear mensajes"""
    package_id: Optional[int] = Field(None, description="ID del paquete relacionado")
    customer_id: Optional[int] = Field(None, description="ID del cliente relacionado")
    tracking_code: Optional[str] = Field(None, max_length=50, description="Código de seguimiento")
    reference_number: Optional[str] = Field(None, max_length=100, description="Número de referencia")
    category: Optional[str] = Field(None, max_length=50, description="Categoría del mensaje")
    tags: Optional[str] = Field(None, max_length=500, description="Tags separados por comas")


class MessageUpdate(BaseSchema):
    """Esquema para actualizar mensajes"""
    status: Optional[MessageStatus] = Field(None, description="Nuevo estado del mensaje")
    is_read: Optional[bool] = Field(None, description="Marcar como leído")
    answer: Optional[str] = Field(None, max_length=2000, description="Respuesta al mensaje")
    answered_by: Optional[int] = Field(None, description="ID del usuario que responde")
    category: Optional[str] = Field(None, max_length=50, description="Categoría del mensaje")
    tags: Optional[str] = Field(None, max_length=500, description="Tags separados por comas")


class MessageResponse(IDSchema, MessageBase, MessageSender, MessageRecipient, TimestampSchema):
    """Esquema de respuesta completo para mensajes"""
    package_id: Optional[int] = None
    customer_id: Optional[int] = None
    answer: Optional[str] = Field(None, max_length=2000, description="Respuesta al mensaje")
    answered_at: Optional[datetime] = None
    answered_by: Optional[int] = None
    answered_by_name: Optional[str] = Field(None, description="Nombre del usuario que respondió")
    tracking_code: Optional[str] = None
    reference_number: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    response_time_hours: Optional[float] = None


class MessageListResponse(BaseSchema):
    """Esquema para lista de mensajes con paginación"""
    messages: List[MessageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageSearchFilters(BaseSchema):
    """Filtros para búsqueda de mensajes"""
    status: Optional[MessageStatus] = None
    message_type: Optional[MessageType] = None
    priority: Optional[MessagePriority] = None
    sender_id: Optional[int] = None
    recipient_id: Optional[int] = None
    package_id: Optional[int] = None
    customer_id: Optional[int] = None
    category: Optional[str] = None
    is_read: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_text: Optional[str] = Field(None, max_length=100, description="Texto para búsqueda general")


class MessageStats(BaseSchema):
    """Esquema para estadísticas detalladas de mensajes"""
    total_messages: int
    pending_count: int
    read_count: int
    answered_count: int
    closed_count: int
    average_response_time_hours: Optional[float] = None
    messages_by_type: dict = Field(default_factory=dict)
    messages_by_priority: dict = Field(default_factory=dict)
    messages_by_status: dict = Field(default_factory=dict)
    messages_today: int = 0
    messages_this_week: int = 0
    messages_this_month: int = 0


class MessageThread(BaseSchema):
    """Esquema para hilos de conversación"""
    thread_id: str
    messages: List[MessageResponse]
    participant_count: int
    last_message_at: datetime
    is_active: bool


class MessageNotification(BaseSchema):
    """Esquema para notificaciones de mensajes"""
    message_id: int
    recipient_id: int
    notification_type: str  # "new_message", "message_answered", "message_closed"
    title: str
    content: str
    is_read: bool = False
    created_at: datetime


class MessageAnswerRequest(BaseSchema):
    """Esquema para responder a un mensaje"""
    answer: str = Field(..., min_length=5, max_length=2000, description="Respuesta al mensaje")


class CustomerInquiryCreate(BaseSchema):
    """Esquema para crear consultas de clientes (público)"""
    customer_name: str = Field(..., min_length=2, max_length=100, description="Nombre del cliente")
    customer_phone: str = Field(..., min_length=7, max_length=20, description="Teléfono del cliente")
    customer_email: Optional[EmailStr] = Field(None, description="Email del cliente (opcional)")
    package_guide_number: str = Field(..., min_length=1, max_length=50, description="Número de guía del paquete")
    package_tracking_code: str = Field(..., min_length=1, max_length=50, description="Código de tracking del paquete")
    subject: str = Field(..., min_length=5, max_length=200, description="Asunto de la consulta")
    content: str = Field(..., min_length=10, max_length=2000, description="Contenido de la consulta")