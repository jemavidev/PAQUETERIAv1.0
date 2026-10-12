# -*- coding: utf-8 -*-
"""
Avisos especiales (`.scratch/avisos-especiales`): avisarles a mano a los clientes con algo pendiente que Papyrus no
presta el servicio de paquetes ciertos días (fines de semana, festivos, cierres).

Este módulo concentra las reglas para que las rutas solo lo llamen:

- los mensajes guardados (`MensajeEspecial`): crear, editar, eliminar (lógico), con historial;
- la resolución del texto para un cliente: un solo texto para SMS y WhatsApp, con `{nombre}` y `{codigos}` como
  únicas variables.
"""
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .mensaje_especial import (
    MAX_NOMBRE_MENSAJE,
    MAX_TEXTO_MENSAJE,
    AccionMensajeEspecial,
    MensajeEspecial,
    MensajeEspecialHistorial,
)
from .notificacion_service import _sin_tildes, normalizar_texto_plantilla

VARIABLES_MENSAJE = ("nombre", "codigos")

# Un SMS en GSM-7 (sin tildes, ver `notificacion_service._sin_tildes`) admite 160 caracteres en un solo segmento.
MAX_CARACTERES_UN_SMS = 160

EJEMPLO_VARIABLES = {"nombre": "MARIA PEREZ", "codigos": "A1B2, C3D4"}


# --------------------------------------------------------------------------- #
# Texto del mensaje
# --------------------------------------------------------------------------- #
def validar_texto_mensaje(texto: str) -> str | None:
    """El mensaje de error para `texto` (ya normalizado), o `None` si se puede guardar."""
    if not texto:
        return "El texto no puede quedar vacío."
    if len(texto) > MAX_TEXTO_MENSAJE:
        return f"El mensaje tiene {len(texto)} caracteres; el máximo es {MAX_TEXTO_MENSAJE}."
    try:
        texto.format(**{nombre: "" for nombre in VARIABLES_MENSAJE})
    except KeyError as exc:
        return f"La variable {{{exc.args[0]}}} no existe. Usa: {{nombre}}, {{codigos}}."
    except (IndexError, ValueError):
        return "Hay una llave { o } suelta: las variables van completas, como {nombre}."
    return None


def resolver_texto(texto: str, nombre: str, codigos: list[str]) -> str:
    """El texto de `MensajeEspecial` con `{nombre}` y `{codigos}` (separados por coma) resueltos -- el que va por
    WhatsApp tal cual. Para el SMS, ver `texto_sms`. Tolerante: un texto que no se pueda resolver (no debería pasar,
    el guardado lo valida) se devuelve sin resolver en vez de reventar."""
    try:
        return texto.format(nombre=nombre or "", codigos=", ".join(codigos))
    except (KeyError, IndexError, ValueError):
        return texto


def texto_sms(texto_resuelto: str) -> str:
    """El texto que sale por SMS: sin tildes, mismo criterio que los avisos automáticos (un carácter fuera de GSM-7
    recorta el segmento de 160 a 70 caracteres)."""
    return _sin_tildes(texto_resuelto)


def vista_previa(texto: str) -> dict:
    """Vista previa con datos de ejemplo: el texto resuelto, su largo como SMS y si cabe en un solo SMS."""
    resuelto = resolver_texto(texto, EJEMPLO_VARIABLES["nombre"], EJEMPLO_VARIABLES["codigos"].split(", "))
    caracteres = len(texto_sms(resuelto))
    return {"texto": resuelto, "caracteres": caracteres, "un_sms": caracteres <= MAX_CARACTERES_UN_SMS}


# --------------------------------------------------------------------------- #
# Mensajes guardados
# --------------------------------------------------------------------------- #
def listar_mensajes(session: Session) -> list[MensajeEspecial]:
    """Los mensajes vigentes (no eliminados), por nombre."""
    return (
        session.query(MensajeEspecial)
        .filter(MensajeEspecial.eliminado_en.is_(None))
        .order_by(func.lower(MensajeEspecial.nombre))
        .all()
    )


def obtener_mensaje(session: Session, mensaje_id) -> MensajeEspecial | None:
    """El mensaje vigente con `mensaje_id`, o `None` si no existe o fue eliminado."""
    mensaje = session.get(MensajeEspecial, mensaje_id)
    if mensaje is None or mensaje.eliminado_en is not None:
        return None
    return mensaje


def _validar(session: Session, nombre: str, texto: str, excluir_id=None) -> tuple[str, str]:
    nombre_limpio = " ".join((nombre or "").split())
    if not nombre_limpio:
        raise ValueError("El nombre no puede quedar vacío.")
    if len(nombre_limpio) > MAX_NOMBRE_MENSAJE:
        raise ValueError(f"El nombre admite hasta {MAX_NOMBRE_MENSAJE} caracteres.")
    texto_limpio = normalizar_texto_plantilla(texto)
    error = validar_texto_mensaje(texto_limpio)
    if error:
        raise ValueError(error)
    duplicado = session.query(MensajeEspecial).filter(
        MensajeEspecial.eliminado_en.is_(None),
        func.lower(MensajeEspecial.nombre) == nombre_limpio.lower(),
    )
    if excluir_id is not None:
        duplicado = duplicado.filter(MensajeEspecial.id != excluir_id)
    if duplicado.first() is not None:
        raise ValueError(f'Ya existe un mensaje llamado "{nombre_limpio}".')
    return nombre_limpio, texto_limpio


def _flush_o_duplicado(session: Session, nombre: str) -> None:
    try:
        session.flush()
    except IntegrityError:
        # Carrera: otro ADMIN guardó el mismo nombre entre la validación y este flush.
        session.rollback()
        raise ValueError(f'Ya existe un mensaje llamado "{nombre}".')


def crear_mensaje(session: Session, nombre: str, texto: str, usuario_id=None) -> MensajeEspecial:
    """Crea un mensaje especial y deja su creación en el historial.

    Raises:
        ValueError: nombre vacío, largo o repetido entre los vigentes (sin distinguir mayúsculas); texto vacío,
            largo, o con una variable distinta de `{nombre}`/`{codigos}`.
    """
    nombre_limpio, texto_limpio = _validar(session, nombre, texto)
    mensaje = MensajeEspecial(nombre=nombre_limpio, texto=texto_limpio)
    session.add(mensaje)
    _flush_o_duplicado(session, nombre_limpio)
    session.add(
        MensajeEspecialHistorial(
            mensaje_id=mensaje.id,
            accion=AccionMensajeEspecial.CREADO,
            usuario_id=usuario_id,
            nombre_nuevo=nombre_limpio,
            texto_nuevo=texto_limpio,
        )
    )
    session.flush()
    return mensaje
