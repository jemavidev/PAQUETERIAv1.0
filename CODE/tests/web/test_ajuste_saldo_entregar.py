# -*- coding: utf-8 -*-
"""
Capa web — ajuste opcional del saldo contra entrega al Entregar
(`.scratch/dinero-contra-entrega`, ticket 04).
"""

from app.domain.paquete import EstadoPaquete, Paquete
from app.domain.paquete_lifecycle import receive as dom_receive
from app.domain.paquete_service import Destinatario, announce
from app.domain.persona_service import get_or_create_persona
from app.domain.saldo_contra_entrega import MovimientoSaldoContraEntrega
from app.domain.saldo_contra_entrega_service import registrar_movimiento_saldo, saldo_de_persona
from app.domain.staff_service import create_initial_admin
from app.domain.usuario import Usuario

_PW = "Contrasena1"


def _login_staff(client, email="staff@club.com"):
    create_initial_admin(client.db, email, "Staff", _PW)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})
    return client.db.query(Usuario).filter(Usuario.email == email).one()


def _recibido_con_saldo_negativo(client, staff, tel="3001234567", saldo_inicial=-2000):
    persona = get_or_create_persona(client.db, tel, "Ana")
    registrar_movimiento_saldo(client.db, persona.id, saldo_inicial, staff)
    p = announce(
        client.db,
        anunciante_telefono=tel,
        anunciante_nombre="Ana",
        destinatario=Destinatario.yo_mismo(),
    )
    dom_receive(client.db, p, staff)
    client.db.commit()
    return p, persona


def test_saldo_negativo_muestra_el_campo_de_ajuste(client):
    staff = _login_staff(client)
    _recibido_con_saldo_negativo(client, staff)

    r = client.get("/paquetes")
    assert "Saldo pendiente" in r.text


def test_completar_el_ajuste_crea_el_movimiento_positivo(client):
    staff = _login_staff(client)
    p, persona = _recibido_con_saldo_negativo(client, staff)

    r = client.post(
        f"/paquetes/{p.id}/entregar", data={"pago_saldo": "2000"}, follow_redirects=False
    )
    assert r.status_code == 303

    client.db.expire_all()
    assert client.db.get(Paquete, p.id).estado == EstadoPaquete.ENTREGADO
    assert saldo_de_persona(client.db, persona.id) == 0
    mov = (
        client.db.query(MovimientoSaldoContraEntrega)
        .filter(MovimientoSaldoContraEntrega.paquete_id == p.id)
        .one()
    )
    assert mov.monto == 2000


def test_dejar_vacio_entrega_igual_sin_crear_movimiento(client):
    staff = _login_staff(client)
    p, persona = _recibido_con_saldo_negativo(client, staff)

    r = client.post(f"/paquetes/{p.id}/entregar", follow_redirects=False)
    assert r.status_code == 303

    client.db.expire_all()
    assert client.db.get(Paquete, p.id).estado == EstadoPaquete.ENTREGADO
    assert saldo_de_persona(client.db, persona.id) == -2000
    assert (
        client.db.query(MovimientoSaldoContraEntrega)
        .filter(MovimientoSaldoContraEntrega.paquete_id == p.id)
        .first()
        is None
    )


def test_sin_saldo_negativo_no_muestra_el_campo(client):
    staff = _login_staff(client)
    p = announce(
        client.db,
        anunciante_telefono="3009999999",
        anunciante_nombre="Beto",
        destinatario=Destinatario.yo_mismo(),
    )
    dom_receive(client.db, p, staff)
    client.db.commit()

    r = client.get("/paquetes")
    assert "Saldo pendiente" not in r.text
