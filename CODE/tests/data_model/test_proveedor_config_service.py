# -*- coding: utf-8 -*-
"""
Seam A — Configuración de proveedores de notificación (habilitado/orden),
`.scratch/administracion-proveedores/spec.md`, issue 01.

Comportamiento observable: guardar habilitado/orden para un `(canal,
proveedor)` crea o actualiza su fila, y deja un registro append-only en el
historial con el actor y el valor completo de antes/después; sin actor
(`usuario_id=None`) es honesto, no un dato inventado; `listar_config`
devuelve las filas de un canal ordenadas por precedencia.
"""

import pytest

from app.domain.preferencia_notificacion import CanalNotificacion
from app.domain.proveedor_config import ProveedorConfig
from app.domain.proveedor_config_historial import ProveedorConfigHistorial
from app.domain.proveedor_config_service import guardar_habilitado_orden, listar_config
from app.domain.usuario import RolUsuario, Usuario

pytestmark = pytest.mark.integration


def _usuario(session) -> Usuario:
    u = Usuario(nombre="Admin", rol=RolUsuario.ADMIN)
    session.add(u)
    session.flush()
    return u


# "OTRO_SMS": una clave que la migración de siembra NO crea (a diferencia de
# AWS_SNS/LIWA/TWILIO/SMTP, ya sembrados) -- simula un proveedor agregado al
# catálogo de código DESPUÉS de esa migración, para ejercitar el camino de
# "crear fila nueva" sin chocar con datos ya sembrados.


def test_guardar_en_proveedor_nuevo_crea_la_fila(db_session):
    config = guardar_habilitado_orden(
        db_session, CanalNotificacion.SMS, "OTRO_SMS", habilitado=False, orden=2
    )

    assert config.canal == "SMS"
    assert config.proveedor == "OTRO_SMS"
    assert config.habilitado is False
    assert config.orden == 2


def test_guardar_en_proveedor_nuevo_deja_historial_con_anterior_none(db_session):
    guardar_habilitado_orden(db_session, CanalNotificacion.SMS, "OTRO_SMS", habilitado=True, orden=1)

    fila = (
        db_session.query(ProveedorConfigHistorial)
        .filter_by(canal="SMS", proveedor="OTRO_SMS")
        .one()
    )
    assert fila.habilitado_anterior is None
    assert fila.habilitado_nuevo is True
    assert fila.orden_anterior is None
    assert fila.orden_nuevo == 1


def test_guardar_de_nuevo_actualiza_la_misma_fila_no_crea_otra(db_session):
    guardar_habilitado_orden(db_session, CanalNotificacion.SMS, "TWILIO", habilitado=True, orden=3)
    guardar_habilitado_orden(db_session, CanalNotificacion.SMS, "TWILIO", habilitado=False, orden=3)

    filas = db_session.query(ProveedorConfig).filter_by(canal="SMS", proveedor="TWILIO").all()
    assert len(filas) == 1
    assert filas[0].habilitado is False


def test_guardar_de_nuevo_el_historial_captura_el_anterior_correcto(db_session):
    guardar_habilitado_orden(db_session, CanalNotificacion.SMS, "TWILIO", habilitado=True, orden=3)
    guardar_habilitado_orden(db_session, CanalNotificacion.SMS, "TWILIO", habilitado=False, orden=1)

    historial = (
        db_session.query(ProveedorConfigHistorial)
        .filter_by(canal="SMS", proveedor="TWILIO")
        .order_by(ProveedorConfigHistorial.created_at)
        .all()
    )
    assert len(historial) == 2
    segundo = historial[1]
    assert segundo.habilitado_anterior is True
    assert segundo.habilitado_nuevo is False
    assert segundo.orden_anterior == 3
    assert segundo.orden_nuevo == 1


def test_historial_es_append_only_nunca_se_pisa(db_session):
    for i in range(3):
        guardar_habilitado_orden(
            db_session, CanalNotificacion.EMAIL, "SMTP", habilitado=True, orden=None
        )

    assert (
        db_session.query(ProveedorConfigHistorial).filter_by(canal="EMAIL", proveedor="SMTP").count()
        == 3
    )


def test_guardar_sin_actor_deja_usuario_id_null_honesto(db_session):
    config = guardar_habilitado_orden(
        db_session, CanalNotificacion.SMS, "AWS_SNS", habilitado=True, orden=1
    )

    assert config.updated_by is None
    historial = db_session.query(ProveedorConfigHistorial).one()
    assert historial.usuario_id is None


def test_guardar_con_actor_lo_registra_en_config_y_en_historial(db_session):
    admin = _usuario(db_session)

    config = guardar_habilitado_orden(
        db_session,
        CanalNotificacion.SMS,
        "AWS_SNS",
        habilitado=True,
        orden=1,
        usuario_id=admin.id,
    )

    assert config.updated_by == admin.id
    historial = db_session.query(ProveedorConfigHistorial).one()
    assert historial.usuario_id == admin.id


def test_listar_config_devuelve_solo_el_canal_pedido_ordenado_por_precedencia(db_session):
    guardar_habilitado_orden(db_session, CanalNotificacion.SMS, "TWILIO", habilitado=True, orden=3)
    guardar_habilitado_orden(db_session, CanalNotificacion.SMS, "AWS_SNS", habilitado=True, orden=1)
    guardar_habilitado_orden(db_session, CanalNotificacion.SMS, "LIWA", habilitado=True, orden=2)
    guardar_habilitado_orden(db_session, CanalNotificacion.EMAIL, "SMTP", habilitado=True, orden=None)

    filas = listar_config(db_session, CanalNotificacion.SMS)

    assert [f.proveedor for f in filas] == ["AWS_SNS", "LIWA", "TWILIO"]
