# -*- coding: utf-8 -*-
"""
Notificación de eventos del Paquete (Seam A) — mensaje + destino, sin infra.

Solo tres eventos notifican: `RECIBIDO`, `ENTREGADO`, `CANCELADO`. `ANUNCIADO` NO
notifica — el cliente ya lo sabe, acaba de hacerlo él mismo (cabo brief §15.1).

El destino es el teléfono del **Destinatario** si tiene uno propio; si es un
nombre sin teléfono, el aviso llega al **Anunciante** (siempre tiene teléfono,
ADR-0003).

El envío es **best-effort**: si el `NotificationSender` falla, `notificar_evento`
NO propaga — la transición del Paquete ya se completó y no debe bloquearse por
un proveedor caído.
"""

from .notification_sender import NotificationSender
from .paquete import EstadoPaquete, Paquete

_EVENTOS_QUE_NOTIFICAN = (
    EstadoPaquete.RECIBIDO,
    EstadoPaquete.ENTREGADO,
    EstadoPaquete.CANCELADO,
)


def construir_mensaje(evento: EstadoPaquete, paquete: Paquete) -> str:
    """El texto del mensaje para `evento`, claro y sin jerga técnica.

    Raises:
        ValueError: si `evento` no es uno de los que notifican
            (`RECIBIDO`/`ENTREGADO`/`CANCELADO`).
    """
    if evento is EstadoPaquete.RECIBIDO:
        return (
            f"Tu paquete ({paquete.recipient_name}) ya está en portería. "
            "Puedes reclamarlo cuando quieras. — PAQUETEX"
        )
    if evento is EstadoPaquete.ENTREGADO:
        return f"Tu paquete ({paquete.recipient_name}) fue entregado. ¡Gracias! — PAQUETEX"
    if evento is EstadoPaquete.CANCELADO:
        motivo = (paquete.cancel_reason or "").replace("_", " ").capitalize()
        return (
            f"Tu paquete ({paquete.recipient_name}) fue cancelado. "
            f"Motivo: {motivo}. — PAQUETEX"
        )
    raise ValueError(f"El evento {evento!r} no dispara notificación.")


def resolver_destino(paquete: Paquete) -> str:
    """El teléfono al que se notifica: el del Destinatario, o si no tiene
    (nombre sin teléfono), el del Anunciante."""
    return paquete.recipient_phone or paquete.announced_by_phone


def notificar_evento(
    paquete: Paquete, evento: EstadoPaquete, sender: NotificationSender
) -> None:
    """Notifica `evento` para `paquete` a través de `sender`.

    Best-effort: si `sender.enviar` lanza, la excepción se ignora aquí — la
    transición del Paquete ya se completó y no debe bloquearse por esto. Un
    `evento` que no dispara notificación (p.ej. `ANUNCIADO`) SÍ propaga su
    `ValueError` (es un error de uso, no un fallo de infraestructura).
    """
    mensaje = construir_mensaje(evento, paquete)
    destino = resolver_destino(paquete)
    try:
        sender.enviar(destino, mensaje)
    except Exception:
        pass
