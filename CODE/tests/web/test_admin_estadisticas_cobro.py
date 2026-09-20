# -*- coding: utf-8 -*-
"""
Capa web — `/administracion/estadisticas-cobro` (rediseño de tablero de
tarjetas, `.scratch/estadisticas-cobro-dashboard`, ticket 01; reemplaza el
rediseño de listas de `.scratch/estadisticas-cobro-interactivas`). Solo
lectura, exclusiva de admin.

La aritmética de las tarjetas (Panorama en hora de Colombia, filtros de
"Periodo seleccionado", casos de frontera de zona horaria) ya está probada a
fondo contra Postgres real en `tests/data_model/
test_estadisticas_tablero_service.py` (Seam A) -- acá solo se cubre que la
ruta HTTP arme los filtros correctos, que el control de acceso sea el
correcto, que el mecanismo de fetch en vivo devuelva solo el fragmento, y que
lo retirado (las 3 listas/paginación, el `<select>` de Usuario, Desde/Hasta,
el parámetro `hoy`) de verdad no esté.

Como la ruta ya no acepta fijar el reloj (`hoy` se retiró -- el servidor usa
su propio reloj real, en hora de Colombia), estos tests NO verifican límites
exactos de día/semana/mes (eso es del seam de dominio); solo que un cobro
recién creado ("ahora" real) aparece en el tablero y que los filtros se
reflejan en la salida.
"""

from app.domain.cobro import Cobro
from app.domain.cobro_service import DesgloseCobro, crear_motivo_anulacion, registrar_cobro
from app.domain.paquete import TipoPaquete
from app.domain.paquete_lifecycle import deliver as dom_deliver
from app.domain.paquete_lifecycle import receive as dom_receive
from app.domain.paquete_service import Destinatario, announce
from app.domain.staff_service import create_initial_admin, create_staff
from app.domain.usuario import RolUsuario, Usuario

_PW = "Contrasena1"


def _login_admin(client, email="admin@club.com"):
    admin = create_initial_admin(client.db, email, "Admin", _PW)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})
    return admin


def _login_operador(client, email="op@club.com"):
    admin = create_initial_admin(client.db, "admin@club.com", "Admin", _PW)
    create_staff(client.db, admin, email, "Opa", _PW, RolUsuario.OPERADOR)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})


def _zona_periodo(texto):
    """El fragmento de HTML de "Periodo seleccionado" -- es la ÚLTIMA de las
    3 zonas, así que basta con recortar desde su marca de apertura hasta el
    final. Panorama SIEMPRE muestra el total sin filtrar (issue estadisticas-
    cobro-dashboard): comparar un monto contra la página completa colisiona
    con la propia tarjeta de Panorama, que no filtra nada -- las
    aserciones de "Periodo seleccionado" deben acotarse a este recorte."""
    inicio = texto.index('aria-label="Periodo seleccionado')
    return texto[inicio:]


def _entregar_con_cobro(client, staff, monto_total, tel, tipo=None, motivo_anulacion=None):
    p = announce(
        client.db,
        anunciante_telefono=tel,
        anunciante_nombre="Ana",
        destinatario=Destinatario.yo_mismo(),
    )
    dom_receive(client.db, p, staff, package_type=tipo)
    dom_deliver(client.db, p, staff)
    registrar_cobro(
        client.db,
        p,
        DesgloseCobro(
            monto_base=monto_total, bloques_bodegaje=0, monto_bodegaje=0, monto_total=monto_total
        ),
        staff,
        motivo_anulacion=motivo_anulacion,
    )
    client.db.commit()
    return p


def test_sin_sesion_redirige_a_login(client):
    r = client.get("/administracion/estadisticas-cobro", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].endswith("/ingresar")


def test_operador_es_rechazado_403(client):
    _login_operador(client)
    r = client.get("/administracion/estadisticas-cobro")
    assert r.status_code == 403


def test_carga_completa_muestra_las_tres_zonas(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 4321, tel="3001111111")

    r = client.get("/administracion/estadisticas-cobro")
    assert r.status_code == 200
    assert "<h1" in r.text
    # Los 3 carriles de color -- Panorama (azul), Ahora (ámbar), Periodo
    # seleccionado (verde) -- ver `_estadisticas_tarjetas.html::zona`.
    assert "bg-blue-600" in r.text
    assert "bg-amber-500" in r.text
    assert "bg-emerald-600" in r.text
    assert "Ingresos" in r.text
    assert "Total de ingresos" in r.text
    assert "4,321" in r.text


