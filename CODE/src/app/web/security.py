# -*- coding: utf-8 -*-
"""
Dependencias de autenticación de la capa web (rebuild PaqueteXv.2).

`current_staff` lee la sesión (cookie firmada), carga el `Usuario` y lo entrega:
es el **actor** de la máquina de estados y la **puerta** de las rutas con
privilegios. `require_admin` añade la exigencia de rol ADMIN. El id del usuario
sale SIEMPRE de la sesión verificada, nunca de un parámetro del cliente.
"""

import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature, Signer
from sqlalchemy.orm import Session

from app.domain.operador_dispositivo_service import registro_vigente
from app.domain.persona import Persona
from app.domain.usuario import RolUsuario, Usuario

from .config import secret_key
from .db import get_db

SESSION_KEY = "usuario_id"
# Clave INDEPENDIENTE de SESSION_KEY: staff y cliente son sesiones separadas que
# coexisten en el mismo navegador sin pisarse (CONTEXT.md: "Usuario = staff;
# Persona/Cliente = residente").
CUSTOMER_SESSION_KEY = "persona_id"
# Dato DERIVADO guardado en sesión al hacer login (ver DEC-09) para que el
# header pueda decidir si mostrar Administración sin una dependencia de BD
# nueva en cada ruta que renderiza una página completa. NUNCA es la fuente de
# autorización real -- `require_admin` (abajo) sigue siendo la única puerta.
ROLE_SESSION_KEY = "rol"
# Issue 383 (.scratch/pendientes-cliente): versión de sesión del Usuario con la que se abrió esta sesión (ver
# `Usuario.sesion_version`). Una cookie de antes de este cambio no la trae: cuenta como 0, la versión inicial.
SESION_VERSION_KEY = "sesion_version"
# Mismo espíritu que ROLE_SESSION_KEY: el nombre para pintar el avatar/trigger
# de cuenta del header (Grupo "header producción") sin una dependencia de BD
# nueva en base.html. Dato derivado para UI únicamente -- si el nombre real
# cambia, se refleja en el próximo login, igual que el rol. DOS claves
# separadas (no una compartida) porque cliente y staff son sesiones
# independientes que pueden coexistir -- una clave única haría que la
# segunda sesión en loguearse pisara el nombre de la primera.
NOMBRE_SESSION_KEY = "nombre"
CUSTOMER_NOMBRE_SESSION_KEY = "persona_nombre"


# Dispositivo registrado (`.scratch/pin-operador-dispositivo`): cookie PROPIA del equipo, firmada, independiente de la
# de sesión -- identifica el navegador aunque la sesión venza o se cierre, y es lo que hace que un PIN solo valga donde
# su dueño entró con contraseña. Su vida es larga a propósito: la vigencia real de cada registro la decide el servidor
# con los días configurados.
COOKIE_DISPOSITIVO = "paquetex_dispositivo"
_DURACION_COOKIE_DISPOSITIVO_SEGUNDOS = 365 * 24 * 60 * 60


def _firmador_dispositivo() -> Signer:
    return Signer(secret_key(), salt="paquetex-dispositivo")


def dispositivo_id_de(request: Request) -> uuid.UUID | None:
    """El id del equipo según su cookie firmada, o `None` si no hay cookie o la firma no cuadra."""
    crudo = request.cookies.get(COOKIE_DISPOSITIVO)
    if not crudo:
        return None
    try:
        return uuid.UUID(_firmador_dispositivo().unsign(crudo).decode("ascii"))
    except (BadSignature, ValueError, UnicodeDecodeError):
        return None


def fijar_cookie_dispositivo(request: Request, response, dispositivo_id) -> None:
    """`Secure` con el mismo criterio que la cookie de sesión, decidido al crear el app (`create_app`)."""
    response.set_cookie(
        COOKIE_DISPOSITIVO,
        _firmador_dispositivo().sign(str(dispositivo_id)).decode("ascii"),
        max_age=_DURACION_COOKIE_DISPOSITIVO_SEGUNDOS,
        httponly=True,
        samesite="lax",
        secure=getattr(request.app.state, "cookies_seguras", False),
    )


