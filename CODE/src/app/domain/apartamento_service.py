# -*- coding: utf-8 -*-
"""
Servicio de dominio de Apartamento y membresía actual (Seam A).

Dos invariantes del dominio:

  1. **Dedup por terna** — un Apartamento se identifica por su terna normalizada
     `(conjunto, torre, apartamento)`; escribir la misma unidad (en cualquier
     casing/espaciado) reutiliza la existente en lugar de duplicarla
     (get-or-create, "creable sobre la marcha").
  2. **Membresía mutable** — la Persona tiene UN Apartamento actual opcional;
     asignarlo/mudarlo/desvincularlo siempre está disponible y resuelve la
     Persona por su Teléfono canónico (igual que `get_or_create_persona`).
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .apartamento import Apartamento, normalizar_terna
from .persona import Persona
from .telefono import normalizar_telefono


def _buscar_por_terna(
    session: Session, conjunto: str, torre: str, apartamento: str
):
    return (
        session.query(Apartamento)
        .filter(
            Apartamento.conjunto == conjunto,
            Apartamento.torre == torre,
            Apartamento.apartamento == apartamento,
        )
        .one_or_none()
    )


def get_or_create_apartamento(
    session: Session, conjunto: str, torre: str, apartamento: str
) -> Apartamento:
    """Reutiliza el Apartamento de la terna dada, o lo crea si no existe.

    Normaliza la terna a su forma canónica antes de buscar/persistir, de modo que
    dos escrituras de la misma unidad (distinto casing/espaciado) resuelvan al
    mismo Apartamento.

    Args:
        session: sesión de SQLAlchemy activa.
        conjunto: nombre del conjunto residencial.
        torre: identificador de la torre/bloque.
        apartamento: identificador del apartamento/unidad.

    Returns:
        El Apartamento existente o recién creado.

    Raises:
        ValueError: si algún componente de la terna es ``None`` o queda vacío.
    """
    conjunto_c, torre_c, apartamento_c = normalizar_terna(conjunto, torre, apartamento)

    existente = _buscar_por_terna(session, conjunto_c, torre_c, apartamento_c)
    if existente is not None:
        return existente

    apto = Apartamento(conjunto=conjunto_c, torre=torre_c, apartamento=apartamento_c)
    session.add(apto)
    try:
        session.flush()
    except IntegrityError:
        # Carrera: otra transacción creó la misma terna; la constraint única nos
        # protege. Reintentar la lectura.
        session.rollback()
        encontrado = _buscar_por_terna(session, conjunto_c, torre_c, apartamento_c)
        if encontrado is None:
            raise
        return encontrado

    return apto


def set_apartamento_actual(
    session: Session, telefono: str, apartamento: Apartamento | None
) -> Persona:
    """Asigna (o desvincula) el Apartamento actual de una Persona.

    Resuelve la Persona por su Teléfono canónico (igual que
    `get_or_create_persona`). NO crea la Persona: este servicio no recibe nombre,
    de modo que la Persona debe existir previamente.

    Args:
        session: sesión de SQLAlchemy activa.
        telefono: teléfono de la Persona, en cualquier formato.
        apartamento: el Apartamento a asignar, o ``None`` para desvincular.

    Returns:
        La Persona con su `apartamento_actual_id` actualizado.

    Raises:
        LookupError: si no existe una Persona con ese Teléfono.
        ValueError: si el teléfono es ``None`` o no contiene dígitos.
    """
    telefono_canonico = normalizar_telefono(telefono)

    persona = (
        session.query(Persona)
        .filter(Persona.telefono == telefono_canonico)
        .one_or_none()
    )
    if persona is None:
        raise LookupError(
            f"No existe una Persona con el teléfono {telefono_canonico!r}; "
            "regístrela primero (get_or_create_persona)."
        )

    persona.apartamento_actual_id = apartamento.id if apartamento is not None else None
    session.flush()
    return persona
