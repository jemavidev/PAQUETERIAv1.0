from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from .base import Base


class PackageHistory(Base):
    """Modelo para registrar el historial de cambios de estado de los paquetes"""

    __tablename__ = "package_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    previous_status = Column(String(50), nullable=True)  # Estado anterior
    new_status = Column(String(50), nullable=False)      # Estado nuevo
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    changed_by = Column(String(100), nullable=True)      # Usuario que realizó el cambio
    additional_data = Column(JSON, nullable=True)        # Datos adicionales del cambio
    observations = Column(Text, nullable=True)           # Observaciones del cambio

    # Relación con el paquete
    # package = relationship("Package", back_populates="history")

    def __repr__(self):
        return f"<PackageHistory(id={self.id}, package_id={self.package_id}, {self.previous_status} -> {self.new_status})>"

    def to_dict(self):
        """Convertir a diccionario para serialización"""
        return {
            "id": str(self.id),
            "package_id": self.package_id,  # Integer, no necesita conversión
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
            "changed_by": self.changed_by,
            "additional_data": self.additional_data,
            "observations": self.observations
        }