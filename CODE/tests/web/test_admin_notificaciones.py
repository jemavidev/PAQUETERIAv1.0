# -*- coding: utf-8 -*-
"""
Capa web — `/administracion/notificaciones` (Grupo 8, ticket 02).

Comportamiento observable por HTTP: gate require_admin (mismo patrón que
`/administracion/personal`); sin plantilla previa, el campo muestra el texto
por defecto; guardar persiste la plantilla personalizada.
"""

from app.domain.notificacion_service import obtener_asunto_actual, obtener_texto_actual
from app.domain.paquete import EstadoPaquete
from app.domain.preferencia_notificacion import CanalNotificacion
from app.domain.staff_service import create_initial_admin, create_staff
from app.domain.usuario import RolUsuario

_PW = "Contrasena1"


def _login_admin(client, email="admin@club.com"):
    create_initial_admin(client.db, email, "Admin", _PW)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})


def _login_operador(client, email="op@club.com"):
    admin = create_initial_admin(client.db, "admin@club.com", "Admin", _PW)
    create_staff(client.db, admin, email, "Opa", _PW, RolUsuario.OPERADOR)
    client.db.commit()
    client.post("/ingresar", data={"email": email, "password": _PW})


def test_sin_sesion_redirige_a_login(client):
    r = client.get("/administracion/notificaciones", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].endswith("/ingresar")


def test_operador_es_rechazado_403(client):
    _login_operador(client)
    r = client.get("/administracion/notificaciones")
    assert r.status_code == 403


def test_admin_ve_las_plantillas_con_el_texto_por_defecto(client):
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert r.status_code == 200
    assert "ya está en portería" in r.text  # default de RECIBIDO, sin override


def test_guardar_persiste_la_plantilla_personalizada(client):
    _login_admin(client)
    r = client.post(
        "/administracion/notificaciones",
        data={
            "evento": "RECIBIDO",
            "motivo": "",
            "texto": "Hola {recipient_name}, ya llegó tu encomienda.",
        },
    )
    assert r.status_code == 200
    assert "ya llegó tu encomienda" in r.text

    client.db.expire_all()
    texto = obtener_texto_actual(client.db, EstadoPaquete.RECIBIDO)
    assert texto == "Hola {recipient_name}, ya llegó tu encomienda."


def test_guardar_con_motivo_solo_afecta_ese_motivo(client):
    _login_admin(client)
    client.post(
        "/administracion/notificaciones",
        data={
            "evento": "CANCELADO",
            "motivo": "NO_RECLAMADO",
            "texto": "Tu paquete {recipient_name} no fue reclamado a tiempo.",
        },
    )

    client.db.expire_all()
    texto_no_reclamado = obtener_texto_actual(
        client.db, EstadoPaquete.CANCELADO, "NO_RECLAMADO"
    )
    texto_otro = obtener_texto_actual(client.db, EstadoPaquete.CANCELADO, "OTRO")

    assert "no fue reclamado a tiempo" in texto_no_reclamado
    assert "no fue reclamado a tiempo" not in texto_otro


def test_texto_vacio_rechaza(client):
    _login_admin(client)
    r = client.post(
        "/administracion/notificaciones",
        data={"evento": "RECIBIDO", "motivo": "", "texto": "   "},
    )
    assert r.status_code == 400


# --------------------------------------------------------------------------- #
# Grupo 19 (Ronda 2) — plantilla Anunciado dividida Cliente/Staff.
# --------------------------------------------------------------------------- #
def test_admin_ve_dos_filas_de_anunciado_cliente_y_staff(client):
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert r.status_code == 200
    assert "ANUNCIADO · Cliente" in r.text
    assert "ANUNCIADO · Staff" in r.text


def test_defaults_de_anunciado_cliente_y_staff_son_distintos(client):
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert "Anunciaste un paquete" in r.text  # default CLIENTE
    assert "Portería anunció un paquete a tu nombre" in r.text  # default STAFF


def test_guardar_anunciado_cliente_no_afecta_anunciado_staff(client):
    _login_admin(client)
    client.post(
        "/administracion/notificaciones",
        data={
            "evento": "ANUNCIADO",
            "motivo": "CLIENTE",
            "texto": "Gracias por anunciar, {recipient_name}.",
        },
    )

    client.db.expire_all()
    from app.domain.notificacion_service import (
        ORIGEN_ANUNCIO_CLIENTE,
        ORIGEN_ANUNCIO_STAFF,
    )

    texto_cliente = obtener_texto_actual(
        client.db, EstadoPaquete.ANUNCIADO, ORIGEN_ANUNCIO_CLIENTE
    )
    texto_staff = obtener_texto_actual(
        client.db, EstadoPaquete.ANUNCIADO, ORIGEN_ANUNCIO_STAFF
    )
    assert "Gracias por anunciar" in texto_cliente
    assert "Gracias por anunciar" not in texto_staff


def test_notificar_anunciado_por_cliente_usa_la_plantilla_de_cliente(client):
    from app.domain.notification_sender import ConsoleNotificationSender
    from app.domain.notificacion_service import notificar_evento
    from app.domain.paquete_service import Destinatario, announce

    p = announce(
        client.db,
        anunciante_telefono="3001234567",
        anunciante_nombre="Ana",
        destinatario=Destinatario.yo_mismo(),
    )
    client.db.commit()

    sender = ConsoleNotificationSender()
    notificar_evento(client.db, p, EstadoPaquete.ANUNCIADO, sender)

    assert len(sender.enviados) == 1
    assert "Anunciaste un paquete" in sender.enviados[0][1]


