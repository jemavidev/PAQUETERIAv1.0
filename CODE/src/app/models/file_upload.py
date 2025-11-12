# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Modelo de Archivo
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from sqlalchemy import Column, Integer, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class FileType(enum.Enum):
    IMAGEN = "IMAGEN"
    DOCUMENTO = "DOCUMENTO"
    RECIBO = "RECIBO"

class FileUpload(BaseModel):
    """
    Modelo de archivo subido
    """
    __tablename__ = "file_uploads"
    
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=True)
    s3_url = Column(String(500), nullable=True)
    file_type = Column(Enum(FileType), nullable=False)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)
    
    # Relaciones
    package = relationship("Package", back_populates="file_uploads")
    
    def __repr__(self):
        return f"<FileUpload(id={self.id}, filename='{self.filename}', type='{self.file_type.value}')>"
