# -*- coding: utf-8 -*-
"""
Capa web — autenticación de staff (login / sesión / current_staff / require_admin).

Comportamiento observable por HTTP: login válido abre sesión, inválido no (mensaje
genérico), las rutas con privilegios se abren solo con sesión, logout cierra, y
require_admin distingue ADMIN de OPERADOR.
"""

from app.domain.staff_service import create_initial_admin, create_staff
from app.domain.usuario import RolUsuario

_PW = "Contrasena1"


def _seed_admin(client, email="admin@club.com"):
    create_initial_admin(client.db, email, "Admin", _PW)
    client.db.commit()
    return email


def _seed_operador(client, email="op@club.com"):
    admin = create_initial_admin(client.db, "admin@club.com", "Admin", _PW)
    create_staff(client.db, admin, email, "Opa", _PW, RolUsuario.OPERADOR)
    client.db.commit()
    return email


def test_get_login_renderiza_el_formulario(client):
    r = client.get("/auth/login")
    assert r.status_code == 200
    assert 'name="email"' in r.text and 'name="password"' in r.text


def test_login_valido_abre_sesion_y_me_muestra_al_staff(client):
    email = _seed_admin(client)
    r = client.post("/auth/login", data={"email": email, "password": _PW})
    assert r.status_code == 200  # siguió el redirect a /auth/me
    assert email in r.text  # la página de sesión muestra al staff


def test_login_invalido_no_abre_sesion_y_mensaje_generico(client):
    _seed_admin(client)
    r = client.post(
        "/auth/login", data={"email": "admin@club.com", "password": "mala12345"}
    )
    assert r.status_code == 400
    assert "incorrect" in r.text.lower()  # "Email o contraseña incorrectos."
    # Sin sesión: una ruta con privilegios manda al login.
    r2 = client.get("/auth/me", follow_redirects=False)
    assert r2.status_code == 303
    assert r2.headers["location"].endswith("/auth/login")


def test_me_sin_sesion_redirige_a_login(client):
    r = client.get("/auth/me", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].endswith("/auth/login")


def test_logout_cierra_la_sesion(client):
    email = _seed_admin(client)
    client.post("/auth/login", data={"email": email, "password": _PW})
    # con sesión, /auth/me responde 200
    assert client.get("/auth/me").status_code == 200
    client.post("/auth/logout")
    # tras logout, vuelve a redirigir al login
    r = client.get("/auth/me", follow_redirects=False)
    assert r.status_code == 303


def test_require_admin_admite_a_un_admin(client):
    email = _seed_admin(client)
    client.post("/auth/login", data={"email": email, "password": _PW})
    r = client.get("/auth/admin/check")
    assert r.status_code == 200
    assert r.json()["admin"] is True


def test_require_admin_rechaza_a_un_operador(client):
    email = _seed_operador(client)
    client.post("/auth/login", data={"email": email, "password": _PW})
    r = client.get("/auth/admin/check")
    assert r.status_code == 403
