# -*- coding: utf-8 -*-
"""
PAQUETES EL CLUB v4.0 - Modelo Base
Versión: 1.0.0
Fecha: 2025-01-24
Autor: Equipo de Desarrollo
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def get_colombia_now():
    """
    Obtener la fecha y hora actual en zona horaria de Colombia (UTC-5)
    """
    # Colombia está en UTC-5
    colombia_offset = timezone(timedelta(hours=-5))
    return datetime.now(colombia_offset)

class BaseModel(Base):
    """
    Modelo base con campos comunes para todos los modelos
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), default=get_colombia_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_colombia_now, onupdate=get_colombia_now, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
