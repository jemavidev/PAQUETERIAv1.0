# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Modelo de Cliente Expandido
Versión: 2.0.0
Fecha: 2025-09-21
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base
from app.utils.datetime_utils import get_colombia_now

class Customer(Base):
    """
    Modelo expandido de cliente con múltiples teléfonos, emails y direcciones
    """
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False, index=True)
    last_name = Column(String(50), nullable=False, index=True)
    full_name = Column(String(100), nullable=False, index=True)  # Para búsquedas

    # Información de contacto principal
    phone = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=True, index=True)

    # Información adicional
    document_type = Column(String(10), nullable=True)  # CC, CE, NIT, etc.
    document_number = Column(String(20), nullable=True, unique=True, index=True)
    birth_date = Column(DateTime, nullable=True)

    # Dirección principal
    address_street = Column(String(100), nullable=True)
    address_city = Column(String(50), nullable=True)
    address_state = Column(String(50), nullable=True)
    address_zip = Column(String(10), nullable=True)
    address_country = Column(String(50), default="Colombia", nullable=False)

    # Información específica del edificio
    building_name = Column(String(100), nullable=True)
    tower = Column(String(10), nullable=True)
    apartment = Column(String(10), nullable=True)
    floor = Column(String(10), nullable=True)

    # Información adicional
    notes = Column(Text, nullable=True)
    preferred_language = Column(String(10), default="es", nullable=False)  # es, en

    # Estado y control
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_vip = Column(Boolean, default=False, nullable=False, index=True)
    total_packages_received = Column(Integer, default=0, nullable=False)
    total_packages_delivered = Column(Integer, default=0, nullable=False)
    total_spent = Column(Integer, default=0, nullable=False)  # En centavos

    # Metadata
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=get_colombia_now, nullable=False)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now, nullable=False)

    # Relaciones
    packages = relationship("Package", back_populates="customer", cascade="all, delete-orphan")
    announcements = relationship("PackageAnnouncementNew", back_populates="customer", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="customer", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="customer", cascade="all, delete-orphan")
    created_by = relationship("User", foreign_keys=[created_by_id])
    updated_by = relationship("User", foreign_keys=[updated_by_id])

    # Propiedades calculadas
    @property
    def display_name(self) -> str:
        """Nombre para mostrar"""
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self) -> str:
        """Dirección completa formateada"""
        parts = []
        if self.address_street:
            parts.append(self.address_street)
        if self.building_name:
            parts.append(f"Edificio {self.building_name}")
        if self.tower and self.apartment:
            parts.append(f"Torre {self.tower}, Apt {self.apartment}")
        elif self.tower:
            parts.append(f"Torre {self.tower}")
        elif self.apartment:
            parts.append(f"Apt {self.apartment}")
        if self.address_city:
            parts.append(self.address_city)
        if self.address_state:
            parts.append(self.address_state)
        return ", ".join(parts) if parts else "Dirección no especificada"

    @property
    def contact_info(self) -> dict:
        """Información de contacto resumida"""
        return {
            "phone": self.phone,
            "email": self.email,
            "full_address": self.full_address
        }

    @property
    def package_stats(self) -> dict:
        """Estadísticas de paquetes"""
        return {
            "total_received": self.total_packages_received,
            "total_delivered": self.total_packages_delivered,
            "pending_delivery": self.total_packages_received - self.total_packages_delivered,
            "total_spent_cop": self.total_spent / 100  # Convertir de centavos a pesos
        }

    def update_package_counts(self):
        """Actualizar contadores de paquetes"""
        from .package import Package, PackageStatus

        self.total_packages_received = len([p for p in self.packages if p.status in [PackageStatus.RECIBIDO, PackageStatus.ENTREGADO]])
        self.total_packages_delivered = len([p for p in self.packages if p.status == PackageStatus.ENTREGADO])

        # Calcular gasto total
        delivered_packages = [p for p in self.packages if p.status == PackageStatus.ENTREGADO]
        self.total_spent = sum(getattr(p, 'total_cost_cents', 0) for p in delivered_packages)

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.display_name}', phone='{self.phone}', active={self.is_active})>"
