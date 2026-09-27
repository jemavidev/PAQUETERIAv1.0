# -*- coding: utf-8 -*-
"""
Servicio del Operador del dispositivo — PIN de operador en equipos compartidos (`.scratch/pin-operador-dispositivo`).

Varios Usuarios comparten un equipo. Cada uno entra UNA vez con contraseña (eso registra el equipo para él) y a partir
de ahí se identifica con su PIN: 4 dígitos, elegido por él, único entre todos los Usuarios, válido solo en los equipos
donde está registrado. Sin HTTP: la capa web decide cookies y redirecciones.

Reloj a nivel de módulo (`_ahora`), reemplazable en las pruebas -- mismo patrón que `paquete_lifecycle._now`.
"""

import hashlib
import hmac
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .configuracion_conjunto_service import obtener_seguridad_sesion
from .dispositivo import Dispositivo, EventoSeguridad, RegistroDispositivo, TipoEventoSeguridad
from .usuario import RolUsuario, Usuario

_PIN_RE = re.compile(r"^\d{4}$")
# Límite de cambios de PIN rechazados por "ya existe": exigir unicidad confirma que ese PIN es de alguien, así que se
# limita el sondeo (grilling 2026-09-27).
MAX_PIN_REPETIDOS_POR_HORA = 3
# PIN incorrectos seguidos que un equipo tolera antes de exigir usuario y contraseña (grilling 2026-09-27).
MAX_PIN_FALLIDOS = 5


class PinNoDisponible(ValueError):
    """El PIN elegido ya es de otro Usuario."""


class DemasiadosIntentosDePin(ValueError):
    """Se agotaron los cambios de PIN rechazados de la última hora."""


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _llave_pin() -> bytes:
    """Llave HMAC del PIN, independiente de la de la cookie de sesión. Obligatoria en producción."""
    llave = os.environ.get("PIN_SECRET_KEY")
    if llave:
        return llave.encode("utf-8")
    if os.environ.get("WEB_ENV") == "production":
        raise RuntimeError("PIN_SECRET_KEY es obligatorio en producción.")
    return b"dev-insecure-pin-solo-desarrollo"


def huella_pin(pin: str) -> str:
    return hmac.new(_llave_pin(), pin.encode("utf-8"), hashlib.sha256).hexdigest()


def validar_formato_pin(pin: str) -> str:
    pin = (pin or "").strip()
    if not _PIN_RE.match(pin):
        raise ValueError("El PIN debe tener exactamente 4 dígitos.")
    return pin


# --------------------------------------------------------------------------- #
# Dispositivo y registros
# --------------------------------------------------------------------------- #
def obtener_dispositivo(session: Session, dispositivo_id) -> Dispositivo | None:
    if dispositivo_id is None:
        return None
    try:
        return session.get(Dispositivo, uuid.UUID(str(dispositivo_id)))
    except (ValueError, TypeError):
        return None


def obtener_o_crear_dispositivo(session: Session, dispositivo_id) -> Dispositivo:
    dispositivo = obtener_dispositivo(session, dispositivo_id)
    if dispositivo is None:
        ahora = _ahora()
        dispositivo = Dispositivo(creado_en=ahora, ultimo_uso_en=ahora)
        session.add(dispositivo)
        session.flush()
    return dispositivo


@dataclass(frozen=True)
class ResultadoIngreso:
    # Todavía no tiene PIN: lo primero es crearlo.
    debe_crear_pin: bool
    # Entró con contraseña en un equipo que había dejado de aceptar PIN por intentos fallidos (ticket 07): cambia su
    # PIN (puede dejar el mismo) antes de seguir.
    debe_cambiar_pin: bool


def registrar_ingreso(session: Session, dispositivo: Dispositivo, usuario: Usuario) -> ResultadoIngreso:
    """Tras verificar la contraseña: registra (o renueva) el equipo para `usuario` y pone en cero los intentos de PIN
    fallidos del equipo."""
    debe_cambiar_pin = (dispositivo.intentos_pin_fallidos or 0) >= MAX_PIN_FALLIDOS
    ahora = _ahora()
    registro = session.get(RegistroDispositivo, (dispositivo.id, usuario.id))
    if registro is None:
        registro = RegistroDispositivo(dispositivo_id=dispositivo.id, usuario_id=usuario.id)
        session.add(registro)
    registro.registrado_en = ahora
    registro.registros_version = usuario.registros_version or 0
    dispositivo.intentos_pin_fallidos = 0
    dispositivo.ultimo_uso_en = ahora
    session.flush()
    return ResultadoIngreso(
        debe_crear_pin=not usuario.pin_huella, debe_cambiar_pin=bool(usuario.pin_huella) and debe_cambiar_pin
    )


