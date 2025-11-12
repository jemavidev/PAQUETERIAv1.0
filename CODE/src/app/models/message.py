# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Modelo de Mensaje Expandido
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, Integer, ForeignKey, Text, Enum, DateTime, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class MessageStatus(enum.Enum):
    """Estados de los mensajes"""
    ABIERTO = "ABIERTO"
    LEIDO = "LEIDO"
    RESPONDIDO = "RESPONDIDO"
    CERRADO = "CERRADO"

class MessageType(enum.Enum):
    """Tipos de mensaje"""
    CONSULTA = "CONSULTA"
    MENSAJE_OPERADOR = "MENSAJE_OPERADOR"
    NOTIFICACION_SISTEMA = "NOTIFICACION_SISTEMA"
    ACTUALIZACION_ESTADO = "ACTUALIZACION_ESTADO"

class MessagePriority(enum.Enum):
    """Prioridad de los mensajes"""
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"

class Message(BaseModel):
    """
    Modelo expandido de mensaje para sistema completo de mensajería
    """
    __tablename__ = "messages"

    # Información básica
    subject = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.CONSULTA, nullable=False)
    priority = Column(Enum(MessagePriority), default=MessagePriority.MEDIA, nullable=False)

    # Estados y seguimiento
    status = Column(Enum(MessageStatus), default=MessageStatus.ABIERTO, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    # Relaciones con paquetes y clientes
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)

    # Información del remitente
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Usuario que envía
    sender_name = Column(String(100), nullable=True)  # Nombre del remitente (para clientes externos)
    sender_email = Column(String(100), nullable=True)
    sender_phone = Column(String(20), nullable=True)

    # Información del destinatario
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Usuario destinatario
    recipient_role = Column(String(50), nullable=True)  # Rol del destinatario (admin, operator, etc.)

    # Respuesta y seguimiento
    answer = Column(Text, nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    answered_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Metadatos adicionales
    tracking_code = Column(String(50), nullable=True)  # Para asociar con paquetes
    reference_number = Column(String(100), nullable=True)  # Número de referencia externo

    # Categorización
    category = Column(String(50), nullable=True)  # Categoría del mensaje
    tags = Column(Text, nullable=True)  # Tags separados por comas

    # Relaciones
    package = relationship("Package", back_populates="messages")
    customer = relationship("Customer", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="messages_received")
    answered_by_user = relationship("User", foreign_keys=[answered_by], back_populates="messages_answered")

    def __repr__(self):
        return f"<Message(id={self.id}, type='{self.message_type.value}', status='{self.status.value}', priority='{self.priority.value}')>"

    @property
    def is_pending(self) -> bool:
        """Verificar si el mensaje está pendiente"""
        return self.status == MessageStatus.ABIERTO

    @property
    def is_answered(self) -> bool:
        """Verificar si el mensaje ha sido respondido"""
        return self.status == MessageStatus.RESPONDIDO

    @property
    def is_closed(self) -> bool:
        """Verificar si el mensaje está cerrado"""
        return self.status == MessageStatus.CERRADO

    @property
    def response_time_hours(self) -> float:
        """Calcular tiempo de respuesta en horas"""
        if self.answered_at and self.created_at:
            return (self.answered_at - self.created_at).total_seconds() / 3600
        return 0.0
