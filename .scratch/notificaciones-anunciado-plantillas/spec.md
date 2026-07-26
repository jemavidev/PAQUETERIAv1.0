# Notificaciones: Anunciado también notifica + plantillas modificables

Fuente: `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 8. Depende del Grupo 1 (ya implementado).

## Problem Statement

Hoy `ANUNCIADO` no dispara notificación (decisión original: "el cliente ya lo sabe, lo acaba de hacer él mismo"). El usuario pidió revertir esto explícitamente. Además, los mensajes de cada evento están hardcodeados en `construir_mensaje` — el usuario quiere poder modificarlos sin tocar código.

**LIWA (proveedor SMS real) queda fuera de esta rebanada.** Ya se investigó su API (endpoint, autenticación, formato — ver Grupo 8 en `REQUERIMIENTOS.md`), pero el proyecto tiene un principio ya establecido y seguido consistentemente (`OtpSender`/`NotificationSender`/`FotoStorage`, todos con solo una implementación de desarrollo hasta ahora): **no se escribe código de infraestructura externa sin poder verificarlo contra la infraestructura real.** Sin credenciales reales de LIWA, un `LiwaNotificationSender` no se puede probar de verdad — quedaría como código no verificado. Se implementa en cuanto se tengan las credenciales (`LIWA_API_KEY`, `LIWA_ACCOUNT`, `LIWA_PASSWORD`).

## Solution

`ANUNCIADO` se agrega a los eventos que notifican. Los textos de mensaje se guardan en una tabla (`plantillas_notificacion`), con un texto por evento (y opcionalmente por motivo de cancelación), editable por el staff desde una pantalla nueva — sin tocar código para cambiar el texto de un aviso.

## User Stories

1. Como residente, quiero recibir una notificación cuando mi paquete queda anunciado, para tener confirmación de que el sistema lo registró.
2. Como miembro del staff (ADMIN), quiero poder editar el texto de las notificaciones de cada evento, para ajustar el tono o la información sin pedirle un cambio de código a nadie.
3. Como miembro del staff (ADMIN), quiero un texto de plantilla distinto según el motivo de cancelación, para que el aviso sea más específico.
4. Como desarrollador, quiero que si no hay una plantilla personalizada para un evento, se use el texto por defecto actual, para no romper nada mientras no se edite ninguna.
5. Como desarrollador, no quiero escribir el conector real de LIWA sin credenciales verificables, para no dejar código de infraestructura sin probar contra la infraestructura real.

## Implementation Decisions

- **`notificacion_service.py`**: `_EVENTOS_QUE_NOTIFICAN` agrega `EstadoPaquete.ANUNCIADO`. `resolver_destino_notificable` y el best-effort de envío no cambian — misma regla unificada de a quién le llega.
- **Nueva tabla `plantillas_notificacion`** (migración Alembic): `id`, `evento` (String, `EstadoPaquete` value), `motivo` (String nullable — solo aplica a `CANCELADO`), `texto` (String largo, con placeholders `{recipient_name}`/`{motivo}`), `updated_at`. Único por `(evento, motivo)`.
- **`construir_mensaje(session, evento, paquete)`** cambia de firma (ahora recibe `session`): busca una plantilla por `(evento, motivo si CANCELADO)`; si existe, la renderiza con los placeholders; si no, usa el texto hardcodeado actual como fallback (comportamiento de hoy, intacto).
- **Nueva ruta staff** `/administracion/notificaciones` (solo `ADMIN`, mismo patrón de gate que `/administracion/personal`): lista las plantillas (una fila por evento/motivo, incluidos los defaults actuales si no hay override), formulario para editar el texto de cada una.
- **LIWA**: NO se implementa en esta rebanada. Se deja documentado (este archivo + el Grupo 8 en `REQUERIMIENTOS.md`) exactamente qué se necesita (credenciales) y cuál es la forma de la integración ya investigada, para que implementarlo sea straightforward en cuanto lleguen las credenciales.

## Testing Decisions

- Seam de dominio (`tests/data_model/test_notificacion_service.py`, extender): `ANUNCIADO` ahora dispara `notificar_evento`; sin plantilla personalizada, usa el texto por defecto (comportamiento actual, no debe cambiar); con plantilla personalizada, la usa en su lugar.
- Seam web (nuevo `tests/web/test_admin_notificaciones.py`): solo `ADMIN` accede; editar una plantilla la persiste; sin plantilla, el formulario muestra el texto por defecto como valor inicial.

## Out of Scope

- Conector real de LIWA — bloqueado por credenciales (`LIWA_API_KEY`, `LIWA_ACCOUNT`, `LIWA_PASSWORD`), ver nota arriba.
- Reemplazar `DevOtpSender` — mismo bloqueo.

## Further Notes

Cuando llegues con las credenciales de LIWA, la implementación real (`LiwaNotificationSender`/`LiwaOtpSender`) es un cambio acotado: una nueva clase que implementa `NotificationSender`/`OtpSender` (los puertos ya existen), cableada en `get_notification_sender()`/donde corresponda para `OtpSender`, sin tocar el resto del sistema.