def test_ingresos_de_panorama_no_cambia_con_ningun_filtro(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 7777, tel="3001111111", tipo=TipoPaquete.NORMAL)

    sin_filtro = client.get("/administracion/estadisticas-cobro")
    con_tipo = client.get(
        "/administracion/estadisticas-cobro", params={"tipo": "EXTRA_DIMENSIONADO"}
    )
    con_rango_lejano = client.get("/administracion/estadisticas-cobro", params={"rango": "hoy"})

    for r in (sin_filtro, con_tipo, con_rango_lejano):
        assert r.status_code == 200
        assert "7,777" in r.text  # sigue en "Ingresos" de Panorama, sin importar el filtro


def test_total_de_ingresos_de_periodo_responde_a_los_filtros(client):
    admin = _login_admin(client)
    normal = _entregar_con_cobro(client, admin, 1500, tel="3001111111", tipo=TipoPaquete.NORMAL)
    _entregar_con_cobro(client, admin, 2500, tel="3002222222", tipo=TipoPaquete.EXTRA_DIMENSIONADO)
    assert normal.estado.value == "ENTREGADO"

    sin_filtro = _zona_periodo(client.get("/administracion/estadisticas-cobro").text)
    assert "4,000" in sin_filtro  # Total de ingresos = todos los datos
    assert "Todos los datos" in sin_filtro

    solo_normal = _zona_periodo(
        client.get("/administracion/estadisticas-cobro", params={"tipo": "NORMAL"}).text
    )
    assert "1,500" in solo_normal
    assert "4,000" not in solo_normal
    assert "Normal" in solo_normal  # chip de filtro activo

    solo_extra = _zona_periodo(
        client.get(
            "/administracion/estadisticas-cobro", params={"tipo": "EXTRA_DIMENSIONADO"}
        ).text
    )
    assert "2,500" in solo_extra
    assert "Extra-dimensionado" in solo_extra


def test_total_de_ingresos_filtra_por_cobrado_y_anulado(client):
    admin = _login_admin(client)
    crear_motivo_anulacion(client.db, "Reclamo")
    client.db.commit()
    _entregar_con_cobro(client, admin, 1234, tel="3001111111")
    _entregar_con_cobro(client, admin, 0, tel="3002222222", motivo_anulacion="Reclamo")

    solo_anulados = client.get(
        "/administracion/estadisticas-cobro", params={"estado_cobro": "anulado"}
    )
    assert solo_anulados.status_code == 200
    assert "1,234" not in _zona_periodo(solo_anulados.text)
    assert "Anulado" in solo_anulados.text

    solo_cobrados = client.get(
        "/administracion/estadisticas-cobro", params={"estado_cobro": "cobrado"}
    )
    assert "1,234" in _zona_periodo(solo_cobrados.text)
    assert "Cobrado" in solo_cobrados.text


def test_una_clave_de_rango_desconocida_se_ignora_sin_error(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1500, tel="3001234567")

    r = client.get("/administracion/estadisticas-cobro", params={"rango": "no-existe"})
    assert r.status_code == 200
    assert "1,500" in r.text
    assert "Todos los datos" in r.text


def test_el_parametro_hoy_ya_no_se_acepta_y_se_ignora(client):
    """Issue estadisticas-cobro-dashboard, ticket 01: el servidor calcula
    "hoy" con su propio reloj, en hora de Colombia -- ya no depende de lo que
    mande el navegador."""
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1500, tel="3001234567")

    r = client.get(
        "/administracion/estadisticas-cobro",
        params={"rango": "hoy", "hoy": "1999-01-01"},
    )
    assert r.status_code == 200
    assert "1,500" in r.text  # sigue contando "hoy" de verdad, no 1999


def test_ya_no_acepta_desde_hasta_ni_paginacion_ni_usuario(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1500, tel="3001234567")

    r = client.get(
        "/administracion/estadisticas-cobro",
        params={
            "desde": "2020-01-01",
            "hasta": "2020-12-31",
            "pagina_apartamento": 2,
            "pagina_usuario": 2,
            "pagina_diario": 2,
            "usuario_id": "no-es-un-uuid",
        },
    )
    assert r.status_code == 200
    assert "1,500" in r.text  # ninguno de esos parámetros lo excluyó


def test_las_tres_listas_y_sus_controles_ya_no_existen(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1500, tel="3001234567")

    r = client.get("/administracion/estadisticas-cobro")
    for texto in (
        "Por cliente / apartamento",
        "Por usuario",
        "Serie diaria",
        "Todos los usuarios",
        'name="desde"',
        'name="hasta"',
        'name="usuario_id"',
        "data-pag-prev",
        "data-pag-next",
    ):
        assert texto not in r.text


