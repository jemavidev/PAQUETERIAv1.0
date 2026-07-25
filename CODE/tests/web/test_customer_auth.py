# -*- coding: utf-8 -*-
"""
Capa web — autenticación de cliente (OTP) + sesión independiente de staff.

Comportamiento observable por HTTP: pedir OTP, verificar (válido abre sesión,
inválido no — mensaje genérico), la ruta protegida exige/expone la Persona
correcta, logout cierra solo la sesión de cliente, y la sesión de staff/cliente
coexisten sin pisarse.
"""

from app.web.routes.customer_auth import _sender as dev_sender

_CANON = "+573001234567"


def _pedir_codigo(client, telefono="3001234567"):
    r = client.post("/auth/customer/request-otp", data={"telefono": telefono})
    assert r.status_code == 200
    return dev_sender.enviados[_CANON]


def test_get_customer_login_renderiza_el_formulario(client):
    r = client.get("/auth/customer/login")
    assert r.status_code == 200
    assert 'name="telefono"' in r.text


def test_request_otp_muestra_pantalla_de_verificar(client):
    r = client.post(
        "/auth/customer/request-otp", data={"telefono": "3001234567"}
    )
    assert r.status_code == 200
    assert 'name="codigo"' in r.text


def test_verify_otp_valido_abre_sesion_y_redirige(client):
    codigo = _pedir_codigo(client)
    r = client.post(
        "/auth/customer/verify-otp",
        data={"telefono": "3001234567", "codigo": codigo},
    )
    assert r.status_code == 200  # siguió el redirect a /auth/customer/me
    assert _CANON in r.text


def test_verify_otp_invalido_mensaje_generico_sin_sesion(client):
    _pedir_codigo(client)
    r = client.post(
        "/auth/customer/verify-otp",
        data={"telefono": "3001234567", "codigo": "000000"},
    )
    assert r.status_code == 400
    assert "inválido" in r.text.lower() or "expirado" in r.text.lower()

    r2 = client.get("/auth/customer/me", follow_redirects=False)
    assert r2.status_code == 303
    assert r2.headers["location"].endswith("/auth/customer/login")


def test_ruta_protegida_sin_sesion_redirige_a_customer_login(client):
    r = client.get("/auth/customer/me", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].endswith("/auth/customer/login")


def test_logout_cierra_solo_la_sesion_de_cliente(client):
    codigo = _pedir_codigo(client)
    client.post(
        "/auth/customer/verify-otp",
        data={"telefono": "3001234567", "codigo": codigo},
    )
    assert client.get("/auth/customer/me").status_code == 200

    client.post("/auth/customer/logout")
    r = client.get("/auth/customer/me", follow_redirects=False)
    assert r.status_code == 303


def test_sesion_de_staff_y_cliente_coexisten_sin_pisarse(client):
    from app.domain.staff_service import create_initial_admin

    create_initial_admin(client.db, "admin@club.com", "Admin", "Contrasena1")
    client.db.commit()

    # Abrir sesión de staff.
    client.post(
        "/auth/login", data={"email": "admin@club.com", "password": "Contrasena1"}
    )
    assert client.get("/auth/me").status_code == 200
    # La sesión de cliente NO existe todavía: la ruta de cliente sigue rechazando.
    assert client.get("/auth/customer/me", follow_redirects=False).status_code == 303

    # Abrir también sesión de cliente, en el MISMO navegador (mismo client/cookies).
    codigo = _pedir_codigo(client)
    client.post(
        "/auth/customer/verify-otp",
        data={"telefono": "3001234567", "codigo": codigo},
    )

    # Ambas sesiones responden 200 a la vez: no se pisaron.
    assert client.get("/auth/me").status_code == 200
    assert client.get("/auth/customer/me").status_code == 200

    # Cerrar la sesión de STAFF no debe afectar la de cliente.
    client.post("/auth/logout")
    assert client.get("/auth/customer/me").status_code == 200
    r = client.get("/auth/me", follow_redirects=False)
    assert r.status_code == 303  # staff sí cerró
