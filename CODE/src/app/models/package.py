# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Modelo de Paquete
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base
from app.utils.datetime_utils import get_colombia_now
from decimal import Decimal
import enum
import uuid

class PackageType(enum.Enum):
    NORMAL = "NORMAL"
    EXTRA_DIMENSIONADO = "EXTRA_DIMENSIONADO"

class PackageStatus(enum.Enum):
    ANUNCIADO = "ANUNCIADO"
    CANCELADO = "CANCELADO"
    RECIBIDO = "RECIBIDO"
    ENTREGADO = "ENTREGADO"

class PackageCondition(enum.Enum):
    BUENO = "BUENO"
    ABIERTO = "ABIERTO"
    REGULAR = "REGULAR"

class Package(Base):
    """
    Modelo de paquete principal
    """
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    
    package_type = Column(Enum(PackageType), default=PackageType.NORMAL, nullable=False)
    status = Column(Enum(PackageStatus), default=PackageStatus.ANUNCIADO, nullable=False)
    package_condition = Column(Enum(PackageCondition), default=PackageCondition.BUENO, nullable=False)
    
    access_code = Column(String(20), unique=True, nullable=False)
    guide_number = Column(String(50), unique=True, nullable=True, index=True)  # Número de guía del transportador
    posicion = Column(String(2), unique=True, nullable=True)  # Posición física 00-99
    
    announced_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    base_fee = Column(Numeric(10, 2), default=1500.00, nullable=False)  # Se calcula dinámicamente según tipo
    storage_fee = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=get_colombia_now, nullable=False)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now, nullable=False)

    # Relaciones
    customer = relationship("Customer", back_populates="packages")
    creator = relationship("User", foreign_keys=[created_by], back_populates="packages_created")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="packages_updated")
    messages = relationship("Message", back_populates="package")
    file_uploads = relationship("FileUpload", back_populates="package")
    notifications = relationship("Notification", back_populates="package")
    announcements = relationship("PackageAnnouncementNew", back_populates="package", viewonly=True)  # Solo lectura para evitar problemas de cascada

    @property
    def total_cost_cents(self) -> int:
        """Costo total en centavos"""
        return int((self.base_fee + self.storage_fee) * 100)

    def calculate_correct_base_fee(self) -> Decimal:
        """Calcular la tarifa base correcta según el tipo de paquete"""
        from app.config import settings
        
        if self.package_type == PackageType.NORMAL:
            return Decimal(str(settings.base_delivery_rate_normal))
        elif self.package_type == PackageType.EXTRA_DIMENSIONED:
            return Decimal(str(settings.base_delivery_rate_extra_dimensioned))
        else:
            return Decimal(str(settings.base_delivery_rate_normal))

    def update_fees_if_needed(self):
        """Actualizar tarifas si no coinciden con el tipo de paquete"""
        correct_base_fee = self.calculate_correct_base_fee()
        
        if self.base_fee != correct_base_fee:
            self.base_fee = correct_base_fee
            self.total_amount = self.base_fee + self.storage_fee
            return True  # Indica que se actualizó
        return False  # No se actualizó

    def __repr__(self):
        return f"<Package(id={self.id}, tracking='{self.tracking_number}', status='{self.status.value}')>"
