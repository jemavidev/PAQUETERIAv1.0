# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Modelo de Usuario
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    OPERADOR = "OPERADOR"
    USUARIO = "USUARIO"

class User(BaseModel):
    """
    Modelo de usuario para personal administrativo
    """
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.OPERADOR, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    packages_created = relationship("Package", foreign_keys="Package.created_by", back_populates="creator")
    packages_updated = relationship("Package", foreign_keys="Package.updated_by", back_populates="updater")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")
    messages_answered = relationship("Message", foreign_keys="Message.answered_by", back_populates="answered_by_user")
    
    # Relaciones de reportes (alineadas con created_by en modelos de reportes)
    reports = relationship("Report", back_populates="created_by")
    report_templates = relationship("ReportTemplate", back_populates="created_by")
    # dashboard_metrics removida: no existe FK users -> dashboard_metrics
    report_schedules = relationship("ReportSchedule", back_populates="created_by")
    
    @property
    def is_admin(self) -> bool:
        """Verificar si el usuario es administrador"""
        return self.role == UserRole.ADMIN

    @property
    def is_operator(self) -> bool:
        """Verificar si el usuario es operador"""
        return self.role == UserRole.OPERADOR

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"
