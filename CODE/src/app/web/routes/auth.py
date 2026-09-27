# -*- coding: utf-8 -*-
"""
Rutas de autenticación de staff — `/ingresar`, `/salir`, `/mi-sesion`.

Login con email + contraseña (server-rendered). La sesión guarda el `usuario_id`;
`current_staff` la lee para producir el actor de las acciones. Mensajes de error
GENÉRICOS (no revelan si el email existe).

También vive aquí `/salir-todo` (Grupo 10, Ronda 2): el header pasó de un
botón de logout por sesión a uno único que cierra AMBAS sesiones
(cliente+staff) si están coexistiendo — mecanismo nuevo, pero las sesiones
siguen siendo cookies/keys independientes por dentro (`/salir` y
`/otp/salir` individuales se conservan intactos, sin cambios).
"""

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.domain.configuracion_conjunto_service import obtener_nombre_conjunto
from app.domain.operador_dispositivo_service import (
    DemasiadosIntentosDePin,
    PinIncorrecto,
    definir_pin,
    desbloquear,
    obtener_o_crear_dispositivo,
    registrar_ingreso,
    tiene_registros_vigentes,
)
from app.domain.usuario import RolUsuario
from app.domain.staff_service import editar_mi_perfil, set_password, verify_credentials
from app.domain.usuario import Usuario

from ..db import get_db
from ..rate_limit import rate_limit
from ..security import (
    CUSTOMER_NOMBRE_SESSION_KEY,
    CUSTOMER_SESSION_KEY,
    NOMBRE_SESSION_KEY,
    ROLE_SESSION_KEY,
    SESION_VERSION_KEY,
    SESSION_KEY,
    abrir_sesion_staff,
    cerrar_sesion_staff,
    current_staff,
    dispositivo_id_de,
    fijar_cookie_dispositivo,
    staff_sin_pin,
)
from ..templating import templates

_MENSAJE_RATE_LIMIT = "Demasiados intentos. Espera un momento e inténtalo de nuevo."

router = APIRouter()


@router.get("/ingresar", response_class=HTMLResponse)
def login_form(request: Request, restablecida: bool = False):
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "restablecida": restablecida}
    )


@router.post("/ingresar")
def login_submit(
    request: Request,
    db: Session = Depends(get_db),
    permitido: bool = Depends(rate_limit("auth_login", 10, 60)),
    email: str = Form(None),
    password: str = Form(None),
):
    def _error():
        # Campos de seguridad (retroalimentación en vivo 2026-08-02): se
        # marcan AMBOS con el mismo mensaje genérico, nunca solo uno --
        # decirle al usuario cuál de los dos falló revelaría si el email
        # existe (mismo principio que el mensaje genérico en sí).
        mensaje = "Email o contraseña incorrectos."
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": mensaje,
                "error_email": mensaje,
                "error_password": mensaje,
                "email": email or "",
            },
            status_code=400,
        )

    if not permitido:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": _MENSAJE_RATE_LIMIT, "email": email or ""},
            status_code=429,
        )

    if not (email or "").strip() or not (password or ""):
        return _error()

    usuario = verify_credentials(db, email, password)
    if usuario is None:
        return _error()

    abrir_sesion_staff(request, usuario)
    # PIN de operador (`.scratch/pin-operador-dispositivo`): entrar con contraseña registra ESTE equipo para el
    # Usuario; sin PIN todavía, lo primero es crearlo.
    dispositivo = obtener_o_crear_dispositivo(db, dispositivo_id_de(request))
    debe_crear_pin = registrar_ingreso(db, dispositivo, usuario)
    # Corrección en vivo 2026-08-02: antes iba a /mi-sesion (ruta de prueba);
    # /paquetes es lo que un staff realmente quiere ver al entrar.
    respuesta = RedirectResponse(
        "/mi-pin" if debe_crear_pin else "/paquetes", status_code=status.HTTP_303_SEE_OTHER
    )
    fijar_cookie_dispositivo(request, respuesta, dispositivo.id)
    return respuesta


def _pantalla_pin(request: Request, usuario: Usuario, error: str | None = None, status_code: int = 200):
    return templates.TemplateResponse(
        "auth/pin.html",
        {"request": request, "usuario": usuario, "tiene_pin": bool(usuario.pin_huella), "error": error},
        status_code=status_code,
    )


