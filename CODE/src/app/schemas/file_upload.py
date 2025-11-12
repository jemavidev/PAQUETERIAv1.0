# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Esquemas de File Upload
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

from .base import BaseSchema, TimestampSchema, IDSchema


class FileType(str, Enum):
    """Tipos de archivo permitidos"""
    IMAGEN = "IMAGEN"
    DOCUMENTO = "DOCUMENTO"
    RECIBO = "RECIBO"


class FileUploadBase(BaseSchema):
    """Esquema base para file uploads"""
    filename: str = Field(..., max_length=255, description="Nombre original del archivo")
    file_path: str = Field(..., max_length=500, description="Ruta del archivo en el servidor")
    file_type: FileType = Field(..., description="Tipo de archivo")
    file_size: int = Field(..., description="Tamaño del archivo en bytes")
    mime_type: str = Field(..., max_length=100, description="Tipo MIME del archivo")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del archivo")


class FileUploadCreate(FileUploadBase):
    """Esquema para crear file uploads"""
    package_id: int = Field(..., description="ID del paquete relacionado")


class FileUploadResponse(IDSchema, FileUploadBase, TimestampSchema):
    """Esquema de respuesta para file uploads"""
    package_id: int
    uploaded_by: int


class FileUploadStats(BaseSchema):
    """Esquema para estadísticas de file uploads"""
    total_files: int
    total_size: int  # en bytes
    images_count: int
    documents_count: int
    receipts_count: int