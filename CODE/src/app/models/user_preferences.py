# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Modelo de Preferencias de Usuario
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel
import json

class UserPreferences(BaseModel):
    """
    Modelo para almacenar preferencias de configuración del usuario
    """
    __tablename__ = "user_preferences"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Notificaciones
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    push_notifications_enabled = Column(Boolean, default=False, nullable=False)
    sms_notifications_enabled = Column(Boolean, default=False, nullable=False)
    notify_package_received = Column(Boolean, default=True, nullable=False)
    notify_package_delivered = Column(Boolean, default=True, nullable=False)
    notify_messages = Column(Boolean, default=True, nullable=False)
    
    # Privacidad
    profile_public = Column(Boolean, default=True, nullable=False)
    share_activity_data = Column(Boolean, default=False, nullable=False)
    
    # Interfaz
    theme = Column(String(20), default="light", nullable=False)  # light, dark, auto
    language = Column(String(10), default="es", nullable=False)  # es, en
    items_per_page = Column(String(10), default="20", nullable=False)  # 10, 20, 50, 100
    
    # Dashboard
    show_statistics = Column(Boolean, default=True, nullable=False)
    show_recent_activity = Column(Boolean, default=True, nullable=False)
    show_charts = Column(Boolean, default=True, nullable=False)
    
    # Preferencias adicionales en JSON
    additional_preferences = Column(JSON, default=dict, nullable=True)
    
    # Relación
    user = relationship("User", backref="preferences")
    
    def to_dict(self) -> dict:
        """Convertir preferencias a diccionario"""
        return {
            "email_notifications_enabled": self.email_notifications_enabled,
            "push_notifications_enabled": self.push_notifications_enabled,
            "sms_notifications_enabled": self.sms_notifications_enabled,
            "notify_package_received": self.notify_package_received,
            "notify_package_delivered": self.notify_package_delivered,
            "notify_messages": self.notify_messages,
            "profile_public": self.profile_public,
            "share_activity_data": self.share_activity_data,
            "theme": self.theme,
            "language": self.language,
            "items_per_page": self.items_per_page,
            "show_statistics": self.show_statistics,
            "show_recent_activity": self.show_recent_activity,
            "show_charts": self.show_charts,
            "additional_preferences": self.additional_preferences or {}
        }
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, theme='{self.theme}')>"

