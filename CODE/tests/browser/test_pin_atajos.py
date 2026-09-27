# -*- coding: utf-8 -*-
"""
Seam de navegador real — atajos del PIN de operador (`.scratch/pendientes-cliente`, issues 422 y 423).

- 422: candado en el header (a la izquierda del menú de cuenta) para bloquear el equipo en un toque, en escritorio y en
  móvil, solo con un Operador activo.
- 423: en escritorio el PIN se teclea sin depender del foco, en la pantalla de bloqueo y en la capa.
"""

from app.domain import operador_dispositivo_service as ods
from app.domain.configuracion_conjunto_service import actualizar_seguridad_sesion
from app.domain.staff_service import create_initial_admin

from _ayudantes import PASSWORD_STAFF, volver_a_iniciar_sesion


def _preparar(app_viva, pagina):
    admin = create_initial_admin(app_viva.db, "admin@club.com", "Admin", PASSWORD_STAFF)
    ods.definir_pin(app_viva.db, admin, "1357")
    actualizar_seguridad_sesion(app_viva.db, segundos_inactividad=60, dias_registro_dispositivo=15, actor=admin)
    app_viva.db.commit()
    volver_a_iniciar_sesion(pagina, app_viva, "admin@club.com")


def _candado(pagina):
    return pagina.locator("#site-header [data-bloquear-equipo]")


def test_el_candado_del_header_bloquea_el_equipo(app_viva, pagina):
    _preparar(app_viva, pagina)
    pagina.goto(f"{app_viva.url}/paquetes")
    assert _candado(pagina).is_visible()
    with pagina.expect_navigation():
        _candado(pagina).click()
    assert "/bloqueo" in pagina.url
    assert _candado(pagina).count() == 0  # bloqueado: ya no hay Operador activo


def test_el_candado_tambien_se_ve_en_movil(app_viva, pagina):
    _preparar(app_viva, pagina)
    pagina.set_viewport_size({"width": 390, "height": 844})
    pagina.goto(f"{app_viva.url}/paquetes")
    assert _candado(pagina).is_visible()


def test_sin_sesion_de_staff_no_hay_candado(app_viva, pagina):
    pagina.goto(f"{app_viva.url}/anunciar")
    assert _candado(pagina).count() == 0


def test_en_la_pantalla_de_bloqueo_se_teclea_el_pin_sin_el_mouse(app_viva, pagina):
    _preparar(app_viva, pagina)
    pagina.goto(f"{app_viva.url}/paquetes")
    with pagina.expect_navigation():
        _candado(pagina).click()
    pagina.mouse.click(5, 5)  # el foco no está en el campo del PIN
    pagina.keyboard.type("13")
    pagina.keyboard.press("Backspace")
    with pagina.expect_navigation():
        pagina.keyboard.type("357")
    assert pagina.url.endswith("/paquetes")


def test_en_la_capa_se_teclea_el_pin_sin_el_mouse(app_viva, pagina):
    _preparar(app_viva, pagina)
    pagina.clock.install()
    pagina.goto(f"{app_viva.url}/paquetes")
    pagina.clock.fast_forward("01:05")
    capa = pagina.locator("#capa-bloqueo")
    capa.wait_for(state="visible")
    pagina.mouse.click(5, 5)
    pagina.keyboard.type("1357")
    capa.wait_for(state="hidden")