def registro_vigente(session: Session, dispositivo_id, usuario: Usuario) -> bool:
    """¿`usuario` tiene un registro vigente en este equipo? Vence por los días configurados (leídos en cada llamada,
    así que acortarlos aplica de inmediato) o si su versión de registros subió desde que se registró."""
    if dispositivo_id is None or not usuario.activo:
        return False
    # Sin buscar el Dispositivo aparte: la FK del registro ya garantiza que existe (una consulta menos por petición).
    registro = session.get(RegistroDispositivo, (dispositivo_id, usuario.id))
    if registro is None or registro.registros_version != (usuario.registros_version or 0):
        return False
    dias = obtener_seguridad_sesion(session).dias_registro_dispositivo
    return _ahora() - registro.registrado_en < timedelta(days=dias)


# --------------------------------------------------------------------------- #
# PIN
# --------------------------------------------------------------------------- #
def _pin_repetidos_recientes(session: Session, usuario: Usuario) -> int:
    return (
        session.query(EventoSeguridad)
        .filter(
            EventoSeguridad.tipo == TipoEventoSeguridad.PIN_REPETIDO,
            EventoSeguridad.usuario_id == usuario.id,
            EventoSeguridad.creado_en > _ahora() - timedelta(hours=1),
        )
        .count()
    )


def definir_pin(session: Session, usuario: Usuario, pin: str) -> None:
    """Fija el PIN de `usuario`. Puede repetir el que ya tenía.

    Raises:
        ValueError: si no son exactamente 4 dígitos.
        DemasiadosIntentosDePin: si ya acumuló `MAX_PIN_REPETIDOS_POR_HORA` rechazos por "ya existe" en la última hora.
        PinNoDisponible: si el PIN es de otro Usuario (el rechazo queda registrado para el límite).
    """
    pin = validar_formato_pin(pin)
    if _pin_repetidos_recientes(session, usuario) >= MAX_PIN_REPETIDOS_POR_HORA:
        raise DemasiadosIntentosDePin("Demasiados intentos. Espera una hora e inténtalo de nuevo.")

    huella = huella_pin(pin)
    dueno = session.query(Usuario).filter(Usuario.pin_huella == huella, Usuario.id != usuario.id).first()
    if dueno is None:
        usuario.pin_huella = huella
        usuario.pin_actualizado_en = _ahora()
        try:
            with session.begin_nested():
                session.flush()
            return
        except IntegrityError:
            # Carrera: otro Usuario tomó el mismo PIN entre la consulta y el flush.
            session.refresh(usuario)
    session.add(
        EventoSeguridad(tipo=TipoEventoSeguridad.PIN_REPETIDO, usuario_id=usuario.id, creado_en=_ahora())
    )
    session.flush()
    raise PinNoDisponible("Ese PIN no está disponible. Elige otro.")


# --------------------------------------------------------------------------- #
# Desbloqueo
# --------------------------------------------------------------------------- #
class PinIncorrecto(ValueError):
    """El PIN no corresponde a ningún Usuario registrado en este equipo. Un solo mensaje para todos los casos: no
    revela si el PIN existe en otro equipo."""


def tiene_registros_vigentes(session: Session, dispositivo_id) -> bool:
    """¿Alguien puede desbloquear este equipo con su PIN? Si no, la pantalla de bloqueo no sirve y se va a
    `/ingresar`."""
    if dispositivo_id is None:
        return False
    registros = (
        session.query(RegistroDispositivo, Usuario)
        .join(Usuario, Usuario.id == RegistroDispositivo.usuario_id)
        .filter(RegistroDispositivo.dispositivo_id == dispositivo_id, Usuario.activo.is_(True))
        .all()
    )
    return any(registro_vigente(session, dispositivo_id, usuario) for _registro, usuario in registros)


class EquipoRequiereContrasena(PinIncorrecto):
    """El equipo acumuló `MAX_PIN_FALLIDOS` PIN incorrectos seguidos: no acepta ningún PIN (ni el correcto) hasta que
    alguien entre con su contraseña."""


