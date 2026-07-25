# Spec — Notificaciones de eventos del Paquete (SMS + override fail-closed de staging)

Status: ready-for-agent
Feature: package-notifications
Branch: PaqueteXv.2
Depende de: `package-lifecycle` (eventos recibido/entregado/cancelado), `packages-staff` (rutas donde ocurren las transiciones), `customer-otp-auth` (puerto `OtpSender`, patrón a replicar).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §9/§10/§15.1 · `CONTEXT.md` (invariante 6: override fail-closed) · ADR-0004

---

## Problem Statement

El residente no se entera de que su paquete **llegó**, **se entregó** o **se canceló** — solo lo sabe si consulta `/search` por su cuenta. El brief exige notificaciones SMS/WhatsApp (§9), pero hoy no existe ningún envío real ni la lógica de **qué evento dispara qué mensaje** (cabo explícito §15.1: "¿anunciado/recibido/entregado? ¿SMS y WhatsApp o uno solo por evento?"). Además, staging debe sincronizarse con datos reales de producción (§10) — lo que significa que sin una salvaguarda, **cualquier prueba en staging mandaría SMS reales a residentes reales**. El brief exige que esa salvaguarda sea **fail-closed**: si falta la config del override, staging **no envía nada a nadie**, nunca cae al envío real (`CONTEXT.md`, invariante 6).

## Solution

Un **puerto de notificación** (mismo patrón que `OtpSender` de `customer-otp-auth`) que las transiciones `recibir`/`entregar`/`cancelar` invocan al completarse, con:

- **Eventos que notifican** (resuelve el cabo §15.1): `Recibido`, `Entregado`, `Cancelado` (con su motivo). **`Anunciado` no notifica** — el cliente ya lo sabe, acaba de hacerlo él mismo.
- **Un mensaje por evento**, con plantilla clara (dominio, sin HTML ni jerga técnica), dirigido al **teléfono del destinatario** si lo tiene (`recipient_phone`), o al **del anunciante** si el destinatario es un nombre sin teléfono.
- **Canal SMS** para esta rebanada (WhatsApp queda como otro adaptador futuro detrás del mismo puerto — no se implementa aquí).
- **Override fail-closed de staging**: en `WEB_ENV=staging`, todo mensaje se redirige a `SMS_OVERRIDE_NUMBER`; si esa variable **falta**, **no se envía nada a nadie** (nunca cae al envío real). En desarrollo/test, un sender de consola (mismo espíritu que `DevOtpSender`) registra el mensaje sin red.
- **Integración real con un proveedor SMS** (Twilio u otro) queda **fuera de esta rebanada** — se entrega el puerto + el wrapper de seguridad + el sender de desarrollo; conectar el proveedor real es, a propósito, un cambio de una sola implementación cuando existan credenciales (mismo patrón que el envío real de OTP quedó diferido a esta rebanada).

## User Stories