def test_barra_de_filtros_tiene_los_siete_atajos_sin_fechas_sueltas(client):
    import re

    _login_admin(client)

    r = client.get("/administracion/estadisticas-cobro")
    assert r.status_code == 200
    assert re.findall(r'data-atajo-fecha="(\w+)"', r.text) == [
        "hoy", "ayer", "semana", "mes", "tres_meses", "semestre", "anio",
    ]
    assert 'type="date"' not in r.text
    assert set(dict(re.findall(r'data-atajo-fecha="(\w+)"[^>]*aria-pressed="(\w+)"', r.text)).values()) == {
        "false"
    }


def test_el_atajo_activo_llega_resaltado(client):
    import re

    _login_admin(client)

    r = client.get("/administracion/estadisticas-cobro", params={"rango": "semestre"})
    estados = dict(re.findall(r'data-atajo-fecha="(\w+)"[^>]*aria-pressed="(\w+)"', r.text))
    assert estados["semestre"] == "true"
    assert [k for k, v in estados.items() if v == "true"] == ["semestre"]
    assert 'name="rango" value="semestre"' in r.text

    desconocido = client.get("/administracion/estadisticas-cobro", params={"rango": "no-existe"})
    assert set(dict(re.findall(r'data-atajo-fecha="(\w+)"[^>]*aria-pressed="(\w+)"', desconocido.text)).values()) == {
        "false"
    }
    assert 'name="rango" value=""' in desconocido.text


def test_con_base_vacia_carga_sin_error(client):
    _login_admin(client)

    r = client.get("/administracion/estadisticas-cobro")
    assert r.status_code == 200
    assert "$0" in r.text


def test_peticion_en_vivo_devuelve_solo_el_fragmento(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1500, tel="3001234567")

    r = client.get(
        "/administracion/estadisticas-cobro", headers={"X-Requested-With": "fetch"}
    )
    assert r.status_code == 200
    assert "<html" not in r.text
    assert "<h1" not in r.text  # el título vive en la barra de filtros, fuera del fragmento
    assert "1,500" in r.text


def test_carga_completa_incluye_la_barra_de_filtros_y_el_fragmento(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 4321, tel="3001111111")

    r = client.get("/administracion/estadisticas-cobro")
    assert r.status_code == 200
    assert "<h1" in r.text
    assert "4,321" in r.text


def test_paquetes_ritmo_y_tasas_se_ven_en_periodo(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1000, tel="3001111111")

    r = _zona_periodo(client.get("/administracion/estadisticas-cobro").text)
    for texto in ("Total de paquetes", "Anunciados", "Recibidos", "Entregados", "Cancelados", "Tasa de entrega", "Tasa de cancelación"):
        assert texto in r


def test_tipo_atenua_total_de_paquetes_pero_no_recibidos(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1000, tel="3001111111", tipo=TipoPaquete.NORMAL)

    sin_filtro = _zona_periodo(client.get("/administracion/estadisticas-cobro").text)
    assert "no depende de Tipo" not in sin_filtro

    con_tipo = _zona_periodo(
        client.get("/administracion/estadisticas-cobro", params={"tipo": "NORMAL"}).text
    )
    assert "no depende de Tipo" in con_tipo


def test_recaudo_completo_se_ve_en_periodo(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1000, tel="3001111111")

    r = _zona_periodo(client.get("/administracion/estadisticas-cobro").text)
    for texto in (
        "Promedio recaudado por paquete", "Recaudado por bodegaje", "Recaudado por servicio",
        "Exonerado por anulaciones", "Exenciones por primera entrega", "Cobro más alto",
    ):
        assert texto in r


def test_promedio_por_paquete_se_redondea_sin_decimales_de_flotante(client):
    """Bug real encontrado en vivo: `promedio_por_paquete` es un float (una
    división) -- formatearlo como dinero sin redondear imprimía algo como
    "$2,520.6919945725917" en vez de "$2,521"."""
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1000, tel="3001111111")
    _entregar_con_cobro(client, admin, 1234, tel="3002222222")

    r = _zona_periodo(client.get("/administracion/estadisticas-cobro").text)
    inicio = r.index("Promedio recaudado por paquete")
    articulo = r[inicio : r.index("</article>", inicio)]
    assert "$1,117" in articulo  # (1000+1234)/2 = 1117.0, exacto
    assert "." not in articulo


def test_exenciones_primera_entrega_se_atenua_con_cobrado_anulado_pero_no_con_tipo(client):
    """Matriz de "no aplica" (issue estadisticas-cobro-dashboard, spec.md):
    esta tarjeta es la única excepción dentro de "Recaudo" -- Tipo SÍ la
    acota, Cobrado/Anulado NO."""
    admin = _login_admin(client)
    crear_motivo_anulacion(client.db, "Reclamo")
    client.db.commit()
    _entregar_con_cobro(client, admin, 1500, tel="3001111111")  # primera entrega -- exenta

    def _articulo(texto):
        r = _zona_periodo(texto)
        inicio = r.index("Exenciones por primera entrega")
        return r[inicio : r.index("</article>", inicio)]

    con_estado = client.get(
        "/administracion/estadisticas-cobro", params={"estado_cobro": "cobrado"}
    ).text
    assert "no depende de Cobrado/Anulado" in _articulo(con_estado)

    con_tipo = client.get("/administracion/estadisticas-cobro", params={"tipo": "NORMAL"}).text
    assert "no depende de" not in _articulo(con_tipo)


