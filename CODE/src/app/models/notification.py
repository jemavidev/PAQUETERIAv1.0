# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Modelo de Notificación Expandido
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, String, Text, Enum, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from src.app.utils.datetime_utils import get_colombia_now
import enum
import uuid

class NotificationType(enum.Enum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    PUSH = "push"

class NotificationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NotificationPriority(enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"

class NotificationEvent(enum.Enum):
    PACKAGE_ANNOUNCED = "package_announced"
    PACKAGE_RECEIVED = "package_received"
    PACKAGE_DELIVERED = "package_delivered"
    PACKAGE_CANCELLED = "package_cancelled"
    PAYMENT_DUE = "payment_due"
    CUSTOM_MESSAGE = "custom_message"

class Notification(Base):
    """
    Modelo expandido de notificación con soporte completo para SMS y otros canales
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    announcement_id = Column(UUID(as_uuid=True), ForeignKey("package_announcements_new.id"), nullable=True)

    notification_type = Column(Enum(NotificationType), nullable=False)
    event_type = Column(Enum(NotificationEvent), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIA, nullable=False)

    recipient = Column(String(100), nullable=False)  # Puede ser teléfono, email, etc.
    recipient_name = Column(String(100), nullable=True)
    subject = Column(String(200), nullable=True)  # Para emails
    message = Column(Text, nullable=False)
    message_template = Column(String(100), nullable=True)  # ID de plantilla usada

    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)

    # Metadatos del proveedor
    provider_id = Column(String(100), nullable=True)  # ID del mensaje en el proveedor
    provider_response = Column(Text, nullable=True)  # Respuesta completa del proveedor
    cost_cents = Column(Integer, default=0, nullable=False)  # Costo en centavos

    # Control de reintentos
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    next_retry_at = Column(DateTime, nullable=True)

    # Configuración adicional
    is_scheduled = Column(Boolean, default=False, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    is_test = Column(Boolean, default=False, nullable=False)

    # Metadata
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=get_colombia_now, nullable=False)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now, nullable=False)

    # Relaciones
    package = relationship("Package", back_populates="notifications")
    customer = relationship("Customer", back_populates="notifications")
    announcement = relationship("PackageAnnouncementNew", foreign_keys=[announcement_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])

    @property
    def is_successful(self) -> bool:
        """Verifica si la notificación fue exitosa"""
        return self.status in [NotificationStatus.SENT, NotificationStatus.ENTREGADO]

    @property
    def can_retry(self) -> bool:
        """Verifica si se puede reintentar el envío"""
        return (self.status == NotificationStatus.FAILED and
                self.retry_count < self.max_retries and
                not self.is_test)

    def mark_as_sent(self, provider_id: str = None, cost_cents: int = 0):
        """Marca la notificación como enviada"""
        self.status = NotificationStatus.SENT
        self.sent_at = get_colombia_now()
        self.provider_id = provider_id
        self.cost_cents = cost_cents

    def mark_as_delivered(self):
        """Marca la notificación como entregada"""
        self.status = NotificationStatus.ENTREGADO
        self.delivered_at = get_colombia_now()

    def mark_as_failed(self, error_message: str, error_code: str = None):
        """Marca la notificación como fallida"""
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.error_code = error_code
        self.retry_count += 1

        # Programar próximo reintento si es posible
        if self.can_retry:
            # Reintento exponencial: 5min, 30min, 2h
            delays = [300, 1800, 7200]  # segundos
            if self.retry_count <= len(delays):
                from datetime import timedelta
                self.next_retry_at = get_colombia_now() + timedelta(seconds=delays[self.retry_count - 1])

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type.value}', event='{self.event_type.value}', status='{self.status.value}')>"

# Modelo para plantillas de mensajes SMS
class SMSMessageTemplate(Base):
    """
    Plantillas predefinidas para mensajes SMS
    """
    __tablename__ = "sms_message_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(String(50), unique=True, nullable=False)  # ID único de la plantilla
    name = Column(String(100), nullable=False)
    event_type = Column(Enum(NotificationEvent), nullable=False)
    language = Column(String(10), default="es", nullable=False)  # es, en

    subject = Column(String(200), nullable=True)  # Para emails
    message_template = Column(Text, nullable=False)  # Plantilla con placeholders
    description = Column(Text, nullable=True)

    # Variables disponibles en la plantilla
    available_variables = Column(Text, nullable=True)  # JSON string con variables disponibles

    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # Plantilla por defecto para el evento

    # Metadata
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=get_colombia_now, nullable=False)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now, nullable=False)

    # Relaciones
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])

    def render_message(self, variables: dict) -> str:
        """Renderiza la plantilla con las variables proporcionadas"""
        message = self.message_template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            message = message.replace(placeholder, str(value))
        return message

    def __repr__(self):
        return f"<SMSMessageTemplate(id='{self.template_id}', name='{self.name}', event='{self.event_type.value}')>"

# Modelo para configuración SMS
class SMSConfiguration(Base):
    """
    Configuración global del servicio SMS
    """
    __tablename__ = "sms_configuration"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider = Column(String(50), default="liwa", nullable=False)  # liwa, twilio, etc.

    # Configuración del proveedor
    api_key = Column(String(255), nullable=True)
    account_id = Column(String(100), nullable=True)
    password = Column(String(255), nullable=True)
    auth_url = Column(String(255), nullable=True)
    api_url = Column(String(255), nullable=True)

    # Configuración de envío
    default_sender = Column(String(20), default="PAQUETES", nullable=False)
    max_message_length = Column(Integer, default=160, nullable=False)
    enable_delivery_reports = Column(Boolean, default=True, nullable=False)
    enable_test_mode = Column(Boolean, default=False, nullable=False)

    # Límites y costos
    daily_limit = Column(Integer, default=1000, nullable=False)
    monthly_limit = Column(Integer, default=30000, nullable=False)
    cost_per_sms_cents = Column(Integer, default=50, nullable=False)  # Costo por SMS en centavos

    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    last_test_at = Column(DateTime, nullable=True)
    last_test_result = Column(Text, nullable=True)

    # Metadata
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=get_colombia_now, nullable=False)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now, nullable=False)

    # Relaciones
    updated_by = relationship("User", foreign_keys=[updated_by_id])

    def __repr__(self):
        return f"<SMSConfiguration(provider='{self.provider}', active={self.is_active})>"
