"""
Mensajes especiales en `/administracion/notificaciones` (`.scratch/avisos-especiales`, tickets 01-02): el ADMIN crea,
edita y elimina los avisos que después manda desde la vista "Avisos especiales" (fines de semana, festivos...).
"""

import re

from app.domain.mensaje_especial import MensajeEspecial, MensajeEspecialHistorial
from app.domain.staff_service import create_initial_admin, create_staff
from app.domain.usuario import RolUsuario

_PW = "Contrasena1"
_URL = "/administracion/notificaciones"
_CREAR = "/administracion/notificaciones/mensajes-especiales"


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


def _seccion(html):
    """El HTML de la sección "Mensajes especiales" (la lista, sin los modales)."""
    m = re.search(r"<div[^>]*data-mensajes-especiales[^>]*>(.*?)</div>", html, re.S)
    assert m, "falta la sección de mensajes especiales"
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1)))


def _crear(client, nombre="Fin de semana", texto="Hola {nombre}: este sabado no hay servicio. Tus paquetes: {codigos}."):
    return client.post(_CREAR, data={"nombre": nombre, "texto": texto})


# --------------------------------------------------------------------------- #
# Ticket 01 -- crear
# --------------------------------------------------------------------------- #
def test_admin_crea_un_mensaje_especial_y_lo_ve_en_la_lista(client):
    _login_admin(client)

    r = _crear(client)

    assert r.status_code == 200
    assert "Mensaje especial creado." in r.text  # el toast
    assert "Fin de semana" in _seccion(r.text)
    assert "Fin de semana" in _seccion(client.get(_URL).text)


def test_operador_no_puede_crear_mensajes_especiales(client):
    _login_operador(client)

    r = _crear(client)

    assert r.status_code == 403
    assert client.db.query(MensajeEspecial).count() == 0


def test_nombre_repetido_sin_distinguir_mayusculas_se_rechaza(client):
    _login_admin(client)
    _crear(client, nombre="Fin de semana")

    r = _crear(client, nombre="  FIN DE   SEMANA ")

    assert r.status_code == 400
    assert 'Ya existe un mensaje llamado &#34;FIN DE SEMANA&#34;.' in r.text
    assert client.db.query(MensajeEspecial).count() == 1


def test_variable_desconocida_se_rechaza_y_reabre_el_modal_con_lo_escrito(client):
    _login_admin(client)

    r = _crear(client, texto="Hola {recipient_name}, no hay servicio")

    assert r.status_code == 400
    assert "La variable {recipient_name} no existe. Usa: {nombre}, {codigos}." in r.text
    modal = re.search(r'<div[^>]*id="modal-mensaje-especial-nuevo"[^>]*>', r.text).group(0)
    assert " hidden" not in modal  # abierto
    assert "Hola {recipient_name}, no hay servicio</textarea>" in r.text
    assert client.db.query(MensajeEspecial).count() == 0


def test_nombre_y_texto_son_obligatorios(client):
    _login_admin(client)

    assert "El nombre no puede quedar vacío." in _crear(client, nombre="   ").text
    assert "El texto no puede quedar vacío." in _crear(client, texto="  ").text
    assert client.db.query(MensajeEspecial).count() == 0


def test_la_lista_muestra_el_largo_como_sms_resuelto_y_sin_tildes(client):
    # 160 caracteres = 1 SMS: el conteo es el del texto que de verdad sale (variables de ejemplo, sin tildes).
    _login_admin(client)
    _crear(client, nombre="Corto", texto="Hola {nombre}")  # "Hola MARIA PEREZ" = 16
    _crear(client, nombre="Largo", texto="á" * 170)

    seccion = _seccion(client.get(_URL).text)
    assert "16 car." in seccion
    assert "170 car." in seccion


def test_la_vista_previa_del_editor_resuelve_las_variables_con_datos_de_ejemplo():
    from app.domain.aviso_especial_service import vista_previa

    previa = vista_previa("Hola {nombre}, tus paquetes {codigos} esperan el lunes.")

    assert previa["texto"] == "Hola MARIA PEREZ, tus paquetes A1B2, C3D4 esperan el lunes."
    assert previa["caracteres"] == len(previa["texto"])
    assert previa["un_sms"] is True
    assert vista_previa("x" * 161)["un_sms"] is False


def test_crear_deja_la_creacion_en_el_historial_con_el_admin(client):
    admin = _login_admin(client)

    _crear(client, nombre="Festivo", texto="Lunes festivo: sin servicio.")

    historial = client.db.query(MensajeEspecialHistorial).one()
    assert historial.accion.value == "CREADO"
    assert historial.usuario_id == admin.id
    assert (historial.nombre_nuevo, historial.texto_nuevo) == ("Festivo", "Lunes festivo: sin servicio.")