1. Como **residente**, quiero recibir un **SMS cuando mi paquete es recibido** en portería, para saber que ya puedo pasar a reclamarlo.
2. Como **residente**, quiero recibir un **SMS cuando mi paquete es entregado**, para tener constancia.
3. Como **residente**, quiero recibir un **SMS si mi paquete es cancelado**, con el **motivo**, para saber por qué no llegará.
4. Como **residente**, quiero **no** recibir un SMS solo por anunciar (ya lo sé, lo acabo de hacer yo).
5. Como **residente cuyo paquete llega a nombre de otra persona registrada**, quiero que el SMS llegue **a esa persona** (el destinatario), no a mí.
6. Como **residente que recibió un paquete "a nombre de un nombre sin teléfono"**, quiero que el SMS me llegue **a mí** (el anunciante), porque el destinatario no tiene teléfono propio.
7. Como **staff**, quiero que el mensaje sea **claro y sin jerga técnica** (nombre del paquete, qué pasó, y el motivo si fue cancelado).
8. Como **operador de sistema**, quiero que en **staging**, TODO mensaje se redirija a un **número de prueba único** (`SMS_OVERRIDE_NUMBER`), para que las pruebas con datos reales nunca lleguen a un residente real.
9. Como **operador de sistema**, quiero que si `SMS_OVERRIDE_NUMBER` **falta** en staging, el sistema **no envíe absolutamente nada** — nunca debe "caer" al envío real por defecto (fail-closed, invariante de `CONTEXT.md`).
10. Como **desarrollador**, quiero que en desarrollo/test los mensajes se **capturen sin red** (consola/memoria), para poder trabajar y probar sin depender de un proveedor externo.
11. Como **QA**, quiero probar de punta a punta (transición → mensaje correcto al destinatario correcto) sin depender de un proveedor SMS real.
12. Como **arquitecto**, quiero que el **puerto de notificación** sea independiente de `OtpSender` (mismo patrón, sin fusionarlos prematuramente — los códigos OTP y los mensajes de evento tienen semántica distinta), para no acoplar dos conceptos que aún no han demostrado necesitar una sola abstracción.
13. Como **dueño**, quiero que la integración real con un proveedor SMS quede **lista para conectar** (el puerto ya existe) el día que haya credenciales, sin tocar la lógica de negocio.
14. Como **staff**, quiero que si el envío de un SMS **falla** (proveedor caído), la transición del paquete (recibir/entregar/cancelar) **igual se complete** — la notificación es best-effort, no debe bloquear la operación.

## Implementation Decisions

### Dominio (Seam A) — mensaje y destino, sin infraestructura

- `notificacion_service.py`: `construir_mensaje(evento, paquete) -> str` — **función pura**, sin sender, fácil de testear. Un mensaje por evento (`RECIBIDO`, `ENTREGADO`, `CANCELADO`, este último incluye el motivo legible).
- `resolver_destino(paquete) -> str` — teléfono del destinatario (`recipient_phone`) si existe, si no el del anunciante (`announced_by_phone`). Nunca `None` (el anunciante siempre tiene teléfono, ADR-0003).
- `notificar_evento(paquete, evento, sender) -> None`: arma mensaje + destino y llama a `sender.enviar(destino, mensaje)`. **Best-effort**: si el `sender` lanza, la excepción se **atrapa aquí y se ignora silenciosamente a nivel de notificación** (se documenta explícitamente — no debe reventar la transición del paquete que ya se completó).
- **Puerto `NotificationSender`** (Protocol, `enviar(destino, mensaje)`) — deliberadamente **separado** de `OtpSender` (mismo patrón, sin fusionar: OTP es un código temporal, esto es un mensaje templado; unificarlos es un refactor futuro legítimo solo si dos usos reales lo piden, no antes — YAGNI).
- `ConsoleNotificationSender` (implementación de desarrollo/test, captura sin red — mismo espíritu que `DevOtpSender`).

### Web (capa de infraestructura) — override fail-closed + wiring

- `StagingOverrideSender(wrapped, override_number)`: envuelve cualquier `sender`. Si `override_number` es `None`/vacío → `.enviar()` **no hace nada** (fail-closed, nunca delega al `wrapped`). Si está presente → sustituye el destino por `override_number` y delega al `wrapped` (así un humano en staging sigue viendo el contenido real, con el destino seguro).
- `get_notification_sender()` (settings lazy, mismo patrón que `secret_key()`/`database_url()`): lee `WEB_ENV`.
  - `staging` → `StagingOverrideSender(ConsoleNotificationSender(), os.environ.get("SMS_OVERRIDE_NUMBER"))` — el proveedor real detrás del wrapper es, por ahora, el de consola (no hay integración real en esta rebanada; el wrapper es el punto de seguridad, no el canal).
  - cualquier otro valor (`development`, tests, sin definir) → `ConsoleNotificationSender()` directo, sin override (nada sale de la máquina de todos modos).