def acepta_pin(session: Session, dispositivo_id) -> bool:
    """¿La pantalla de bloqueo le sirve a este equipo? Hace falta alguien que pueda desbloquearlo con su PIN, y que el
    equipo no haya agotado sus intentos."""
    dispositivo = obtener_dispositivo(session, dispositivo_id)
    if dispositivo is None or (dispositivo.intentos_pin_fallidos or 0) >= MAX_PIN_FALLIDOS:
        return False
    return tiene_registros_vigentes(session, dispositivo.id)


def desbloquear(session: Session, dispositivo_id, pin: str) -> Usuario:
    """El Usuario dueño de `pin`, si tiene un registro vigente en este equipo -- el nuevo Operador activo.

    Raises:
        EquipoRequiereContrasena: si el equipo ya agotó sus intentos, o si este fallo es el que los agota (queda
            registrado como evento de seguridad para el aviso al ADMIN).
        PinIncorrecto: en cualquier otro caso de rechazo.
    """
    dispositivo = obtener_dispositivo(session, dispositivo_id)
    if dispositivo is not None and (dispositivo.intentos_pin_fallidos or 0) >= MAX_PIN_FALLIDOS:
        raise EquipoRequiereContrasena(_MENSAJE_REQUIERE_CONTRASENA)
    usuario = None
    if dispositivo is not None and _PIN_RE.match((pin or "").strip()):
        usuario = session.query(Usuario).filter(Usuario.pin_huella == huella_pin(pin.strip())).first()
    if usuario is None or not registro_vigente(session, dispositivo.id, usuario):
        if dispositivo is not None:
            dispositivo.intentos_pin_fallidos = (dispositivo.intentos_pin_fallidos or 0) + 1
            if dispositivo.intentos_pin_fallidos >= MAX_PIN_FALLIDOS:
                session.add(
                    EventoSeguridad(
                        tipo=TipoEventoSeguridad.BLOQUEO_POR_INTENTOS, dispositivo_id=dispositivo.id, creado_en=_ahora()
                    )
                )
                session.flush()
                raise EquipoRequiereContrasena(_MENSAJE_REQUIERE_CONTRASENA)
            session.flush()
        raise PinIncorrecto("PIN incorrecto.")
    dispositivo.intentos_pin_fallidos = 0
    dispositivo.ultimo_uso_en = _ahora()
    session.flush()
    return usuario


_MENSAJE_REQUIERE_CONTRASENA = "Demasiados intentos. Ingresa con tu usuario y contraseña."


def bloqueos_por_intentos_recientes(session: Session, limite: int = 10) -> list[EventoSeguridad]:
    """Los últimos bloqueos de equipos por PIN incorrectos, más reciente primero (aviso en `/administracion/personal`)."""
    return (
        session.query(EventoSeguridad)
        .filter(EventoSeguridad.tipo == TipoEventoSeguridad.BLOQUEO_POR_INTENTOS)
        .order_by(EventoSeguridad.creado_en.desc())
        .limit(limite)
        .all()
    )


# --------------------------------------------------------------------------- #
# Revocación (ticket 08)
# --------------------------------------------------------------------------- #
def salir_de_dispositivo(session: Session, dispositivo_id, usuario: Usuario) -> None:
    """"Salir de este dispositivo": quita el registro de `usuario` solo en este equipo."""
    if dispositivo_id is None:
        return
    registro = session.get(RegistroDispositivo, (dispositivo_id, usuario.id))
    if registro is not None:
        session.delete(registro)
        session.flush()


def cerrar_en_todos(session: Session, usuario: Usuario, actor: Usuario) -> None:
    """"Cerrar en todos los dispositivos": invalida TODOS los registros de `usuario` (en cada equipo vuelve a hacer
    falta la contraseña). Lo pueden hacer el propio Usuario o un ADMIN.

    Raises:
        PermissionError: si `actor` no es `usuario` ni un ADMIN.
    """
    if actor is None or (actor.id != usuario.id and actor.rol != RolUsuario.ADMIN):
        raise PermissionError("Solo el propio Usuario o un ADMIN pueden cerrar sus dispositivos.")
    usuario.registros_version = (usuario.registros_version or 0) + 1
    session.flush()
