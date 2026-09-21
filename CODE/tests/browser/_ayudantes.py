# -*- coding: utf-8 -*-
"""
Ayudantes del seam de navegador real (`conftest.py` de esta carpeta explica cómo correrlo).

Ninguno importa Playwright: reciben la `pagina` (una `Page` de Playwright) ya creada por el fixture,
así que importar este módulo es barato y seguro aun sin Playwright instalado (la suite por defecto
recoge estas pruebas para deseleccionarlas, no para ejecutarlas).
"""

from app.domain.paquete import Paquete
from app.domain.paquete_lifecycle import receive
from app.domain.paquete_service import Destinatario, announce
from app.domain.staff_service import create_initial_admin
from app.domain.usuario import Usuario

PASSWORD_STAFF = "Contrasena1"
EMAIL_STAFF = "staff@club.com"


def iniciar_sesion_staff(pagina, app_viva, email=EMAIL_STAFF):
    """Crea un Operador/Admin en la BD de la prueba y deja `pagina` con su sesión iniciada.

    El login va por HTTP con el contexto del navegador (las cookies de la respuesta quedan en la
    misma sesión de la `pagina`): más rápido que llenar el formulario y no es lo que se prueba acá.
    """
    create_initial_admin(app_viva.db, email, "Staff", PASSWORD_STAFF)
    app_viva.db.commit()
    respuesta = pagina.context.request.post(
        f"{app_viva.url}/ingresar",
        form={"email": email, "password": PASSWORD_STAFF},
        max_redirects=0,
    )
    assert respuesta.status == 303, f"el login de Staff no redirigió (status {respuesta.status})"


def anunciar_paquete(app_viva, tel="3001234567", nombre="Ana"):
    """Deja un Paquete `Anunciado` (destinatario: el propio Anunciante) y lo devuelve."""
    p = announce(
        app_viva.db,
        anunciante_telefono=tel,
        anunciante_nombre=nombre,
        destinatario=Destinatario.yo_mismo(),
    )
    app_viva.db.commit()
    return p


def paquete_en_bd(app_viva, paquete_id):
    """El Paquete tal como está AHORA en la BD (fuente de verdad de qué se envió de verdad)."""
    app_viva.db.expire_all()
    return app_viva.db.get(Paquete, paquete_id)


def abrir_modal_recibir(pagina, app_viva, paquete):
    """Va a /paquetes y abre el modal Recibir de `paquete` con un clic real sobre su botón."""
    modal_id = f"modal-receive-{paquete.id}"
    pagina.goto(f"{app_viva.url}/paquetes")
    pagina.locator(f'[data-open="{modal_id}"]:visible').first.click()
    pagina.wait_for_function("id => !document.getElementById(id).hidden", arg=modal_id)


def recibir_paquete_en_bd(app_viva, paquete, guia, email=EMAIL_STAFF):
    """Deja el Paquete `Recibido` con `guia` directo en el dominio (para probar Entregar sin pasar por Recibir)."""
    staff = app_viva.db.query(Usuario).filter(Usuario.email == email).one()
    receive(app_viva.db, paquete, staff, guia)
    app_viva.db.commit()


def abrir_modal_entregar(pagina, app_viva, paquete):
    """Va a /paquetes (Recibidos) y abre el modal Entregar de `paquete` con un clic real."""
    modal_id = f"modal-deliver-{paquete.id}"
    pagina.goto(f"{app_viva.url}/paquetes?estado=RECIBIDO")
    pagina.locator(f'[data-open="{modal_id}"]:visible').first.click()
    pagina.wait_for_function("id => !document.getElementById(id).hidden", arg=modal_id)