@router.get("/mi-pin", response_class=HTMLResponse)
def mi_pin(request: Request, usuario: Usuario = Depends(staff_sin_pin)):
    return _pantalla_pin(request, usuario)


@router.post("/mi-pin")
def mi_pin_guardar(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(staff_sin_pin),
    pin: str = Form(""),
    pin_confirmacion: str = Form(""),
):
    """Crear el PIN (`.scratch/pin-operador-dispositivo`, ticket 02). Quien llega acá sin PIN acaba de entrar con su
    contraseña, así que no se le vuelve a pedir."""
    if usuario.pin_huella:
        return RedirectResponse("/paquetes", status_code=status.HTTP_303_SEE_OTHER)
    if pin != pin_confirmacion:
        return _pantalla_pin(request, usuario, "Los PIN no coinciden.", status_code=400)
    try:
        definir_pin(db, usuario, pin)
    except DemasiadosIntentosDePin as exc:
        return _pantalla_pin(request, usuario, str(exc), status_code=429)
    except ValueError as exc:
        return _pantalla_pin(request, usuario, str(exc), status_code=400)
    return RedirectResponse("/paquetes", status_code=status.HTTP_303_SEE_OTHER)


def _siguiente_seguro(siguiente: str, usuario: Usuario) -> str:
    """A dónde volver tras desbloquear: solo rutas locales, y al inicio si el nuevo Operador no tiene permiso para la
    vista pedida (un OPERADOR sobre Administración)."""
    siguiente = (siguiente or "").strip()
    if not siguiente.startswith("/") or siguiente.startswith("//") or "\\" in siguiente:
        return "/paquetes"
    if siguiente.startswith("/administracion") and usuario.rol != RolUsuario.ADMIN:
        return "/paquetes"
    return siguiente


def _pantalla_bloqueo(request: Request, db: Session, siguiente: str, error: str | None = None, status_code=200):
    return templates.TemplateResponse(
        "auth/bloqueo.html",
        {
            "request": request,
            "nombre_conjunto": obtener_nombre_conjunto(db),
            "siguiente": siguiente,
            "error": error,
        },
        status_code=status_code,
    )


@router.get("/bloqueo", response_class=HTMLResponse)
def pantalla_bloqueo(request: Request, db: Session = Depends(get_db), siguiente: str = "/paquetes"):
    """Pantalla de bloqueo (`.scratch/pin-operador-dispositivo`, ticket 03): nombre del conjunto, teclado del PIN y el
    enlace a usuario y contraseña. Nunca lista a los registrados. Sin registros vigentes en el equipo, no sirve de
    nada: directo a `/ingresar`."""
    if not tiene_registros_vigentes(db, dispositivo_id_de(request)):
        return RedirectResponse("/ingresar", status_code=status.HTTP_303_SEE_OTHER)
    return _pantalla_bloqueo(request, db, siguiente)


@router.post("/bloqueo")
def desbloquear_con_pin(
    request: Request,
    db: Session = Depends(get_db),
    pin: str = Form(""),
    siguiente: str = Form("/paquetes"),
):
    try:
        usuario = desbloquear(db, dispositivo_id_de(request), pin)
    except PinIncorrecto as exc:
        return _pantalla_bloqueo(request, db, siguiente, error=str(exc), status_code=400)
    abrir_sesion_staff(request, usuario)
    return RedirectResponse(_siguiente_seguro(siguiente, usuario), status_code=status.HTTP_303_SEE_OTHER)