- **Wiring**: las rutas `POST /packages/{id}/receive`, `/deliver`, `/cancel` (ya existentes) llaman a `notificar_evento(paquete, evento, get_notification_sender())` **después** de que la transición de dominio tuvo éxito, antes del redirect (PRG). No se toca la lógica de transición en sí (`paquete_lifecycle.py` no se modifica).

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento externo observable** — qué mensaje se construye para cada evento, a qué teléfono se dirige (destinatario vs anunciante), que el override fail-closed **nunca** deja pasar un mensaje real sin config, y que una transición HTTP exitosa efectivamente invoca al sender correcto con el contenido correcto — no la infraestructura de red de un proveedor real (no se testea código no escrito).

**Costuras (ambas EXISTENTES):**
- **Dominio (Seam A):** `construir_mensaje`/`resolver_destino`/`notificar_evento` con un `NotificationSender` **fake** (captura llamadas). Casos: mensaje de cada evento (Recibido/Entregado/Cancelado+motivo) tiene el contenido esperado; destino = `recipient_phone` cuando existe, `announced_by_phone` cuando el destinatario es nombre-sin-teléfono; `Anunciado` **no** dispara nada (no hay hook para ese evento — se prueba por ausencia de llamada al orquestar el flujo completo); si el sender lanza, `notificar_evento` no propaga la excepción.
- **HTTP (Seam web):** `TestClient` (arnés existente, `tests/web/test_packages.py` como prior art). Reemplaza `get_notification_sender` por un fake inyectable (mismo patrón de `dependency_overrides` que ya usa `client.db`/`get_db`). Casos: `POST receive/deliver/cancel` exitoso invoca al sender con destino+mensaje correctos; el `StagingOverrideSender` con `SMS_OVERRIDE_NUMBER` ausente **no llama** al sender envuelto (assert explícito de "cero llamadas", el corazón de esta rebanada); con el override presente, el destino que llega al sender envuelto **es el número de override**, no el real.

**Prior art:** `tests/data_model/test_otp_service.py` (patrón de sender fake + Seam A), `tests/web/test_packages.py` (rutas de transición). Construir **test-first** con `/tdd`.

## Out of Scope

- **Integración real con un proveedor SMS** (Twilio u otro) — el puerto y el wrapper de seguridad quedan listos; conectar el proveedor real es un cambio de una sola implementación cuando existan credenciales.
- **Canal WhatsApp** — mismo puerto, otro adaptador futuro; no se implementa en esta rebanada.
- **Notificación al anunciar** (`Anunciado`) — decisión explícita: no notifica.
- **Notificaciones por email** (`EMAIL_OVERRIDE` del brief §10) — no existe canal email en el rebuild; solo aplica el override de SMS.
- **Plantillas configurables desde `/admin`** (el brief menciona `sms_message_templates` como mecanismo viejo a conservar) — aquí las plantillas son fijas en código; la gestión editable es otra rebanada.
- **Reintentos / cola de envío** ante fallo del proveedor — best-effort simple (se ignora el error), sin retry.

## Further Notes

- **Por qué NO fusionar con `OtpSender`:** son dos puertos con la misma forma (`enviar(destino, mensaje)`) pero semántica distinta (código temporal vs mensaje templado de evento). Fusionarlos ahora sería una abstracción prematura con un solo caso de uso real de cada lado; si aparece un tercer uso que comparta infraestructura de envío real (el mismo proveedor SMS), ese es el momento de extraer un `SmsGateway` común — no antes.
- **El fail-closed es el corazón de esta rebanada.** Todo lo demás (plantillas, destino) es útil pero reversible; el override sin salvaguarda sería el error más caro posible (SMS reales a residentes reales durante pruebas de staging) — por eso el test de "cero llamadas sin config" es el más importante de todos.
- **Consumo aguas abajo:** cuando exista un proveedor real, se conecta como una nueva implementación de `NotificationSender` (y de `OtpSender`, por separado) sin tocar `notificacion_service.py` ni las rutas.
