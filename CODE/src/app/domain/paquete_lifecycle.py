# -*- coding: utf-8 -*-
"""
Máquina de estados del Paquete — transiciones del ciclo de vida (Seam A).

El Paquete nace `ANUNCIADO` (ver `paquete_service.announce`). Este módulo gobierna
las transiciones posteriores, cada una registrando **quién** (el `Usuario` de la
sesión real, nunca hardcodeado) y **cuándo**:

    ANUNCIADO ──receive──▶ RECIBIDO ──deliver──▶ ENTREGADO   (terminal)
        └────────cancel────────┴─────cancel──────▶ CANCELADO (terminal)

`ENTREGADO` y `CANCELADO` son terminales: cualquier transición desde ellos se
rechaza con `TransicionInvalida`. Toda transición **valida antes de mutar**: un
rechazo deja el Paquete intacto (ni estado ni timestamps cambian).
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .paquete import EstadoPaquete, Paquete
from .usuario import Usuario


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TransicionInvalida(Exception):
    """Se intentó una transición desde un estado que no la permite.

    El Paquete queda intacto (la validación ocurre antes de cualquier mutación).
    """

    def __init__(self, estado_actual: EstadoPaquete, transicion: str):
        self.estado_actual = estado_actual
        self.transicion = transicion
        super().__init__(
            f"Transición '{transicion}' no permitida desde el estado "
            f"{getattr(estado_actual, 'value', estado_actual)}."
        )


def receive(
    session: Session,
    paquete: Paquete,
    actor: Usuario,
    guide_number: str = None,
) -> Paquete:
    """Recibe un paquete `ANUNCIADO` → `RECIBIDO`.

    Registra `received_at` (ahora) y `received_by_usuario_id` = el actor. La Guía
    del transportador es OPCIONAL (no todos la usan); si se pasa, se persiste.

    Raises:
        TransicionInvalida: si el paquete no está `ANUNCIADO` (queda intacto).
    """
    if paquete.estado is not EstadoPaquete.ANUNCIADO:
        raise TransicionInvalida(paquete.estado, "recibir")

    paquete.estado = EstadoPaquete.RECIBIDO
    paquete.received_at = _now()
    paquete.received_by_usuario_id = actor.id
    if guide_number is not None:
        paquete.guide_number = guide_number

    session.flush()
    return paquete
