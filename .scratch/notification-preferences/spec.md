# Spec — Preferencia de notificaciones (opt-out) del cliente

Status: ready-for-agent
Feature: notification-preferences
Branch: PaqueteXv.2
Depende de: `package-notifications` (`notificar_evento`, `NotificationSender`), `customer-verify` (`/customer/verify`), `customers-manage` (`/customers/manage/{id}`), ADR-0005 (anonimización).
Fuente de verdad: conversación de diseño con el owner (2026-07-25/26) — 4 decisiones cerradas + 1 regla unificada, ver Implementation Decisions.

---

## Problem Statement

Hoy **nadie puede desactivar** las notificaciones de evento (`Recibido`/`Entregado`/`Cancelado`, `package-notifications`) — se envían siempre, sin excepción, a quien resuelva `resolver_destino`. Un residente que pide dejar de recibir SMS no tiene forma de lograrlo, ni el cliente por sí mismo ni el staff en su nombre. Además, el diseño actual de `resolver_destino` es **puro** (sin sesión de BD): no puede distinguir si el teléfono al que apuntaría el envío sigue perteneciendo a una identidad viva — un caso que se vuelve real ahora que existe la anonimización (ADR-0005, `customers-manage`): un Destinatario registrado que fue anonimizado después de que se le anunció un paquete deja un `recipient_phone` **congelado** (snapshot, ADR-0001) que ya no encuentra a nadie.

## Solution

Un **interruptor global** por Persona (`notificaciones_activas`, booleano, `default=True` — preserva el comportamiento actual), editable por el **cliente** (`/customer/verify`) y por **staff** (`/customers/manage/{id}`), que `notificar_evento` respeta antes de enviar. **Nunca** afecta el envío del OTP (mecanismo de login, no una notificación opcional).

Se resuelve, de paso, el caso del Destinatario anonimizado con una **única regla** (no dos): el Anunciante recibe el aviso **siempre que no haya un Destinatario con teléfono propio y alcanzable** — eso cubre tanto el "nombre sin teléfono" (ya existente) como el "tenía teléfono pero fue anonimizado después" (nuevo). Es la misma lógica, dos disparadores.

## User Stories

1. Como **residente**, quiero **desactivar** mis notificaciones de evento desde mi perfil (`/customer/verify`), para dejar de recibir SMS si no los quiero.
2. Como **residente**, quiero poder **reactivarlas** cuando cambie de opinión.
3. Como **staff**, quiero poder **activar/desactivar** las notificaciones de un cliente desde `/customers/manage/{id}`, para atender una solicitud sin que el residente tenga que entrar a la app.
4. Como **residente nuevo**, quiero que mis notificaciones estén **activas por defecto**, para no perderme avisos que hoy sí recibo, sin tener que configurar nada.
5. Como **residente que desactivó** sus notificaciones, quiero seguir recibiendo mi **código OTP** para iniciar sesión con normalidad — la preferencia no debe bloquear mi propio acceso.
6. Como **residente que anuncia** un paquete para **otra Persona registrada** (con teléfono propio), quiero que **ella** reciba el aviso (si tiene sus notificaciones activas) — su preferencia gobierna, no la mía.
7. Como **residente que anuncia** un paquete para un **nombre sin teléfono**, quiero seguir recibiendo yo el aviso (comportamiento ya existente, sin cambios).
8. Como **residente destinatario que fue anonimizado** después de que le anunciaron un paquete, quiero que el sistema **no intente notificar** a mi número histórico (ya no me representa) — en vez de eso, que avise al **Anunciante** (mismo criterio que el nombre sin teléfono).
9. Como **operador de sistema**, quiero que un envío fallido o "nadie a quien notificar" **no rompa** la transición del Paquete (`recibir`/`entregar`/`cancelar` se completan igual) — mismo principio best-effort ya existente.
10. Como **desarrollador**, quiero que la regla de "a quién notificar" quede en **una sola función**, no dos reglas separadas para "nombre sin teléfono" y "destinatario anonimizado".

## Implementation Decisions

### Esquema (migración `0008`, descendiente de `0007`)

- `personas.notificaciones_activas`: `Boolean`, `NOT NULL`, `default=True` (server-side y de aplicación). Constraint/columna con nombre explícito consistente con el patrón existente; guard de paridad esquema↔ORM la cubre; `alembic heads` = 1 (ADR-0002).

### Dominio — cambio de firma real en `notificar_evento` (no solo aditivo)

