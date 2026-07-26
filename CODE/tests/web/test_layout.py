# -*- coding: utf-8 -*-
"""
Capa web — header/footer transversales (Grupo 9, ticket 01:
`.scratch/header-footer/issues/01-header-footer-publicos.md`).

Comportamiento observable por HTTP para un visitante SIN ninguna sesión: el
header con marca + enlaces públicos + botones de login, el enlace de la
pantalla actual marcado como activo, y el footer móvil con los mismos
enlaces. Sin Tailwind ni Alpine.js (ADR-0004) — la app del rebuild es
clean-room, aislada del stack legacy.
"""


def test_visitante_publico_ve_header_con_marca_enlaces_y_botones_login(client):
    r = client.get("/anunciar")
    assert r.status_code == 200
    html = r.text

    assert "PAQUETEX" in html
    assert 'href="/anunciar"' in html
    assert 'href="/consultar"' in html
    assert 'href="/otp"' in html
    assert 'href="/ingresar"' in html


def test_visitante_publico_no_ve_ningun_enlace_de_cliente_ni_de_staff(client):
    r = client.get("/anunciar")
    html = r.text

    assert 'href="/mis-datos"' not in html
    assert 'href="/paquetes"' not in html
    assert 'href="/announce"' not in html
    assert 'href="/residentes"' not in html
    assert 'href="/administracion/personal"' not in html
    assert 'href="/administracion/notificaciones"' not in html


def _etiqueta_ancla(html: str, href: str, desde: int = 0) -> str:
    """Extrae el `<a ...>` completo que apunta a `href` (hasta el `>` de cierre),
    buscando a partir de `desde` (para saltarse el link de marca, que también
    apunta a `/anunciar`)."""
    inicio = html.index(f'href="{href}"', desde)
    fin = html.index(">", inicio)
    return html[max(0, inicio - 10) : fin + 1]


def test_enlace_de_la_pantalla_actual_queda_marcado_como_activo(client):
    r = client.get("/anunciar")
    html = r.text
    desde_nav = html.index('class="site-nav"')
    assert "aria-current" in _etiqueta_ancla(html, "/anunciar", desde_nav)
    assert "aria-current" not in _etiqueta_ancla(html, "/consultar", desde_nav)

    r2 = client.get("/consultar")
    html2 = r2.text
    desde_nav2 = html2.index('class="site-nav"')
    assert "aria-current" not in _etiqueta_ancla(html2, "/anunciar", desde_nav2)
    assert "aria-current" in _etiqueta_ancla(html2, "/consultar", desde_nav2)


def test_footer_movil_repite_los_enlaces_publicos(client):
    r = client.get("/consultar")
    html = r.text
    assert "site-footer-mobile" in html
    footer_idx = html.index("site-footer-mobile")
    footer_html = html[footer_idx:]
    assert 'href="/anunciar"' in footer_html
    assert 'href="/consultar"' in footer_html


def test_sin_tailwind_ni_alpine_ni_dependencias_nuevas(client):
    r = client.get("/anunciar")
    html = r.text.lower()
    assert "tailwind" not in html
    assert "alpine" not in html
    assert "x-data" not in html
    assert "cdn." not in html


def test_pantalla_publica_conserva_su_contenido_propio(client):
    r = client.get("/anunciar")
    html = r.text
    assert 'name="nombre"' in html
    assert 'name="telefono"' in html
    assert 'name="acepta_tyc"' in html
