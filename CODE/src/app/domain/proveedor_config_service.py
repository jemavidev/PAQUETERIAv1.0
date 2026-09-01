# -*- coding: utf-8 -*-
"""
Service de `ProveedorConfig` — habilitado/orden de precedencia por
`(canal, proveedor)` (`.scratch/administracion-proveedores/spec.md`, issue
01). Nunca toca credenciales -- esas siguen solo en `.env` del servidor
(Fase 2, issue 04/05).

Sin ruta HTTP ni pantalla en esta rebanada (issue 03) -- este service es el
seam que el refactor de la cadena de failover (issue 02) y la pantalla van a
consumir, sin volver a tocar el modelo de datos.
"""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .preferencia_notificacion import CanalNotificacion
from .proveedor_config import ProveedorConfig
from .proveedor_config_historial import ProveedorConfigHistorial


def _buscar_config(session: Session, canal: CanalNotificacion, proveedor: str) -> ProveedorConfig | None:
    return (
        session.query(ProveedorConfig)
        .filter(ProveedorConfig.canal == canal.value, ProveedorConfig.proveedor == proveedor)
        .one_or_none()
    )


def listar_config(session: Session, canal: CanalNotificacion) -> list[ProveedorConfig]:
    """Las filas de `canal`, ordenadas por precedencia (`orden` ascendente,
    NULLs al final -- solo relevante para un canal con más de un proveedor;
    hoy únicamente SMS)."""
    return (
        session.query(ProveedorConfig)
        .filter(ProveedorConfig.canal == canal.value)
        .order_by(ProveedorConfig.orden.is_(None), ProveedorConfig.orden)
        .all()
    )


def guardar_habilitado_orden(
    session: Session,
    canal: CanalNotificacion,
    proveedor: str,
    habilitado: bool,
    orden: int | None = None,
    usuario_id: uuid.UUID | None = None,
) -> ProveedorConfig:
    """Crea o actualiza la fila de `(canal, proveedor)`, y deja un registro
    en `ProveedorConfigHistorial` por cada guardado exitoso -- append-only,
    nunca se edita ni se borra.

    `usuario_id` es opcional (default `None`): un historial con
    `usuario_id=NULL` es honesto para un caller sin actor real (tests de
    dominio, la migración de siembra), no un dato inventado -- mismo
    criterio que `notificacion_service.guardar_plantilla`.

    A diferencia de las credenciales (Fase 2), habilitado/orden nunca es
    secreto -- el historial guarda el valor COMPLETO de antes/después.

    Carrera (dos guardados simultáneos del mismo proveedor NUEVO -- mismo
    patrón que `notificacion_service.guardar_plantilla`): si el `INSERT`
    choca contra `uq_proveedores_config_canal_proveedor`, se reintenta como
    UPDATE sobre la fila que la otra transacción ya creó, en vez de propagar
    el `IntegrityError`."""
    config = _buscar_config(session, canal, proveedor)
    if config is None:
        config = ProveedorConfig(canal=canal.value, proveedor=proveedor)
        session.add(config)
        config.habilitado = habilitado
        config.orden = orden
        config.updated_by = usuario_id
        try:
            session.flush()
            habilitado_anterior, orden_anterior = None, None
        except IntegrityError:
            session.rollback()
            config = _buscar_config(session, canal, proveedor)
            habilitado_anterior, orden_anterior = config.habilitado, config.orden
            config.habilitado = habilitado
            config.orden = orden
            config.updated_by = usuario_id
            session.flush()
    else:
        habilitado_anterior, orden_anterior = config.habilitado, config.orden
        config.habilitado = habilitado
        config.orden = orden
        config.updated_by = usuario_id
        session.flush()

    session.add(
        ProveedorConfigHistorial(
            canal=canal.value,
            proveedor=proveedor,
            usuario_id=usuario_id,
            habilitado_anterior=habilitado_anterior,
            habilitado_nuevo=habilitado,
            orden_anterior=orden_anterior,
            orden_nuevo=orden,
        )
    )
    session.flush()
    return config
