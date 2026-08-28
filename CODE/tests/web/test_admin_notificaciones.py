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
# issue 202 (.scratch/pendientes-cliente): ANUNCIADO deja de distinguir
# Cliente/Staff (Grupo 19, Ronda 2, revertido) -- el aviso siempre llega al
# mismo destinatario final sin importar quién anunció, así que sobraba
# tener dos plantillas separadas. Ahora se comporta igual que RECIBIDO/
# ENTREGADO: una sola fila, sin motivo.
# --------------------------------------------------------------------------- #
def test_admin_ve_una_sola_fila_de_anunciado_sin_motivo(client):
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert r.status_code == 200
    assert ">ANUNCIADO<" in r.text
    assert "ANUNCIADO · Cliente" not in r.text
    assert "ANUNCIADO · Staff" not in r.text


def test_notificar_anunciado_usa_la_misma_plantilla_sin_importar_quien_anuncio(client):
    from app.domain.notification_sender import ConsoleNotificationSender
    from app.domain.notificacion_service import notificar_evento
    from app.domain.paquete_service import Destinatario, announce
    from app.domain.usuario import Usuario

    _login_admin(client)
    admin = client.db.query(Usuario).one()

    p_cliente = announce(
        client.db,
        anunciante_telefono="3001234567",
        anunciante_nombre="Ana",
        destinatario=Destinatario.yo_mismo(),
    )
    p_staff = announce(
        client.db,
        anunciante_telefono="3009999999",
        anunciante_nombre="Beto",
        destinatario=Destinatario.yo_mismo(),
        staff_actor=admin,
    )
    client.db.commit()

    sender = ConsoleNotificationSender()
    notificar_evento(client.db, p_cliente, EstadoPaquete.ANUNCIADO, sender)
    notificar_evento(client.db, p_staff, EstadoPaquete.ANUNCIADO, sender)

    assert len(sender.enviados) == 2
    assert "Anunciaste un paquete" in sender.enviados[0][1]
    assert "Anunciaste un paquete" in sender.enviados[1][1]  # mismo texto


# --------------------------------------------------------------------------- #
# `.scratch/plantillas-notificacion-multicanal`, ticket 02 — pestañas
# SMS/Email/WhatsApp por evento.
# --------------------------------------------------------------------------- #
def test_pantalla_muestra_3_pestanas_por_cada_una_de_las_7_filas(client):
    # 7 filas: ANUNCIADO + RECIBIDO + ENTREGADO + CANCELADO x4 (un
    # MotivoCancelacion cada una) -- ANUNCIADO dejó de distinguir
    # Cliente/Staff en issue 202 (.scratch/pendientes-cliente).
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert r.status_code == 200
    for canal in ("SMS", "EMAIL", "WHATSAPP"):
        assert r.text.count(f'data-canal="{canal}"') == 7


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
    assert r.text.count('aria-label="Asunto"') == 7
    # "Variables disponibles" solo se muestra en SMS/WhatsApp -- 2 de los 3
    # canales, en cada una de las 7 filas.
    assert r.text.count("Variables disponibles") == 14


# --------------------------------------------------------------------------- #
# .scratch/plantillas-notificacion-multicanal / pendientes-cliente issue 200
# -- layout de acordeón (elegido tras prototipar 3 alternativas en vivo).
# --------------------------------------------------------------------------- #
def _tag_details_de(html_text, titulo_summary):
    """El `<details ...>` cuyo `<summary>` contiene `titulo_summary` como
    texto (ej. 'RECIBIDO' o 'ANUNCIADO · Cliente')."""
    i = html_text.index(f">{titulo_summary}<")
    inicio = html_text.rindex("<details", 0, i)
    fin = html_text.index(">", inicio)
    return html_text[inicio : fin + 1]


def test_primera_fila_abierta_las_demas_cerradas_por_defecto(client):
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert "open" in _tag_details_de(r.text, "ANUNCIADO")  # la primera
    assert "open" not in _tag_details_de(r.text, "RECIBIDO")


def test_error_en_fila_no_primera_abre_su_propio_acordeon(client):
    _login_admin(client)
    r = client.post(
        "/administracion/notificaciones",
        data={"evento": "RECIBIDO", "motivo": "", "canal": "SMS", "texto": "   "},
    )
    assert r.status_code == 400
    assert "open" in _tag_details_de(r.text, "RECIBIDO")
    # issue 202: un solo acordeón abierto a la vez -- la primera fila NO
    # debe quedar abierta también solo porque es la primera.
    assert "open" not in _tag_details_de(r.text, "ANUNCIADO")


def test_details_comparten_name_para_ser_exclusivos(client):
    # issue 202: `name` compartido -- soporte nativo del navegador para que
    # abrir uno cierre cualquier otro del mismo grupo, sin JS.
    _login_admin(client)
    r = client.get("/administracion/notificaciones")
    assert r.text.count('name="notif-acordeon"') == 7


def test_guardar_en_fila_no_primera_abre_su_propio_acordeon(client):
    _login_admin(client)
    r = client.post(
        "/administracion/notificaciones",
        data={"evento": "RECIBIDO", "motivo": "", "canal": "SMS", "texto": "Ya llegó."},
    )
    assert r.status_code == 200
    assert "open" in _tag_details_de(r.text, "RECIBIDO")