- **Nueva función `resolver_destino_notificable(session, paquete) -> Persona | None`**: si `paquete.recipient_phone` existe, busca una Persona **viva** por ese teléfono exacto (una Persona anonimizada ya no tiene ese teléfono — la búsqueda no la encuentra por construcción, sin necesidad de filtrar `eliminado_en` aparte); si la encuentra, es el destino. **Si no** (nombre sin teléfono, o el Destinatario ya no es alcanzable) → cae al **Anunciante**, resuelto por la FK real `announced_by_persona_id` (ADR-0003, siempre existe) — pero **solo si el Anunciante mismo sigue vivo** (`eliminado_en is None`; si también fue anonimizado, no queda nadie a quien notificar → `None`).
- **`notificar_evento` cambia de firma**: pasa a **`notificar_evento(session, paquete, evento, sender)`** (antes: `notificar_evento(paquete, evento, sender)`, sin sesión). Usa `resolver_destino_notificable` para obtener la Persona destino; si es `None` **o** `persona.notificaciones_activas` es `False` → no envía nada (silencioso, sin error). Si hay destino y está activo → llama `sender.enviar(persona.telefono, mensaje)` (best-effort, igual que hoy).
- **Impacto real en código ya en producción**: los 3 call sites en `packages.py` (`receive_action`, `deliver_action`, `cancel_action`) deben actualizarse para pasar `db` a `notificar_evento`. Los tests de Seam A existentes que llaman `notificar_evento` directamente (`test_notificacion_service.py`) también deben actualizarse a la firma nueva.
- **`resolver_destino` (la función pura vieja, `recipient_phone or announced_by_phone`) se conserva sin cambios** — sigue siendo la respuesta correcta a "qué dice el snapshot de texto", útil aparte de la decisión de envío; `notificar_evento` deja de usarla internamente, usa `resolver_destino_notificable`.
- **Nueva función `set_notificaciones_activas(session, persona, activas: bool) -> Persona`** en `persona_service.py` (junto a `update_datos_personales`/`anonimizar_persona`) — trivial, sin ambigüedad de "parcial" (un checkbox siempre tiene un estado definido al enviarse, a diferencia de los campos de texto opcionales de `update_datos_personales`).

### Web — un checkbox en dos formularios ya existentes

- **`/customer/verify`**: se añade un checkbox "Recibir notificaciones por SMS" al formulario existente. Un checkbox **desmarcado no se envía** en el POST (semántica HTML estándar) — la ruta debe interpretar su **ausencia** como `False`, distinto del resto de campos (cuya ausencia significa "no tocar"). Se aplica **junto** con `update_datos_personales` en el mismo `POST` (mismo "todo o nada": si el email es inválido, tampoco se aplica el cambio de preferencia de ese envío).
- **`/customers/manage/{persona_id}`**: mismo checkbox, mismo patrón, en el formulario de edición que el staff ya usa.
- **Sin ruta nueva** — se reutilizan las dos rutas `POST` existentes, extendiendo su payload y su llamada a dominio.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento observable** — que desactivar detiene el envío; que activar lo restaura; que el OTP nunca se ve afectado; que la preferencia de quien **recibe de verdad** el mensaje es la que gobierna (no la del Anunciante cuando hay un Destinatario vivo); que el fallback al Anunciante ocurre tanto por nombre-sin-teléfono como por Destinatario anonimizado, con la **misma** función — no dos rutas de código distintas.

**Costuras (ambas EXISTENTES, ninguna nueva):**
- **Dominio (Seam A):** `resolver_destino_notificable` — Destinatario vivo con teléfono → ese es el destino; nombre sin teléfono → cae al Anunciante; Destinatario anonimizado después de anunciar → cae al Anunciante (mismo resultado que el caso anterior, mismo código); Anunciante también anonimizado → `None`. `notificar_evento` (nueva firma) — `notificaciones_activas=False` → cero llamadas al sender; `True` → llama normal; actualizar los tests existentes a la firma con `session`.
- **HTTP (Seam web):** `TestClient`, patrón de `test_customer_verify.py`/`test_customers_manage.py`. Casos: desactivar desde `/customer/verify` → una transición posterior (`receive` sobre un paquete de esa Persona) no dispara el sender (con `dependency_overrides`, patrón de `test_notifications.py`); staff desactivando desde `/customers/manage/{id}` → mismo efecto; reactivar restaura el envío; checkbox desmarcado no rompe el resto del guardado (nombre/email se guardan igual).

**Prior art:** `tests/data_model/test_notificacion_service.py` (se extiende, no se reescribe desde cero), `tests/web/test_notifications.py` (patrón de sender espía + `dependency_overrides`), `tests/web/test_customer_verify.py`/`test_customers_manage.py` (patrón de formulario + `client.db`). Construir **test-first** con `/tdd`.

## Out of Scope

- **Granularidad por evento o por canal** — decisión cerrada: un solo interruptor global; si se necesita granularidad después, es una extensión de esquema, no de esta spec.
- **Preferencias de OTP** — el OTP nunca se ve afectado, decisión cerrada explícitamente.
- **Notificar al residente que su preferencia cambió** — no aplica.
- **Auditoría de quién cambió la preferencia de quién** — mismo criterio que el resto del rebuild (sin log de eventos).
- **Canal WhatsApp** — sigue fuera de alcance del rebuild completo (`package-notifications` lo dejó pendiente); esta spec no lo toca.

## Further Notes

- **Por qué el cambio de firma de `notificar_evento` no es opcional:** evaluar "¿está viva y alcanzable la Persona destino?" requiere una consulta a la BD (buscar por teléfono, o revisar `eliminado_en` del Anunciante) — no se puede resolver con los datos ya congelados en el `Paquete`. Es un cambio real a código en producción, documentado aquí para que quien lo implemente no lo descubra a mitad de camino.
- **La regla unificada del Anunciante-como-fallback** fue una decisión tomada en conversación con el owner, generalizando el comportamiento ya existente de "nombre sin teléfono" al nuevo caso de "destinatario anonimizado" — una sola función, no una rama especial para el caso nuevo.
- **Consumo aguas abajo:** ninguna otra rebanada depende de ésta.