def test_clientes_se_ven_en_periodo_con_nombre_no_telefono(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1000, tel="3001111111")

    r = _zona_periodo(client.get("/administracion/estadisticas-cobro").text)
    for texto in ("Clientes activos", "Clientes nuevos", "Clientes recurrentes", "Cliente con más paquetes", "Cliente con mayor gasto"):
        assert texto in r
    assert "ANA" in r  # el nombre del cliente destacado, no su teléfono
    assert "+573001111111" not in r


def test_cobrado_anulado_atenua_paquetes_y_ritmo_pero_no_recaudo(client):
    admin = _login_admin(client)
    crear_motivo_anulacion(client.db, "Reclamo")
    client.db.commit()
    _entregar_con_cobro(client, admin, 1000, tel="3001111111")

    r = _zona_periodo(
        client.get("/administracion/estadisticas-cobro", params={"estado_cobro": "cobrado"}).text
    )
    assert "no depende de Cobrado/Anulado" in r
    # "Total de ingresos" (Recaudo) SÍ responde a Cobrado/Anulado -- nunca
    # debería llevar esa nota.
    inicio_recaudo = r.index("Total de ingresos")
    fin_recaudo = r.index("</article>", inicio_recaudo)
    assert "no depende de" not in r[inicio_recaudo:fin_recaudo]


def test_operacion_y_calidad_se_ven_en_periodo(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1000, tel="3001111111")

    r = _zona_periodo(client.get("/administracion/estadisticas-cobro").text)
    for texto in (
        "Operador con más entregas",
        "Día más activo",
        "Hora pico",
        "Entregas dentro de 48h",
        "Extra-dimensionados",
        "Recibidos en mal estado",
    ):
        assert texto in r


def test_operacion_y_calidad_no_depende_de_cobrado_anulado(client):
    # Ninguna tarjeta de Operación/Calidad responde a Cobrado/Anulado (matriz
    # del ticket 05) -- al activar ese filtro, todas deben mostrar la nota.
    admin = _login_admin(client)
    crear_motivo_anulacion(client.db, "Reclamo")
    client.db.commit()
    _entregar_con_cobro(client, admin, 1000, tel="3001111111")

    r = _zona_periodo(
        client.get("/administracion/estadisticas-cobro", params={"estado_cobro": "cobrado"}).text
    )

    def _articulo(titulo):
        inicio = r.index(titulo)
        return r[inicio : r.index("</article>", inicio)]

    for titulo in (
        "Operador con más entregas",
        "Día más activo",
        "Hora pico",
        "Entregas dentro de 48h",
        "Extra-dimensionados",
        "Recibidos en mal estado",
    ):
        assert "no depende de Cobrado/Anulado" in _articulo(titulo)


def test_extra_dimensionados_no_depende_de_tipo(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1000, tel="3001111111", tipo=TipoPaquete.NORMAL)

    r = _zona_periodo(
        client.get("/administracion/estadisticas-cobro", params={"tipo": "NORMAL"}).text
    )
    inicio = r.index("Extra-dimensionados")
    fin = r.index("</article>", inicio)
    assert "no depende de Tipo" in r[inicio:fin]

    inicio_operador = r.index("Operador con más entregas")
    fin_operador = r.index("</article>", inicio_operador)
    assert "no depende de" not in r[inicio_operador:fin_operador]


def test_panorama_entregados_y_cancelados_no_cambian_con_filtros(client):
    admin = _login_admin(client)
    _entregar_con_cobro(client, admin, 1000, tel="3001111111")

    r = client.get("/administracion/estadisticas-cobro").text
    inicio = r.index('aria-label="Panorama')
    fin = r.index('aria-label="Ahora')
    panorama = r[inicio:fin]
    assert "Entregados" in panorama
    assert "Cancelados" in panorama

    con_filtros = client.get(
        "/administracion/estadisticas-cobro", params={"tipo": "NORMAL", "rango": "hoy"}
    ).text
    inicio2 = con_filtros.index('aria-label="Panorama')
    fin2 = con_filtros.index('aria-label="Ahora')
    panorama_filtrado = con_filtros[inicio2:fin2]
    assert panorama == panorama_filtrado
