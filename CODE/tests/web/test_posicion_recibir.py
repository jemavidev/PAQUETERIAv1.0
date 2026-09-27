# -*- coding: utf-8 -*-
"""
Capa web — Posición de almacenamiento al Recibir (`.scratch/posicion-almacenamiento`).

Seam HTTP: lo que el servidor guarda/rechaza al Recibir y el HTML del modal (la grilla del estante) en las
tres vistas que reutilizan el modal Recibir: /paquetes, /consultar (staff) y /announce (anunciar y recibir).
"""

import re

from app.domain.paquete import EstadoPaquete, Paquete
from app.domain.paquete_service import Destinatario, announce
from app.domain.staff_service import create_initial_admin

_PW = "Contrasena1"

# El estante visto de frente: fila 7 arriba … fila 1 abajo; izquierda = x2, derecha = x1.
_ORDEN_ESTANTE = ["72", "71", "62", "61", "52", "51", "42", "41", "32", "31", "22", "21", "12", "11"]


def _login_staff(client, email="staff@club.com"):
    create_initial_admin(client.db, email, "Staff", _PW)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})


def _anunciar(client, tel="3001234567", nombre="Ana"):
    p = announce(
        client.db,
        anunciante_telefono=tel,
        anunciante_nombre=nombre,
        destinatario=Destinatario.yo_mismo(),
    )
    client.db.commit()
    return p


def _form_recibir(html, paquete_id):
    """El `<form>` del modal Recibir de ese paquete."""
    m = re.search(rf'<form method="post" action="/paquetes/{paquete_id}/recibir".*?</form>', html, re.S)
    assert m, "el form Recibir del paquete no está en la página"
    return m.group(0)


def _posiciones_en_orden(form):
    return re.findall(r'name="posicion" value="(\d\d)"', form)


def _paquete(client, paquete_id):
    client.db.expire_all()
    return client.db.get(Paquete, paquete_id)


def test_recibir_con_posicion_la_guarda_en_el_paquete(client):
    _login_staff(client)
    p = _anunciar(client)

    r = client.post(f"/paquetes/{p.id}/recibir", data={"posicion": "41"}, follow_redirects=False)

    assert r.status_code == 303
    p = _paquete(client, p.id)
    assert p.estado == EstadoPaquete.RECIBIDO
    assert p.posicion == "41"


def test_recibir_con_posicion_fuera_del_estante_se_rechaza_sin_efecto(client):
    _login_staff(client)
    p = _anunciar(client)

    r = client.post(
        f"/paquetes/{p.id}/recibir",
        data={"posicion": "13", "torre": "1", "apartamento": "302"},
        follow_redirects=False,
    )

    assert r.status_code == 400
    assert "La posición «13» no existe en el estante." in r.text
    p = _paquete(client, p.id)
    assert p.estado == EstadoPaquete.ANUNCIADO
    assert p.posicion is None
    assert p.snapshot_apartamento is None  # la unidad NO se declaró


def test_el_modal_recibir_muestra_la_grilla_del_estante_antes_del_boton_en_paquetes_y_consultar(client):
    _login_staff(client)
    p = _anunciar(client)

    for ruta in ["/paquetes", f"/consultar?q={p.access_code}"]:
        r = client.get(ruta)
        assert r.status_code == 200, ruta
        form = _form_recibir(r.text, p.id)
        assert _posiciones_en_orden(form) == _ORDEN_ESTANTE, ruta
        # La grilla va al final, justo antes del botón Recibir.
        assert form.rindex('name="posicion"') < form.rindex(">Recibir</button>"), ruta


def test_el_modal_recibir_de_announce_muestra_la_grilla_del_estante(client):
    _login_staff(client)

    r = client.post("/announce", data={"telefono": "3001234567", "nombre": "Ana", "accion": "recibir"})

    assert r.status_code == 200
    client.db.expire_all()
    p = client.db.query(Paquete).one()
    assert _posiciones_en_orden(_form_recibir(r.text, p.id)) == _ORDEN_ESTANTE