class RedireccionStaff(Exception):
    """Una puerta de staff que no niega el acceso sino que lo desvía (ej. "Crea tu PIN"). El app la convierte en un
    303 hacia `destino`."""

    def __init__(self, destino: str):
        self.destino = destino


def staff_sin_pin(request: Request, db: Session = Depends(get_db)) -> Usuario:
    """El `Usuario` de la sesión actual, sin exigir que ya tenga PIN -- solo para la pantalla que lo crea.
    Sin sesión válida → 401.

    Un 401 lo convierte el app en un redirect a `/ingresar` (ver app factory).
    """
    raw = request.session.get(SESSION_KEY)
    if not raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    try:
        usuario_id = uuid.UUID(str(raw))
    except (ValueError, TypeError):
        request.session.pop(SESSION_KEY, None)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")

    usuario = db.get(Usuario, usuario_id)
    if usuario is not None and request.session.get(SESION_VERSION_KEY, 0) != (usuario.sesion_version or 0):
        # Issue 383: la contraseña cambió después de abrir esta sesión -- otro equipo, o un restablecimiento.
        usuario = None
    if usuario is not None and not registro_vigente(db, dispositivo_id_de(request), usuario):
        # PIN de operador: la sesión solo vale en un equipo donde este Usuario tiene un registro vigente (vence por
        # días configurados, o por "Cerrar en todos los dispositivos").
        usuario = None
    if usuario is None or not usuario.activo:
        # `activo` se relee de la BD en CADA request (sin caché, mismo
        # criterio que ya aplicaba el rol -- ver ROLE_SESSION_KEY arriba):
        # un ADMIN que desactiva a alguien con sesión YA abierta corta su
        # acceso en el siguiente request, no recién en su próximo login
        # (hueco real encontrado en auditoría, .scratch/pendientes-cliente
        # -- antes `activo` solo se chequeaba en `staff_service.autenticar`).
        request.session.pop(SESSION_KEY, None)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")
    return usuario


def current_staff(request: Request, usuario: Usuario = Depends(staff_sin_pin)) -> Usuario:
    """El `Usuario` de la sesión actual: el actor de las acciones y la puerta de las rutas con privilegios.
    Sin sesión válida → 401; sin PIN todavía → a "Crea tu PIN" (nadie opera sin identidad rápida)."""
    if not usuario.pin_huella:
        raise RedireccionStaff("/mi-pin")
    return usuario


def require_admin(usuario: Usuario = Depends(current_staff)) -> Usuario:
    """Como `current_staff`, pero exige rol ADMIN. Si no → 403."""
    if usuario.rol != RolUsuario.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Requiere rol ADMIN")
    return usuario


def current_customer(request: Request, db: Session = Depends(get_db)) -> Persona:
    """La `Persona` de la sesión de CLIENTE actual (independiente de `current_staff`).

    Sin sesión válida → 401. El id sale SIEMPRE de la sesión verificada, nunca de
    un parámetro del cliente.
    """
    raw = request.session.get(CUSTOMER_SESSION_KEY)
    if not raw:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    try:
        persona_id = uuid.UUID(str(raw))
    except (ValueError, TypeError):
        request.session.pop(CUSTOMER_SESSION_KEY, None)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")

    persona = db.get(Persona, persona_id)
    if persona is None:
        request.session.pop(CUSTOMER_SESSION_KEY, None)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida")
    return persona


def gate_bloqueado(persona: Persona) -> RedirectResponse | None:
    """`None` si `persona` puede usar el portal del cliente con normalidad;
    si sigue bloqueada (`bloqueado_en` seteado -- incluso con desbloqueo
    autorizado, todavía no aceptó términos), un redirect a la pantalla de
    aceptar términos en vez de lo que sea que la ruta iba a hacer
    (.scratch/bloquear-clientes, ticket 04). Mismo patrón que
    `customer_verify._gate_no_verificado`: la ruta llama esto primero y
    retorna temprano si no es `None`.

    NUNCA se llama desde la propia pantalla de aceptar términos -- esa
    sigue accesible con `bloqueado_en` seteado, es la única forma de salir
    de ese estado."""
    if persona.bloqueado_en is not None:
        return RedirectResponse("/mis-datos/aceptar-terminos", status_code=status.HTTP_303_SEE_OTHER)
    return None
