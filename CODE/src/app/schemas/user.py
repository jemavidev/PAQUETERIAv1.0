# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v1.0 - Esquemas de Usuario
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

from .base import BaseSchema, TimestampSchema, IDSchema


class UserRole(str, Enum):
    """Roles de usuario disponibles"""
    ADMIN = "ADMIN"
    OPERADOR = "OPERADOR"
    USUARIO = "USUARIO"


class UserBase(BaseSchema):
    """Esquema base para usuarios"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: EmailStr = Field(..., description="Email único del usuario")
    full_name: str = Field(..., min_length=2, max_length=100, description="Nombre completo")
    role: UserRole = Field(default=UserRole.OPERADOR, description="Rol del usuario")
    is_active: bool = Field(default=True, description="Estado activo del usuario")
    phone: Optional[str] = Field(None, pattern=r'^\+57\s?\d{3}\s?\d{3}\s?\d{4}$', description="Número de teléfono colombiano")


class UserCreate(UserBase):
    """Esquema para crear usuarios"""
    password: str = Field(..., min_length=8, max_length=255, description="Contraseña del usuario")

    @validator('password')
    def password_strength(cls, v):
        """Valida la fortaleza de la contraseña"""
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        return v


class UserUpdate(BaseSchema):
    """Esquema para actualizar usuarios"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = Field(None, pattern=r'^\+57\s?\d{3}\s?\d{3}\s?\d{4}$')
    password: Optional[str] = Field(None, min_length=8, max_length=255)


class UserResponse(IDSchema, UserBase, TimestampSchema):
    """Esquema de respuesta para usuarios"""
    pass


class UserLogin(BaseSchema):
    """Esquema para login de usuarios"""
    username: str = Field(..., description="Nombre de usuario o email")
    password: str = Field(..., description="Contraseña")


class TokenResponse(BaseSchema):
    """Esquema de respuesta para tokens JWT"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class PasswordResetRequest(BaseSchema):
    """Esquema para solicitud de reset de contraseña"""
    email: EmailStr


class PasswordResetTokenResponse(BaseSchema):
    """Esquema de respuesta para token de reset"""
    message: str
    reset_token: str


class PasswordResetConfirm(BaseSchema):
    """Esquema para confirmar reset de contraseña"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=255)

    @validator('new_password')
    def password_strength(cls, v):
        """Valida la fortaleza de la contraseña"""
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        return v