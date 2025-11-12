# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Esquema Base Pydantic
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Esquema base con configuración común para todos los esquemas Pydantic
    """
    model_config = ConfigDict(
        from_attributes=True,  # Permite crear esquemas desde objetos SQLAlchemy
        validate_assignment=True,  # Valida asignaciones
        str_strip_whitespace=True,  # Elimina espacios en blanco en strings
        json_encoders={
            datetime: lambda v: v.isoformat()  # Formato ISO para fechas
        }
    )


class TimestampSchema(BaseSchema):
    """
    Esquema con campos de timestamp
    """
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IDSchema(BaseSchema):
    """
    Esquema con campo ID
    """
    id: int