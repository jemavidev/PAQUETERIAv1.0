# -*- coding: utf-8 -*-
"""
Seam de navegador real — guía de más de 50 caracteres: error en el campo y envío bloqueado
(`.scratch/captura-guia-lector-camara`, ticket 04).

El campo NO lleva `maxlength`: cortaría en silencio lo que inyecta el lector del F7. Lo que se
cuenta es la guía NORMALIZADA (espacios colapsados y recortada), igual que en el servidor.
"""

from app.domain.paquete import EstadoPaquete

from _ayudantes import (
    abrir_modal_recibir,
    anunciar_paquete,
    iniciar_sesion_staff,
    paquete_en_bd,
)


def _abrir(app_viva, pagina):
    iniciar_sesion_staff(pagina, app_viva)
    p = anunciar_paquete(app_viva)
    abrir_modal_recibir(pagina, app_viva, p)
    return p


def _espiar_envios(pagina):
    enviados = []
    pagina.on(
        "request",
        lambda r: enviados.append(r.url) if r.method == "POST" and r.url.endswith("/recibir") else None,
    )
    return enviados


def _mensaje(pagina, p):
    return pagina.locator(f"#modal-receive-{p.id} .guia-largo-msg")


def test_mas_de_50_caracteres_marca_el_error_con_el_largo_y_bloquea_el_envio(app_viva, pagina):
    p = _abrir(app_viva, pagina)
    enviados = _espiar_envios(pagina)

    pagina.click(f"#guia-{p.id}")
    pagina.keyboard.insert_text("x" * 60)  # como lo inyecta un lector: texto de una vez

    # Sin maxlength: el campo conserva los 60 caracteres, no los corta en silencio.
    assert len(pagina.input_value(f"#guia-{p.id}")) == 60
    assert _mensaje(pagina, p).is_visible()
    assert "60" in _mensaje(pagina, p).inner_text()
    assert "50" in _mensaje(pagina, p).inner_text()

    pagina.click(f"#modal-receive-{p.id} button[type=submit]")
    pagina.wait_for_timeout(500)
    assert enviados == []
    assert paquete_en_bd(app_viva, p.id).estado == EstadoPaquete.ANUNCIADO


def test_al_corregir_la_guia_el_error_desaparece_y_recibir_funciona(app_viva, pagina):
    p = _abrir(app_viva, pagina)

    pagina.click(f"#guia-{p.id}")
    pagina.keyboard.insert_text("x" * 60)
    assert _mensaje(pagina, p).is_visible()

    pagina.fill(f"#guia-{p.id}", "")
    pagina.keyboard.type("abc-123")
    assert not _mensaje(pagina, p).is_visible()

    with pagina.expect_navigation():
        pagina.click(f"#modal-receive-{p.id} button[type=submit]")
    recibido = paquete_en_bd(app_viva, p.id)
    assert recibido.estado == EstadoPaquete.RECIBIDO
    assert recibido.guide_number == "ABC-123"


def test_los_espacios_que_se_colapsan_no_cuentan_para_el_maximo(app_viva, pagina):
    """60 caracteres crudos = 46 normalizados: no hay error y Recibir guarda la guía normalizada."""
    p = _abrir(app_viva, pagina)

    pagina.click(f"#guia-{p.id}")
    pagina.keyboard.insert_text("a" * 30 + " " * 15 + "b" * 15)
    assert not _mensaje(pagina, p).is_visible()

    with pagina.expect_navigation():
        pagina.click(f"#modal-receive-{p.id} button[type=submit]")
    assert paquete_en_bd(app_viva, p.id).guide_number == "A" * 30 + " " + "B" * 15


def test_si_el_envio_llega_al_servidor_el_modal_reabre_con_el_mensaje_visible(app_viva, pagina):
    """El camino defensivo: `form.submit()` no pasa por la validación del campo. El servidor rechaza con
    400, no recibe nada y reabre el modal Recibir con el mensaje DENTRO (el toast queda detrás del modal)."""
    p = _abrir(app_viva, pagina)

    pagina.click(f"#guia-{p.id}")
    pagina.keyboard.insert_text("x" * 60)
    with pagina.expect_navigation():
        pagina.evaluate(
            "id => document.querySelector('#modal-receive-' + id + ' form').submit()", str(p.id)
        )

    assert pagina.locator(f"#modal-receive-{p.id}").is_visible()
    assert _mensaje(pagina, p).is_visible()
    assert "La guía tiene 60 caracteres; el máximo es 50." in _mensaje(pagina, p).inner_text()
    assert paquete_en_bd(app_viva, p.id).estado == EstadoPaquete.ANUNCIADO
