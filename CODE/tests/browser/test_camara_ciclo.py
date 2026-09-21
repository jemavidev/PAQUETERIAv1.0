# -*- coding: utf-8 -*-
"""
Seam de navegador real — el escaneo con cámara tiene un ciclo de vida claro
(`.scratch/captura-guia-lector-camara`, ticket 06).

Antes un doble clic en "Escanear" abría dos flujos de cámara y, al cerrar el modal, solo se liberaba uno:
la cámara quedaba encendida detrás del modal hasta recargar la página. Tampoco había cómo cancelar un
escaneo sin haber leído nada. Cada prueba mira el estado de TODOS los flujos que se abrieron
(`camara.estado()`): al terminar, de cualquier forma, ninguno queda vivo.
"""

import pytest

from _ayudantes import (
    abrir_modal_entregar,
    abrir_modal_recibir,
    anunciar_paquete,
    iniciar_sesion_staff,
    recibir_paquete_en_bd,
)


def _abrir(app_viva, pagina):
    iniciar_sesion_staff(pagina, app_viva)
    p = anunciar_paquete(app_viva)
    abrir_modal_recibir(pagina, app_viva, p)
    return p


def _escanear_btn(pagina, p):
    return pagina.locator(f"#modal-receive-{p.id} .scan-btn")


def _detener_btn(pagina, p):
    return pagina.locator(f"#modal-receive-{p.id} .scan-stop")


def _video(pagina, p):
    return pagina.locator(f"#video-{p.id}")


def _sin_flujos_vivos(camara):
    pistas = camara.estado()["pistas"]
    return all(estado == "ended" for flujo in pistas for estado in flujo)


def _esperar_sin_flujos_vivos(pagina, camara):
    pagina.wait_for_function(
        "() => window.__camara.flujos.every(f => f.getTracks().every(t => t.readyState === 'ended'))"
    )
    assert _sin_flujos_vivos(camara)


def test_un_doble_clic_en_escanear_abre_un_solo_flujo(app_viva, pagina, camara):
    p = _abrir(app_viva, pagina)

    _escanear_btn(pagina, p).dblclick()
    _video(pagina, p).wait_for(state="visible")

    estado = camara.estado()
    assert estado["llamadas"] == 1
    assert estado["pistas"] == [["live"]]


def test_mientras_escanea_el_boton_queda_deshabilitado_y_aparece_detener(app_viva, pagina, camara):
    p = _abrir(app_viva, pagina)
    assert _detener_btn(pagina, p).count() == 0

    _escanear_btn(pagina, p).click()
    _video(pagina, p).wait_for(state="visible")

    assert _escanear_btn(pagina, p).is_disabled()
    assert _detener_btn(pagina, p).is_visible()
    assert _detener_btn(pagina, p).inner_text() == "Detener"


def test_detener_apaga_la_camara_oculta_el_video_y_deja_el_campo_como_estaba(app_viva, pagina, camara):
    p = _abrir(app_viva, pagina)
    pagina.click(f"#guia-{p.id}")
    pagina.keyboard.type("abc")

    _escanear_btn(pagina, p).click()
    _video(pagina, p).wait_for(state="visible")
    _detener_btn(pagina, p).click()

    _esperar_sin_flujos_vivos(pagina, camara)
    assert _video(pagina, p).is_hidden()
    assert pagina.input_value(f"#guia-{p.id}") == "ABC"
    assert _escanear_btn(pagina, p).is_enabled()
    assert _detener_btn(pagina, p).count() == 0


def test_una_lectura_llena_el_campo_apaga_la_camara_y_permite_otra(app_viva, pagina, camara):
    p = _abrir(app_viva, pagina)
    camara.con_video("gu-77")  # un QR real dibujado frente a la "cámara"

    _escanear_btn(pagina, p).click()
    pagina.wait_for_function(
        "id => document.getElementById('guia-' + id).value !== ''", arg=str(p.id), timeout=15_000
    )

    assert pagina.input_value(f"#guia-{p.id}") == "gu-77"  # tal como se leyó
    assert _video(pagina, p).is_hidden()
    _esperar_sin_flujos_vivos(pagina, camara)
    assert _escanear_btn(pagina, p).is_enabled()
    assert _detener_btn(pagina, p).count() == 0

    # Otra lectura funciona: el estado quedó reiniciado.
    camara.con_video("otra-88")
    _escanear_btn(pagina, p).click()
    pagina.wait_for_function(
        "id => document.getElementById('guia-' + id).value === 'otra-88'",
        arg=str(p.id),
        timeout=15_000,
    )
    _esperar_sin_flujos_vivos(pagina, camara)
    assert camara.estado()["llamadas"] == 2


@pytest.mark.parametrize("como", ["equis", "fondo", "escape"])
def test_cerrar_el_modal_apaga_la_camara_y_se_puede_volver_a_escanear(app_viva, pagina, camara, como):
    p = _abrir(app_viva, pagina)
    _escanear_btn(pagina, p).click()
    _video(pagina, p).wait_for(state="visible")

    if como == "equis":
        pagina.click(f'#modal-receive-{p.id} button[aria-label="Cerrar"]')
    elif como == "fondo":
        pagina.mouse.click(8, 450)  # sobre el fondo oscuro, fuera del panel del modal
    else:
        pagina.keyboard.press("Escape")

    pagina.wait_for_function("id => document.getElementById(id).hidden", arg=f"modal-receive-{p.id}")
    _esperar_sin_flujos_vivos(pagina, camara)

    # Reabrir el modal y escanear otra vez funciona.
    pagina.locator(f'[data-open="modal-receive-{p.id}"]:visible').first.click()
    _escanear_btn(pagina, p).click()
    _video(pagina, p).wait_for(state="visible")
    assert camara.estado()["llamadas"] == 2


def test_detener_antes_de_que_llegue_la_camara_no_deja_un_flujo_vivo(app_viva, pagina, camara):
    """El aviso de permiso sin contestar: si el Operador cancela antes de que la cámara responda, el flujo
    que llega tarde no puede quedar encendido."""
    p = _abrir(app_viva, pagina)
    camara.con_video(retardo_ms=800)

    _escanear_btn(pagina, p).click()
    _detener_btn(pagina, p).click()  # antes de que la cámara responda
    pagina.wait_for_function("() => window.__camara.flujos.length === 1", timeout=5_000)

    _esperar_sin_flujos_vivos(pagina, camara)
    assert _video(pagina, p).is_hidden()
    assert _escanear_btn(pagina, p).is_enabled()


def test_en_confirmar_guia_de_entregar_el_ciclo_es_el_mismo(app_viva, pagina, camara):
    iniciar_sesion_staff(pagina, app_viva)
    p = anunciar_paquete(app_viva)
    recibir_paquete_en_bd(app_viva, p, "GUIA-9")
    abrir_modal_entregar(pagina, app_viva, p)
    boton = pagina.locator(f"#modal-deliver-{p.id} .scan-btn")
    video = pagina.locator(f"#video-confirmar-{p.id}")

    boton.dblclick()
    video.wait_for(state="visible")
    assert camara.estado()["llamadas"] == 1
    assert boton.is_disabled()

    pagina.locator(f"#modal-deliver-{p.id} .scan-stop").click()
    _esperar_sin_flujos_vivos(pagina, camara)
    assert video.is_hidden()
    assert boton.is_enabled()

    boton.click()
    video.wait_for(state="visible")
    pagina.keyboard.press("Escape")
    pagina.wait_for_function("id => document.getElementById(id).hidden", arg=f"modal-deliver-{p.id}")
    _esperar_sin_flujos_vivos(pagina, camara)
