# 01 — Notificación de evento: mensaje + destino + puerto (dominio)

**Spec:** `.scratch/package-notifications/spec.md` · **Glosario:** Estados del Paquete, Anunciante, Destinatario

**What to build:** Dado un Paquete y un evento (`Recibido`/`Entregado`/`Cancelado`), el sistema sabe **qué mensaje** enviar y **a qué teléfono** — al destinatario si tiene teléfono propio, si no al anunciante. Todo en dominio puro, sin infraestructura de red.

**Blocked by:** None — `Paquete`/`EstadoPaquete`/`MotivoCancelacion` (data-model, package-lifecycle) ya están.

**Status:** done · 176 tests verdes

- [x] **Puerto `NotificationSender`** (Protocol, `enviar(destino, mensaje)`) — **separado** de `OtpSender` (misma forma, semántica distinta; no fusionar — YAGNI). `ConsoleNotificationSender`: implementación de desarrollo/test que captura sin red (mismo espíritu que `DevOtpSender`).
- [x] `construir_mensaje(evento, paquete) -> str`: un mensaje claro por evento — `RECIBIDO` (ya está en portería), `ENTREGADO` (constancia de entrega), `CANCELADO` (incluye el **motivo** legible). Función pura, sin sender.
- [x] `resolver_destino(paquete) -> str`: `recipient_phone` si existe; si no, `announced_by_phone` (nunca `None` — el anunciante siempre tiene teléfono).
- [x] `notificar_evento(paquete, evento, sender) -> None`: arma mensaje+destino y llama `sender.enviar(...)`. **Best-effort**: si `sender.enviar` lanza, la excepción se **atrapa y se ignora** aquí (no debe propagar y bloquear al llamador).
- [x] Tests (Seam A, sender fake): mensaje correcto por cada uno de los 3 eventos (Cancelado incluye el motivo); destino = destinatario cuando tiene teléfono, anunciante cuando el destinatario es nombre-sin-teléfono; si el sender lanza, `notificar_evento` no propaga.
