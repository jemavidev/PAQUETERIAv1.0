# -*- coding: utf-8 -*-
"""
Pantalla "Respaldos" (`.scratch/respaldos-y-restauracion`, ticket 08) -- Seam B por HTTP: solo ADMIN, lista de los
respaldos del disco del servidor, descarga `.zip` y comando de restauración listo para copiar.
"""

import io
import zipfile
from datetime import datetime, timezone

import pytest

from app.domain.respaldo_service import Instalacion, MotivoRespaldo, crear_respaldo
from app.domain.staff_service import create_initial_admin, create_staff
from app.domain.usuario import RolUsuario

_PW = "Contrasena1"
_URL = "/administracion/respaldos"


def _login_admin(client, email="admin@club.com"):
    create_initial_admin(client.db, email, "Admin", _PW)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})


def _login_operador(client, email="op@club.com"):
    admin = create_initial_admin(client.db, "admin@club.com", "Admin", _PW)
    create_staff(client.db, admin, email, "Opa", _PW, RolUsuario.OPERADOR)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})


@pytest.fixture()
def respaldos(tmp_path, monkeypatch, migrated_db_url):
    """Dos respaldos reales en una carpeta de respaldos propia de la prueba."""
    monkeypatch.setenv("RESPALDO_DIR", str(tmp_path))
    instalacion = Instalacion(database_url=migrated_db_url, dominio="test.papyrus.com.co", commit="abc1234")
    viejo = crear_respaldo(instalacion, tmp_path, MotivoRespaldo.DIARIO, ahora=datetime(2026, 9, 24, 8, 0, tzinfo=timezone.utc))
    nuevo = crear_respaldo(instalacion, tmp_path, MotivoRespaldo.A_PEDIDO, ahora=datetime(2026, 9, 25, 15, 30, tzinfo=timezone.utc))
    return viejo, nuevo


def test_sin_sesion_redirige_a_login(client, respaldos):
    r = client.get(_URL, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].endswith("/ingresar")


def test_un_operador_no_puede_ver_ni_descargar_respaldos(client, respaldos):
    _login_operador(client)
    assert client.get(_URL).status_code == 403
    assert client.get(f"{_URL}/{respaldos[0].carpeta.name}/descargar").status_code == 403


def test_el_admin_ve_los_respaldos_del_disco_del_mas_nuevo_al_mas_viejo(client, respaldos):
    _login_admin(client)
    html = client.get(_URL).text

    viejo, nuevo = respaldos
    assert html.index(nuevo.carpeta.name) < html.index(viejo.carpeta.name)
    assert "2026-09-25 10:30" in html and "A pedido" in html
    assert "2026-09-24 03:00" in html and "Diario" in html
    assert "paquetex-respaldos" in html  # dónde están los anteriores (S3)


def test_cada_respaldo_muestra_el_comando_exacto_para_restaurarlo(client, respaldos):
    _login_admin(client)
    html = client.get(_URL).text

    nombre = respaldos[0].carpeta.name
    assert f"scripts/respaldos/restaurar.sh /home/ubuntu/paquetex-respaldos/{nombre}" in html


def test_descargar_un_respaldo_entrega_un_zip_con_todos_sus_archivos(client, respaldos):
    _login_admin(client)
    carpeta = respaldos[1].carpeta

    r = client.get(f"{_URL}/{carpeta.name}/descargar")

    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    assert f'filename="{carpeta.name}.zip"' in r.headers["content-disposition"]
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        assert sorted(z.namelist()) == sorted(f"{carpeta.name}/{a.name}" for a in carpeta.iterdir())
        assert z.read(f"{carpeta.name}/base_datos.dump") == (carpeta / "base_datos.dump").read_bytes()


@pytest.mark.parametrize("nombre", ["no_existe", "..", "%2E%2E%2Fetc"])
def test_no_se_puede_descargar_nada_que_no_sea_un_respaldo(client, respaldos, nombre):
    _login_admin(client)
    assert client.get(f"{_URL}/{nombre}/descargar").status_code == 404


def test_el_menu_de_datos_enlaza_la_pantalla_de_respaldos(client, respaldos):
    _login_admin(client)
    html = client.get("/paquetes").text
    i = html.index('data-cat-panel="datos"')
    assert f'href="{_URL}"' in html[i : html.index("</div>", i)]