# --------------------------------------------------------------------------- #
# `.scratch/plantillas-notificacion-multicanal`, ticket 02 — pestañas
# SMS/Email/WhatsApp por evento.
# --------------------------------------------------------------------------- #
def test_pantalla_muestra_3_pestanas_por_cada_una_de_las_8_filas(client):
    # 8 filas: ANUNCIADO x2 (Cliente/Staff) + RECIBIDO + ENTREGADO +
    # CANCELADO x4 (un MotivoCancelacion cada una).
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert r.status_code == 200
    for canal in ("SMS", "EMAIL", "WHATSAPP"):
        assert r.text.count(f'data-canal="{canal}"') == 8


def test_guardar_email_no_afecta_el_sms_del_mismo_evento(client):
    _login_admin(client)
    r = client.post(
        "/administracion/notificaciones",
        data={
            "evento": "RECIBIDO",
            "motivo": "",
            "canal": "EMAIL",
            "asunto": "Tu paquete llegó a portería",
            "texto": "Cuerpo de correo personalizado.",
        },
    )
    assert r.status_code == 200

    client.db.expire_all()
    texto_email = obtener_texto_actual(
        client.db, EstadoPaquete.RECIBIDO, canal=CanalNotificacion.EMAIL
    )
    asunto_email = obtener_asunto_actual(client.db, EstadoPaquete.RECIBIDO)
    texto_sms = obtener_texto_actual(client.db, EstadoPaquete.RECIBIDO)  # default canal=SMS

    assert texto_email == "Cuerpo de correo personalizado."
    assert asunto_email == "Tu paquete llegó a portería"
    assert "portería" in texto_sms  # sigue siendo el default de SMS, sin tocar


def test_asunto_vacio_en_email_rechaza_sin_borrar_el_existente(client):
    _login_admin(client)
    client.post(
        "/administracion/notificaciones",
        data={
            "evento": "RECIBIDO",
            "motivo": "",
            "canal": "EMAIL",
            "asunto": "Asunto original",
            "texto": "Cuerpo original.",
        },
    )

    r = client.post(
        "/administracion/notificaciones",
        data={
            "evento": "RECIBIDO",
            "motivo": "",
            "canal": "EMAIL",
            "asunto": "   ",
            "texto": "Cuerpo nuevo.",
        },
    )
    assert r.status_code == 400

    client.db.expire_all()
    assert obtener_asunto_actual(client.db, EstadoPaquete.RECIBIDO) == "Asunto original"


def _primer_srcdoc(html_text):
    inicio = html_text.index('srcdoc="') + len('srcdoc="')
    fin = html_text.index('"', inicio)
    return html_text[inicio:fin]


def test_pestana_email_muestra_preview_con_datos_de_ejemplo(client):
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert r.status_code == 200
    preview = _primer_srcdoc(r.text)
    # Datos de ejemplo (variables_ejemplo) resueltos dentro del preview --
    # nunca el placeholder crudo.
    assert "Juan Pérez" in preview
    assert "{recipient_name}" not in preview
    assert "papyrus-logo.png" in preview
    assert "Consultar mis paquetes" in preview


def test_preview_de_un_evento_cancelado_usa_su_propio_motivo(client):
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    # CANCELADO·NO_RECLAMADO trae {motivo} en su default -- el preview de
    # ESA fila debe resolverlo a "No reclamado" (variables_ejemplo).
    i = r.text.index("CANCELADO · No reclamado")
    bloque = r.text[i : i + 8000]
    preview = _primer_srcdoc(bloque)
    assert "No reclamado" in preview
    assert "{motivo}" not in preview


def test_canal_invalido_rechaza(client):
    _login_admin(client)
    r = client.post(
        "/administracion/notificaciones",
        data={"evento": "RECIBIDO", "motivo": "", "canal": "FAX", "texto": "texto"},
    )
    assert r.status_code == 400


def test_pestana_email_tiene_asunto_y_no_la_lista_de_variables(client):
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert r.text.count('aria-label="Asunto"') == 8
    # "Variables disponibles" solo se muestra en SMS/WhatsApp -- 2 de los 3
    # canales, en cada una de las 8 filas.
    assert r.text.count("Variables disponibles") == 16


def test_notificar_anunciado_por_staff_usa_la_plantilla_de_staff(client):
    from app.domain.notification_sender import ConsoleNotificationSender
    from app.domain.notificacion_service import notificar_evento
    from app.domain.paquete_service import Destinatario, announce
    from app.domain.usuario import Usuario

    _login_admin(client)
    admin = client.db.query(Usuario).one()

    p = announce(
        client.db,
        anunciante_telefono="3001234567",
        anunciante_nombre="Ana",
        destinatario=Destinatario.yo_mismo(),
        staff_actor=admin,
    )
    client.db.commit()

    sender = ConsoleNotificationSender()
    notificar_evento(client.db, p, EstadoPaquete.ANUNCIADO, sender)

    assert len(sender.enviados) == 1
    assert "Portería anunció un paquete a tu nombre" in sender.enviados[0][1]
