# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Modelo de Preferencias de Cliente
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
import secrets


class CustomerPreferences(BaseModel):
    """
    Modelo para almacenar preferencias de notificaciones de clientes
    Los clientes NO tienen cuenta de usuario, pero pueden gestionar
    sus preferencias usando un token único.
    """
    __tablename__ = "customer_preferences"
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Token único para acceso sin login
    token = Column(String(64), unique=True, nullable=False, index=True)
    
    # Notificaciones por tipo
    sms_notifications_enabled = Column(Boolean, default=True, nullable=False)
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    
    # Notificaciones por evento
    notify_package_received = Column(Boolean, default=True, nullable=False)
    notify_package_delivered = Column(Boolean, default=True, nullable=False)
    notify_package_announced = Column(Boolean, default=True, nullable=False)
    notify_payment_due = Column(Boolean, default=True, nullable=False)
    
    # Marketing (desactivado por defecto)
    marketing_enabled = Column(Boolean, default=False, nullable=False)
    
    # Relación
    customer = relationship("Customer", backref="preferences")
    
    @staticmethod
    def generate_token() -> str:
        """Genera un token único seguro"""
        return secrets.token_urlsafe(48)
    
    def should_send_notification(self, notification_type: str, event_type: str) -> bool:
        """
        Verifica si se debe enviar una notificación según las preferencias del cliente
        
        Args:
            notification_type: Tipo de notificación (SMS, EMAIL, etc.)
            event_type: Tipo de evento (PACKAGE_RECEIVED, etc.)
        
        Returns:
            bool: True si se debe enviar, False si está desactivado
        """
        from app.models.notification import NotificationType, NotificationEvent
        
        # Eventos críticos siempre se envían (aunque el cliente los desactive)
        CRITICAL_EVENTS = [
            NotificationEvent.SECURITY_ALERT,
            NotificationEvent.LEGAL_NOTICE,
        ]
        
        if event_type in CRITICAL_EVENTS:
            return True
        
        # Verificar preferencia general por tipo
        if notification_type == NotificationType.SMS:
            if not self.sms_notifications_enabled:
                return False
        elif notification_type == NotificationType.EMAIL:
            if not self.email_notifications_enabled:
                return False
        
        # Verificar preferencia específica por evento
        if event_type == NotificationEvent.PACKAGE_RECEIVED:
            return self.notify_package_received
        elif event_type == NotificationEvent.PACKAGE_DELIVERED:
            return self.notify_package_delivered
        elif event_type == NotificationEvent.PACKAGE_ANNOUNCED:
            return self.notify_package_announced
        elif event_type == NotificationEvent.PAYMENT_DUE:
            return self.notify_payment_due
        elif event_type == NotificationEvent.MARKETING:
            return self.marketing_enabled
        
        # Por defecto, permitir otras notificaciones
        return True
    
    def to_dict(self) -> dict:
        """Convertir preferencias a diccionario"""
        return {
            "sms_notifications_enabled": self.sms_notifications_enabled,
            "email_notifications_enabled": self.email_notifications_enabled,
            "notify_package_received": self.notify_package_received,
            "notify_package_delivered": self.notify_package_delivered,
            "notify_package_announced": self.notify_package_announced,
            "notify_payment_due": self.notify_payment_due,
            "marketing_enabled": self.marketing_enabled
        }
    
    def __repr__(self):
        return f"<CustomerPreferences(customer_id={self.customer_id}, token='{self.token[:10]}...')>"