@router.post("/bloquear")
def bloquear(request: Request):
    """"Bloquear" del menú: quita al Operador activo, sin tocar los registros del equipo."""
    cerrar_sesion_staff(request)
    return RedirectResponse("/bloqueo", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/salir")
def logout(request: Request):
    # pop, no clear: la sesión de cliente (persona_id) es independiente y no debe
    # cerrarse al cerrar la de staff.
    request.session.pop(SESSION_KEY, None)
    request.session.pop(ROLE_SESSION_KEY, None)
    request.session.pop(NOMBRE_SESSION_KEY, None)
    return RedirectResponse("/ingresar", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/salir-todo")
def logout_todo(request: Request):
    """Cierra la sesión de STAFF y de CLIENTE a la vez, si hay alguna (o
    ambas) abiertas — el único botón de logout que el header muestra ahora
    (Grupo 10, Ronda 2). `pop` de las claves, nunca `request.session.
    clear()`, para no arrastrar por accidente alguna clave futura ajena a
    estas dos sesiones."""
    request.session.pop(SESSION_KEY, None)
    request.session.pop(ROLE_SESSION_KEY, None)
    request.session.pop(NOMBRE_SESSION_KEY, None)
    request.session.pop(CUSTOMER_SESSION_KEY, None)
    request.session.pop(CUSTOMER_NOMBRE_SESSION_KEY, None)
    return RedirectResponse("/anunciar", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/mi-sesion", response_class=HTMLResponse)
def me(request: Request, usuario: Usuario = Depends(current_staff)):
    return templates.TemplateResponse(
        "auth/me.html", {"request": request, "usuario": usuario}
    )


@router.post("/mi-sesion/editar", response_class=HTMLResponse)
def editar_mi_perfil_route(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(current_staff),
    nombre: str = Form(None),
    telefono: str = Form(None),
    whatsapp: str = Form(None),
):
    """Autoservicio (.scratch/pendientes-cliente, issue 197): cualquier
    staff (OPERADOR incluido) edita SU PROPIO nombre. Sin campo de rol en
    este form ni en `editar_mi_perfil` -- a diferencia de
    `admin.admin_staff_editar` (edita nombre+rol de OTRO, exige actor
    ADMIN), acá no hay forma de tocar el rol propio ni manipulando el HTML
    a mano, porque la función de dominio ni siquiera acepta ese parámetro.

    `telefono`/`whatsapp` (.scratch/notificaciones-enviar-prueba, ticket 01):
    contacto propio del staff, opcionales -- ver `editar_mi_perfil`."""
    try:
        editar_mi_perfil(db, usuario, nombre, telefono=telefono, whatsapp=whatsapp)
    except ValueError as exc:
        return templates.TemplateResponse(
            "auth/me.html",
            {"request": request, "usuario": usuario, "error": str(exc), "error_nombre": str(exc)},
            status_code=400,
        )
    return templates.TemplateResponse(
        "auth/me.html", {"request": request, "usuario": usuario, "guardado_nombre": True}
    )


@router.post("/mi-sesion", response_class=HTMLResponse)
def cambiar_mi_password(
    request: Request,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(current_staff),
    password: str = Form(None),
    password_confirmacion: str = Form(None),
):
    """Autoservicio (.scratch/pendientes-cliente, issue 196): cualquier staff
    (OPERADOR incluido) puede cambiar SU PROPIA contraseña -- a diferencia de
    `admin.admin_staff_resetear_password`, que exige actor ADMIN para tocar
    la de OTRO. `set_password` (staff_service.py) no exige actor porque acá
    `usuario` sale de `current_staff` (la sesión), nunca de un campo del
    form -- solo se puede tocar a uno mismo."""
    def _error(mensaje: str, campos: list[str] = None):
        return templates.TemplateResponse(
            "auth/me.html",
            {
                "request": request,
                "usuario": usuario,
                "error": mensaje,
                "error_password": mensaje if "password" in (campos or []) else None,
                "error_password_confirmacion": mensaje if "password_confirmacion" in (campos or []) else None,
            },
            status_code=400,
        )

    if password != password_confirmacion:
        return _error("Las contraseñas no coinciden.", campos=["password", "password_confirmacion"])

    try:
        set_password(db, usuario, password)
    except ValueError as exc:
        return _error(str(exc), campos=["password"])
    # Issue 383: el cambio cierra las sesiones de OTROS equipos, no la de quien lo acaba de hacer -- ni el registro de
    # este equipo (PIN de operador), que se renueva con la versión nueva.
    request.session[SESION_VERSION_KEY] = usuario.sesion_version
    registrar_ingreso(db, obtener_o_crear_dispositivo(db, dispositivo_id_de(request)), usuario)

    return templates.TemplateResponse(
        "auth/me.html", {"request": request, "usuario": usuario, "guardado": True}
    )
