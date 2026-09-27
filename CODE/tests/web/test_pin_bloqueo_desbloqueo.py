# -*- coding: utf-8 -*-
"""
Capa web — pantalla de bloqueo, desbloqueo con PIN y "Bloquear" (`.scratch/pin-operador-dispositivo`, ticket 03).

"Bloquear" deja el equipo en la pantalla de bloqueo, sin cerrar los registros. Un PIN válido convierte a su dueño en
el Operador activo, siempre que tenga un registro vigente en ESTE equipo. Dos `TestClient` = dos equipos.
"""

import re

import pytest
from fastapi.testclient import TestClient

from app.domain import operador_dispositivo_service as ods
from app.domain.paquete import EstadoPaquete, Paquete
from app.domain.paquete_service import Destinatario, announce
from app.domain.staff_service import create_initial_admin, create_staff
from app.domain.usuario import RolUsuario

pytestmark = pytest.mark.pin_manual

_PW = "Contrasena1"


def _sembrar(client):
    admin = create_initial_admin(client.db, "admin@club.com", "Admin", _PW)
    ana = create_staff(client.db, admin, "ana@club.com", "Ana", _PW, RolUsuario.OPERADOR)
    beto = create_staff(client.db, admin, "beto@club.com", "Beto", _PW, RolUsuario.OPERADOR)
    ods.definir_pin(client.db, admin, "1000")
    ods.definir_pin(client.db, ana, "1111")
    ods.definir_pin(client.db, beto, "2222")
    client.db.commit()
    return admin, ana, beto


def _ingresar(equipo, email):
    r = equipo.post("/ingresar", data={"email": email, "password": _PW}, follow_redirects=False)
    assert r.headers["location"] == "/paquetes"


def _desbloquear(equipo, pin, siguiente="/paquetes"):
    return equipo.post("/bloqueo", data={"pin": pin, "siguiente": siguiente}, follow_redirects=False)


def test_bloquear_lleva_a_la_pantalla_de_bloqueo_y_exige_el_pin(client):
    _sembrar(client)
    _ingresar(client, "ana@club.com")

    r = client.post("/bloquear", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/bloqueo"

    r = client.get("/paquetes", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/bloqueo?siguiente=/paquetes"

    r = client.get("/bloqueo")
    assert r.status_code == 200
    assert "EL CLUB" in r.text
    assert 'href="/ingresar"' in r.text
    assert not re.search(r"\bANA\b", r.text)  # no lista a los registrados (los nombres se guardan en mayúsculas)

    r = _desbloquear(client, "1111")
    assert r.status_code == 303
    assert r.headers["location"] == "/paquetes"
    assert client.get("/paquetes", follow_redirects=False).status_code == 200


def test_el_pin_de_otro_usuario_registrado_en_el_equipo_lo_vuelve_operador_activo(client):
    _sembrar(client)
    _ingresar(client, "ana@club.com")
    _ingresar(client, "beto@club.com")  # mismo equipo: ahora ambos registrados
    client.post("/bloquear")

    assert _desbloquear(client, "1111").status_code == 303
    assert "ANA" in client.get("/mi-sesion").text.upper()
    client.post("/bloquear")
    assert _desbloquear(client, "2222").status_code == 303
    assert "BETO" in client.get("/mi-sesion").text.upper()


def test_el_pin_no_sirve_en_un_equipo_donde_su_dueno_no_esta_registrado(client):
    _sembrar(client)
    _ingresar(client, "ana@club.com")
    client.post("/bloquear")

    r = _desbloquear(client, "2222")  # Beto nunca entró con contraseña en este equipo
    assert r.status_code == 400
    assert "PIN incorrecto" in r.text
    r_inexistente = _desbloquear(client, "9999")
    assert r_inexistente.status_code == 400
    assert "PIN incorrecto" in r_inexistente.text  # mismo mensaje: no revela si el PIN existe


def test_recibir_tras_desbloquear_con_el_pin_de_otro_queda_a_su_nombre(client):
    _, ana, beto = _sembrar(client)
    paquete = announce(
        client.db, anunciante_telefono="3001234567", anunciante_nombre="Carla", destinatario=Destinatario.yo_mismo()
    )
    client.db.commit()
    _ingresar(client, "ana@club.com")
    _ingresar(client, "beto@club.com")
    client.post("/bloquear")
    _desbloquear(client, "2222")

    client.post(f"/paquetes/{paquete.id}/recibir", data={"posicion": "41"})

    client.db.expire_all()
    paquete = client.db.get(Paquete, paquete.id)
    assert paquete.estado == EstadoPaquete.RECIBIDO
    assert paquete.received_by_usuario_id == beto.id


def test_equipo_sin_registros_vigentes_va_directo_a_ingresar(client):
    _sembrar(client)
    r = client.get("/bloqueo", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/ingresar"
    assert client.get("/paquetes", follow_redirects=False).headers["location"].endswith("/ingresar")


def test_bloquear_en_un_equipo_no_afecta_al_otro(client):
    _sembrar(client)
    otro_equipo = TestClient(client.app)
    _ingresar(client, "ana@club.com")
    _ingresar(otro_equipo, "ana@club.com")

    client.post("/bloquear")
    assert client.get("/paquetes", follow_redirects=False).status_code == 303
    assert otro_equipo.get("/paquetes", follow_redirects=False).status_code == 200


def test_desbloquear_sin_permiso_para_la_vista_pedida_va_al_inicio(client):
    _sembrar(client)
    _ingresar(client, "admin@club.com")
    _ingresar(client, "ana@club.com")
    client.post("/bloquear")

    r = _desbloquear(client, "1111", siguiente="/administracion/personal")
    assert r.headers["location"] == "/paquetes"
    client.post("/bloquear")
    r = _desbloquear(client, "1000", siguiente="/administracion/personal")
    assert r.headers["location"] == "/administracion/personal"


def test_siguiente_externo_se_ignora(client):
    _sembrar(client)
    _ingresar(client, "ana@club.com")
    client.post("/bloquear")
    for siguiente in ("https://evil.example/", "//evil.example/x", "paquetes"):
        client.post("/bloquear")
        assert _desbloquear(client, "1111", siguiente=siguiente).headers["location"] == "/paquetes"


def test_el_menu_trae_bloquear(client):
    _sembrar(client)
    _ingresar(client, "ana@club.com")
    assert 'action="/bloquear"' in client.get("/paquetes").text


def test_el_otp_del_residente_no_cambia(client):
    r = client.get("/otp", follow_redirects=False)
    assert r.status_code == 200
    r = client.get("/mis-paquetes", follow_redirects=False)
    assert r.headers["location"].endswith("/otp")


def test_cambiar_la_contrasena_invalida_el_pin_en_los_otros_equipos_no_en_el_propio(client):
    _sembrar(client)
    otro_equipo = TestClient(client.app)
    _ingresar(client, "ana@club.com")
    _ingresar(otro_equipo, "ana@club.com")

    r = client.post("/mi-sesion", data={"password": "OtraClave2025", "password_confirmacion": "OtraClave2025"})
    assert r.status_code == 200
    assert client.get("/paquetes", follow_redirects=False).status_code == 200

    r = otro_equipo.get("/paquetes", follow_redirects=False)
    assert r.headers["location"].endswith("/ingresar")  # no a /bloqueo: su registro también cayó
    assert _desbloquear(otro_equipo, "1111").status_code == 400
