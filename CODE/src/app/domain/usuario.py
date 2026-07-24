# -*- coding: utf-8 -*-
"""
Usuario (staff) — entidad separada de la Persona (rebuild PaqueteXv.2).

El staff que opera sobre los paquetes es una identidad distinta del residente:
tiene un `rol` (`ADMIN`/`OPERADOR`) que gobierna sus privilegios. Esta rebanada
define SOLO el esqueleto mínimo que necesitan las FK-de-actor del Paquete
(quién ejecutó cada transición). Las columnas de credencial (contraseña fuerte)
son de la rebanada de auth, NO de aquí.

UUID PK por portabilidad del D/R basado en dump/restore.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RolUsuario(str, enum.Enum):
    """Rol del staff. `str` mixin: el valor persistido ES la etiqueta."""

    ADMIN = "ADMIN"
    OPERADOR = "OPERADOR"


class Usuario(Base):
    __tablename__ = "usuarios"

    # Surrogate key propia (UUID por portabilidad del D/R basado en dump/restore).
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nombre = Column(String(120), nullable=False)

    # VARCHAR-backed (`native_enum=False`): se persiste como VARCHAR(20) sin tipo
    # ENUM nativo de Postgres (alembic compara mal los ENUM nativos y rompería el
    # guard de paridad). SQLAlchemy valida el conjunto de valores en Python.
    rol = Column(
        Enum(RolUsuario, native_enum=False, length=20), nullable=False
    )

    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} nombre={self.nombre!r} rol={self.rol}>"
