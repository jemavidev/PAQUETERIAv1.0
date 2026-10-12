"""
Vista "Avisos especiales" (`.scratch/avisos-especiales`, tickets 03-07): el ADMIN ve, un cliente por fila, a quienes
tienen algo pendiente en Papyrus (Anunciados de los últimos 5 días calendario y todos los Recibidos) y les avisa por
SMS o WhatsApp que ciertos días no hay servicio.
"""

import re
from datetime import datetime, timedelta, timezone

from app.domain.paquete_lifecycle import cancel, deliver, receive
from app.domain.paquete_service import Destinatario, announce
from app.domain.staff_service import create_initial_admin, create_staff
from app.domain.usuario import RolUsuario, Usuario
from app.domain.zona_horaria import ZONA_HORARIA_APP

_PW = "Contrasena1"
_URL = "/administracion/avisos-especiales"


def _login_admin(client, email="admin@club.com"):
    create_initial_admin(client.db, email, "Admin", _PW)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})
    return client.db.query(Usuario).filter(Usuario.email == email).one()


def _login_operador(client, email="op@club.com"):
    admin = create_initial_admin(client.db, "admin@club.com", "Admin", _PW)
    create_staff(client.db, admin, email, "Opa", _PW, RolUsuario.OPERADOR)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})


def _anunciar(client, tel="3001234567", nombre="Ana", hace_dias=0, apartamento=None):
    """Un Paquete ANUNCIADO por `tel` para sí mismo; `hace_dias` corre su fecha de anuncio a ese día calendario
    (hora de Colombia), al mediodía."""
    p = announce(
        client.db,
        anunciante_telefono=tel,
        anunciante_nombre=nombre,
        destinatario=Destinatario.yo_mismo(),
        apartamento=apartamento,
    )
    if hace_dias:
        dia = datetime.now(ZONA_HORARIA_APP).date() - timedelta(days=hace_dias)
        p.announced_at = datetime(dia.year, dia.month, dia.day, 12, tzinfo=ZONA_HORARIA_APP).astimezone(timezone.utc)
    client.db.commit()
    return p


def _filas(html):
    """El texto de cada fila de cliente (escritorio), en orden."""
    filas = re.findall(r"<tr[^>]*data-cliente-aviso[^>]*>(.*?)</tr>", html, re.S)
    return [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", f)).strip() for f in filas]


# --------------------------------------------------------------------------- #
# Ticket 03 -- la lista de clientes
# --------------------------------------------------------------------------- #
def test_admin_ve_a_los_clientes_con_paquetes_recibidos(client):
    admin = _login_admin(client)
    p = _anunciar(client, tel="3001234567", nombre="Ana")
    receive(client.db, p, admin)
    client.db.commit()

    r = client.get(_URL)

    assert r.status_code == 200
    filas = _filas(r.text)
    assert len(filas) == 1
    assert "ANA" in filas[0] and p.access_code in filas[0]


def test_sin_sesion_redirige_a_ingresar_y_operador_es_rechazado(client):
    r = client.get(_URL, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].endswith("/ingresar")

    _login_operador(client)
    assert client.get(_URL).status_code == 403


def test_anunciados_de_los_ultimos_5_dias_calendario_entran_y_los_mas_viejos_no(client):
    _login_admin(client)
    _anunciar(client, tel="3001111111", nombre="Hoy")
    _anunciar(client, tel="3002222222", nombre="Hace cuatro", hace_dias=4)
    _anunciar(client, tel="3003333333", nombre="Hace cinco", hace_dias=5)

    texto = " ".join(_filas(client.get(_URL).text))

    assert "HOY" in texto and "HACE CUATRO" in texto
    assert "HACE CINCO" not in texto


def test_recibidos_viejos_entran_y_entregados_o_cancelados_nunca(client):
    admin = _login_admin(client)
    viejo = _anunciar(client, tel="3001111111", nombre="Recibido viejo", hace_dias=40)
    receive(client.db, viejo, admin)
    entregado = _anunciar(client, tel="3002222222", nombre="Entregado")
    receive(client.db, entregado, admin)
    deliver(client.db, entregado, admin)
    cancelado = _anunciar(client, tel="3003333333", nombre="Cancelado")
    cancel(client.db, cancelado, admin, motivo="Otro")
    client.db.commit()

    texto = " ".join(_filas(client.get(_URL).text))

    assert "RECIBIDO VIEJO" in texto
    assert "ENTREGADO" not in texto and "CANCELADO" not in texto


def test_un_cliente_con_varios_paquetes_es_una_sola_fila_con_todos_sus_codigos(client):
    admin = _login_admin(client)
    uno = _anunciar(client, tel="3001234567", nombre="Ana")
    dos = _anunciar(client, tel="3001234567", nombre="Ana")
    receive(client.db, dos, admin)
    client.db.commit()

    filas = _filas(client.get(_URL).text)

    assert len(filas) == 1
    assert uno.access_code in filas[0] and dos.access_code in filas[0]


def test_cada_codigo_enlaza_a_consultar_con_el_color_de_su_estado(client):
    _login_admin(client)
    p = _anunciar(client)

    html = client.get(_URL).text

    enlace = re.search(rf'<a href="/consultar\?q={p.access_code}"[^>]*>', html).group(0)
    assert "bg-amber-400" in enlace  # Anunciado


def test_sin_clientes_pendientes_muestra_un_estado_vacio(client):
    _login_admin(client)

    html = client.get(_URL).text

    assert "No hay clientes con paquetes pendientes." in html
    assert _filas(html) == []


def test_el_menu_de_cuenta_trae_avisos_especiales_solo_para_admin(client):
    _login_admin(client)
    assert f'href="{_URL}"' in client.get("/paquetes").text


def test_el_menu_de_cuenta_no_trae_avisos_especiales_al_operador(client):
    _login_operador(client)
    assert f'href="{_URL}"' not in client.get("/paquetes").text


def test_la_ventana_de_anunciados_empieza_a_medianoche_hora_colombia_de_hace_4_dias():
    from datetime import date

    from app.domain.aviso_especial_service import inicio_ventana_anunciados

    inicio = inicio_ventana_anunciados(date(2026, 10, 11))

    # Medianoche del 7 de octubre en Colombia (UTC-5) = 05:00 UTC.
    assert inicio == datetime(2026, 10, 7, 5, 0, tzinfo=timezone.utc)
    once_pm_del_6 = datetime(2026, 10, 6, 23, 0, tzinfo=ZONA_HORARIA_APP)  # 5 días calendario atrás: fuera
    assert once_pm_del_6 < inicio
    assert datetime(2026, 10, 7, 0, 0, tzinfo=ZONA_HORARIA_APP) >= inicio
