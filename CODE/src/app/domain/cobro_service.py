# -*- coding: utf-8 -*-
"""
Servicio de dominio de `Cobro` -- cálculo y registro del cobro por recepción
de un paquete (módulo "Gestión de cobro y bodegaje", `.scratch/cobro-bodegaje`).

`calcular_cobro` es una función PURA: no toca la base de datos, solo resuelve
el desglose a partir de datos ya cargados (`Paquete`, `TarifaCobro`, un
instante "ahora" explícito, y si es primera entrega ya resuelto por el
caller vía `paquete_service.es_primera_entrega_a_telefono`) -- separado así
a propósito para poder probar toda la aritmética (exención de primera
entrega, bloques de bodegaje) sin sesión de BD ni HTTP de por medio.
"""

import math
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .cobro import Cobro
from .paquete import Paquete, TipoPaquete
from .tarifa_cobro import ID_SINGLETON, TarifaCobro
from .usuario import Usuario

# Grace period antes de que empiece a correr el bodegaje, y el tamaño de cada
# bloque de cobro adicional -- .scratch/cobro-bodegaje, pedido explícito del
# cliente ("pasado 1 minuto de estas 48 horas ya se estaría realizando el
# cobro de bodegaje... cada 24 horas adicionales seguirá incrementándose").
_HORAS_GRACIA_BODEGAJE = 48
_HORAS_POR_BLOQUE_BODEGAJE = 24

# Valores iniciales por defecto -- .scratch/cobro-bodegaje, pedido explícito
# del cliente. Solo se usan mientras ningún ADMIN haya editado `TarifaCobro`
# todavía (ver `obtener_tarifas_vigentes`).
_TARIFA_BASE_NORMAL_DEFECTO = 1500
_TARIFA_BASE_EXTRA_DIMENSIONADO_DEFECTO = 2000
_TARIFA_BODEGAJE_NORMAL_24H_DEFECTO = 1000
_TARIFA_BODEGAJE_EXTRA_DIMENSIONADO_24H_DEFECTO = 1500


@dataclass(frozen=True)
class DesgloseCobro:
    """Resultado de `calcular_cobro` -- listo para mostrarse en el modal
    Entregar y para persistirse tal cual en un `Cobro` nuevo."""

    monto_base: int
    bloques_bodegaje: int
    monto_bodegaje: int
    monto_total: int


def obtener_tarifas_vigentes(session: Session) -> TarifaCobro:
    """La fila vigente de tarifas -- si ningún ADMIN la editó todavía, se
    materializa con los valores por defecto (nunca `None`, para que
    `calcular_cobro` siempre tenga con qué trabajar)."""
    fila = session.get(TarifaCobro, ID_SINGLETON)
    if fila is None:
        fila = TarifaCobro(
            id=ID_SINGLETON,
            base_normal=_TARIFA_BASE_NORMAL_DEFECTO,
            base_extra_dimensionado=_TARIFA_BASE_EXTRA_DIMENSIONADO_DEFECTO,
            bodegaje_normal_24h=_TARIFA_BODEGAJE_NORMAL_24H_DEFECTO,
            bodegaje_extra_dimensionado_24h=_TARIFA_BODEGAJE_EXTRA_DIMENSIONADO_24H_DEFECTO,
        )
        session.add(fila)
        session.flush()
    return fila


def calcular_cobro(
    paquete: Paquete,
    tarifas: TarifaCobro,
    ahora: datetime,
    es_primera_entrega: bool,
) -> DesgloseCobro:
    """Desglose del cobro a aplicar a `paquete`: cargo base según su
    `TipoPaquete` (exento si `es_primera_entrega`) + bodegaje (bloques de 24h
    desde el minuto 48:01 de haber sido Recibido -- NUNCA exento, ni para
    primera entrega). Sin `received_at` (paquete nunca Recibido), el
    bodegaje queda en 0 por no haber nada que contar."""
    es_extra_dimensionado = paquete.package_type == TipoPaquete.EXTRA_DIMENSIONADO

    monto_base = (
        tarifas.base_extra_dimensionado if es_extra_dimensionado else tarifas.base_normal
    )
    if es_primera_entrega:
        monto_base = 0

    bloques_bodegaje = 0
    monto_bodegaje = 0
    if paquete.received_at is not None:
        horas_transcurridas = (ahora - paquete.received_at).total_seconds() / 3600
        if horas_transcurridas > _HORAS_GRACIA_BODEGAJE:
            bloques_bodegaje = math.ceil(
                (horas_transcurridas - _HORAS_GRACIA_BODEGAJE) / _HORAS_POR_BLOQUE_BODEGAJE
            )
            tarifa_bodegaje = (
                tarifas.bodegaje_extra_dimensionado_24h
                if es_extra_dimensionado
                else tarifas.bodegaje_normal_24h
            )
            monto_bodegaje = bloques_bodegaje * tarifa_bodegaje

    return DesgloseCobro(
        monto_base=monto_base,
        bloques_bodegaje=bloques_bodegaje,
        monto_bodegaje=monto_bodegaje,
        monto_total=monto_base + monto_bodegaje,
    )


def registrar_cobro(
    session: Session,
    paquete: Paquete,
    desglose: DesgloseCobro,
    actor: Usuario,
    motivo_anulacion: str = None,
) -> Cobro:
    """Persiste el `Cobro` de `paquete` -- llamar SOLO dentro de la misma
    transacción que `paquete_lifecycle.deliver()` (ver
    `packages.py::deliver_action`), nunca de forma aislada: un `Cobro` sin
    paquete `ENTREGADO` no tiene sentido de negocio.

    `motivo_anulacion` es obligatorio cuando `desglose.monto_total == 0` por
    anulación explícita del staff (ver `packages.py::deliver_action`, que ya
    distingue ese caso de un monto $0 por cálculo/primera entrega antes de
    llamar acá) -- esta función no lo re-valida, confía en el caller.
    """
    cobro = Cobro(
        id=uuid.uuid4(),
        paquete_id=paquete.id,
        monto_base=desglose.monto_base,
        bloques_bodegaje=desglose.bloques_bodegaje,
        monto_bodegaje=desglose.monto_bodegaje,
        monto_total=desglose.monto_total,
        motivo_anulacion=motivo_anulacion,
        cobrado_por_usuario_id=actor.id,
        cobrado_en=datetime.now(timezone.utc),
    )
    session.add(cobro)
    session.flush()
    return cobro
