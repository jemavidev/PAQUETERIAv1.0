# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Esquemas Pydantic
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from .base import BaseSchema
from .user import UserCreate, UserUpdate, UserResponse, UserLogin
from .customer import CustomerCreate, CustomerUpdate, CustomerResponse
from .package import PackageCreate, PackageUpdate, PackageResponse, PackageStatusUpdate
from .message import MessageCreate, MessageResponse, MessageAnswerRequest
from .notification import NotificationResponse
from .file_upload import FileUploadResponse

__all__ = [
    "BaseSchema",
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin",
    "CustomerCreate", "CustomerUpdate", "CustomerResponse",
    "PackageCreate", "PackageUpdate", "PackageResponse", "PackageStatusUpdate",
    "MessageCreate", "MessageResponse", "MessageAnswerRequest",
    "NotificationResponse",
    "FileUploadResponse"
]