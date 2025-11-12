# ========================================
# PAQUETES EL CLUB v4.0 - Modelo de Tarifas
# ========================================

import enum
from sqlalchemy import Column, String, Numeric, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base
from ..utils.datetime_utils import get_colombia_now

class RateType(str, enum.Enum):
    """Tipos de tarifa"""
    STORAGE = "storage"
    DELIVERY = "delivery"
    PACKAGE_TYPE = "package_type"

class Rate(Base):
    """Modelo de tarifas"""
    __tablename__ = "rates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rate_type = Column(Enum(RateType), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    daily_storage_rate = Column(Numeric(10, 2), default=0, nullable=False)
    delivery_rate = Column(Numeric(10, 2), default=0, nullable=False)
    package_type_multiplier = Column(Numeric(10, 2), default=1.0, nullable=False)

    # Control de versiones
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    valid_from = Column(DateTime, default=get_colombia_now, nullable=False)
    valid_to = Column(DateTime, nullable=True)

    # Metadata
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relaciones
    created_by = relationship("User", foreign_keys=[created_by_id], backref="created_rates")
    updated_by = relationship("User", foreign_keys=[updated_by_id], backref="updated_rates")

    def __repr__(self):
        return f"<Rate {self.rate_type.value} - {self.name}: ${self.base_price}>"

    @property
    def is_currently_active(self) -> bool:
        """Verificar si la tarifa está actualmente activa"""
        now = get_colombia_now()
        return (
            self.is_active and
            self.valid_from <= now and
            (self.valid_to is None or self.valid_to > now)
        )

    def deactivate(self):
        """Desactivar la tarifa"""
        self.is_active = False
        self.valid_to = get_colombia_now()

    def activate(self):
        """Activar la tarifa"""
        self.is_active = True
        if not self.valid_from:
            self.valid_from = get_colombia_now()
        self.valid_to = None