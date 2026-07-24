# -*- coding: utf-8 -*-
"""
Servicio de dominio de registro de Persona (Seam A).

Concentra el invariante "el Teléfono es la llave universal": normaliza el
teléfono ANTES de persistir y garantiza que un mismo número —en cualquier
formato— resuelva a UNA sola Persona (registro implícito, sin duplicados).
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .persona import Persona
from .telefono import normalizar_telefono


def _buscar_por_telefono(session: Session, telefono_canonico: str):
    return (
        session.query(Persona)
        .filter(Persona.telefono == telefono_canonico)
        .one_or_none()
    )


def get_or_create_persona(session: Session, telefono: str, nombre: str) -> Persona:
    """Reutiliza la Persona del teléfono dado, o la crea si no existe.

    Normaliza el teléfono a su forma canónica antes de buscar/persistir, de modo
    que dos formatos del mismo número resuelvan a la misma Persona.

    Args:
        session: sesión de SQLAlchemy activa.
        telefono: teléfono en cualquier formato.
        nombre: nombre del residente (solo se usa al CREAR; si la Persona ya
            existe no se sobreescribe su nombre).

    Returns:
        La Persona existente o recién creada.
    """
    telefono_canonico = normalizar_telefono(telefono)

    existente = _buscar_por_telefono(session, telefono_canonico)
    if existente is not None:
        return existente

    persona = Persona(telefono=telefono_canonico, nombre=nombre)
    session.add(persona)
    try:
        session.flush()
    except IntegrityError:
        # Carrera: otra transacción creó la misma Persona; la constraint única
        # del Teléfono nos protege. Reintentar la lectura.
        session.rollback()
        encontrada = _buscar_por_telefono(session, telefono_canonico)
        if encontrada is None:
            raise
        return encontrada

    return persona
