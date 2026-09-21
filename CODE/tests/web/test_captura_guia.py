# -*- coding: utf-8 -*-
"""
Capa web — captura de la Guía en Recibir/Entregar
(`.scratch/captura-guia-lector-camara`).

Seam 1 (HTTP sobre el servidor): lo que el servidor decide y el HTML que entrega al
cliente. Lo que solo existe en un navegador real (Enter, foco, cámara) vive en el seam
de navegador (`tests/browser`, marcador `browser`).
"""

import re

from app.domain.paquete_service import Destinatario, announce
from app.domain.staff_service import create_initial_admin
from app.domain.usuario import Usuario

_PW = "Contrasena1"


def _login_staff(client, email="staff@club.com"):
    create_initial_admin(client.db, email, "Staff", _PW)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})
    return client.db.query(Usuario).filter(Usuario.email == email).one()


def _anunciar(client, tel="3001234567", nombre="Ana"):
    p = announce(
        client.db,
        anunciante_telefono=tel,
        anunciante_nombre=nombre,
        destinatario=Destinatario.yo_mismo(),
    )
    client.db.commit()
    return p


def _bloques_script(html):
    """Cuerpos de los `<script>` inline sin atributos (los que emite `recursos_recibir()`)."""
    return re.findall(r"<script>(.*?)</script>", html, re.S)


def _bloques_con(html, marca):
    return [b for b in _bloques_script(html) if marca in b]


# --------------------------------------------------------------------------- #
# Ticket 01 (prefactor) — la captura de guía es un bloque propio dentro del
# componente compartido, en cada página que lo usa.
# --------------------------------------------------------------------------- #
def test_la_captura_de_guia_es_un_bloque_propio_y_unico_en_cada_pagina(client):
    _login_staff(client)
    p = _anunciar(client)

    rutas = ["/paquetes", f"/consultar?q={p.access_code}", "/announce", "/residentes"]
    for ruta in rutas:
        r = client.get(ruta)
        assert r.status_code == 200, ruta
        captura = _bloques_con(r.text, "BrowserMultiFormatReader")
        resto = _bloques_con(r.text, "pickerRenderTorres")

        # Exactamente un bloque de captura y uno del resto (picker/modales), y distintos.
        assert len(captura) == 1, ruta
        assert len(resto) == 1, ruta
        assert captura[0] != resto[0], ruta

        # El bloque de captura no arrastra lo demás, ni al revés.
        assert "pickerRenderTorres" not in captura[0], ruta
        assert "cargarTimelineDiferido" not in captura[0], ruta
        assert "BrowserMultiFormatReader" not in resto[0], ruta

        # Los estilos de escaneo se emiten una sola vez por página.
        assert r.text.count(".scan-msg {") == 1, ruta


# --------------------------------------------------------------------------- #
# Ticket 03 — la guardia del Enter llega a /announce y al Recibir de /consultar por reusar el
# mismo componente: el bloque de captura es el MISMO en todas las páginas que lo cargan.
# El comportamiento en sí (Enter/Tab/envío) se prueba en el seam de navegador real.
# --------------------------------------------------------------------------- #
def test_el_bloque_de_captura_es_el_mismo_en_todas_las_paginas_con_recibir(client):
    _login_staff(client)
    p = _anunciar(client)

    rutas = ["/paquetes", f"/consultar?q={p.access_code}", "/announce", "/residentes"]
    bloques = {}
    for ruta in rutas:
        r = client.get(ruta)
        assert r.status_code == 200, ruta
        captura = _bloques_con(r.text, "BrowserMultiFormatReader")
        assert len(captura) == 1, ruta
        bloques[ruta] = captura[0]

    de_referencia = bloques["/paquetes"]
    for ruta, bloque in bloques.items():
        assert bloque == de_referencia, f"{ruta} carga un bloque de captura distinto"
