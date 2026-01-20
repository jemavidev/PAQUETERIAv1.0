"""
Modelo para gestión de códigos CUFE
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class CufeStatus(str, enum.Enum):
    """Estados del proceso de importación de CUFE"""
    PENDING = "pending"           # Registrado, esperando descarga
    DOWNLOADING = "downloading"   # En proceso de descarga desde DIAN
    DOWNLOADED = "downloaded"     # PDF descargado, esperando procesamiento
    PROCESSING = "processing"     # Procesando PDF
    PROCESSED = "processed"       # Completado exitosamente
    ERROR = "error"              # Error en el proceso


class CufeRecord(Base):
    """
    Registro de códigos CUFE para importación desde DIAN
    """
    __tablename__ = "cufe_records"
    
    id = Column(Integer, primary_key=True, index=True)
    cufe = Column(String(96), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(CufeStatus, values_callable=lambda x: [e.value for e in x]), default=CufeStatus.PENDING, nullable=False)
    
    # Información extraída
    supplier_name = Column(String(255), nullable=True)
    invoice_number = Column(String(100), nullable=True)
    
    # Relación con factura procesada
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    invoice = relationship("Invoice", foreign_keys=[invoice_id])
    
    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Manejo de errores
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relaciones
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<CufeRecord(id={self.id}, cufe={self.cufe[:20]}..., status={self.status})>"
    
    @property
    def dian_url(self):
        """URL para consultar en la DIAN"""
        return f"https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={self.cufe}"
