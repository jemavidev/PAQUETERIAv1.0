# ========================================
# PAQUETES EL CLUB v1.0 - Modelo Nuevo de Anuncio
# ========================================

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base
from app.utils.datetime_utils import get_colombia_now

class PackageAnnouncementNew(Base):
    """Modelo nuevo para anuncios de paquetes"""
    __tablename__ = "package_announcements_new"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    guide_number = Column(String(50), unique=True, nullable=False, index=True)
    tracking_code = Column(String(10), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)
    announced_at = Column(DateTime, default=get_colombia_now, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=get_colombia_now, nullable=False)
    updated_at = Column(DateTime, default=get_colombia_now, onupdate=get_colombia_now, nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relaciones
    customer = relationship("Customer", back_populates="announcements")
    package = relationship("Package", back_populates="announcements")
    created_by = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self):
        return f"<PackageAnnouncementNew {self.guide_number} - {self.customer_name}>"

    @property
    def status(self):
        """Estado del anuncio"""
        if not self.is_active:
            return "inactivo"
        elif self.is_processed:
            return "recibido"
        else:
            return "pendiente"