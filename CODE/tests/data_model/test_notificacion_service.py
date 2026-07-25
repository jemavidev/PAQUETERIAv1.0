# -*- coding: utf-8 -*-
"""
Seam A — Notificación de eventos del Paquete (mensaje + destino + best-effort).

Comportamiento observable: el mensaje correcto por evento (Cancelado incluye el
motivo); el destino es el Destinatario si tiene teléfono, si no el Anunciante;
un fallo del sender no se propaga.
"""

import pytest

from app.domain.notification_sender import ConsoleNotificationSender
from app.domain.notificacion_service import (
    construir_mensaje,
    notificar_evento,
    resolver_destino,
)
from app.domain.paquete import EstadoPaquete
from app.domain.paquete_lifecycle import cancel, deliver, receive
from app.domain.paquete_service import Destinatario, announce
from app.domain.usuario import RolUsuario, Usuario

pytestmark = pytest.mark.integration


def _usuario(session) -> Usuario:
    u = Usuario(nombre="Operador", rol=RolUsuario.OPERADOR)
    session.add(u)
    session.flush()
    return u


def _anunciar(session, destinatario=None):
    return announce(
        session,
        anunciante_telefono="3001234567",
        anunciante_nombre="Ana",
        destinatario=destinatario or Destinatario.yo_mismo(),
    )


def test_mensaje_recibido(db_session):
    p = _anunciar(db_session)
    msg = construir_mensaje(EstadoPaquete.RECIBIDO, p)
    assert "Ana" in msg and "portería" in msg


def test_mensaje_entregado(db_session):
    p = _anunciar(db_session)
    msg = construir_mensaje(EstadoPaquete.ENTREGADO, p)
    assert "Ana" in msg and "entregado" in msg


def test_mensaje_cancelado_incluye_el_motivo(db_session):
    op = _usuario(db_session)
    p = _anunciar(db_session)
    cancel(db_session, p, op, "NO_RECLAMADO")

    msg = construir_mensaje(EstadoPaquete.CANCELADO, p)
    assert "cancelado" in msg.lower()
    assert "no reclamado" in msg.lower()


def test_evento_que_no_notifica_lanza_valueerror():
    class _Fake:
        recipient_name = "X"

    with pytest.raises(ValueError):
        construir_mensaje(EstadoPaquete.ANUNCIADO, _Fake())


def test_destino_es_el_destinatario_registrado(db_session):
    from app.domain.persona_service import get_or_create_persona

    get_or_create_persona(db_session, "3019999999", "Beto")
    p = _anunciar(db_session, Destinatario.persona_registrada("3019999999"))

    assert resolver_destino(p) == "+573019999999"


def test_destino_es_el_anunciante_si_destinatario_sin_telefono(db_session):
    p = _anunciar(db_session, Destinatario.solo_nombre("Carlos"))
    assert resolver_destino(p) == "+573001234567"  # el anunciante (Ana)


def test_notificar_evento_llama_al_sender_con_destino_y_mensaje(db_session):
    p = _anunciar(db_session)
    sender = ConsoleNotificationSender()

    notificar_evento(p, EstadoPaquete.RECIBIDO, sender)

    assert len(sender.enviados) == 1
    destino, mensaje = sender.enviados[0]
    assert destino == "+573001234567"
    assert "Ana" in mensaje


def test_notificar_evento_no_propaga_si_el_sender_falla(db_session):
    p = _anunciar(db_session)

    class _SenderQueFalla:
        def enviar(self, destino, mensaje):
            raise RuntimeError("proveedor caído")

    notificar_evento(p, EstadoPaquete.ENTREGADO, _SenderQueFalla())  # no debe lanzar
