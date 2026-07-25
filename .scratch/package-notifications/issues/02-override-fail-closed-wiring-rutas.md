# 02 — Override fail-closed de staging + wiring en las rutas (web)

**Spec:** `.scratch/package-notifications/spec.md` · **Glosario:** invariante de `CONTEXT.md` "override fail-closed" · **ADR:** 0004

**What to build:** En `WEB_ENV=staging`, **todo** mensaje se redirige a un número de prueba (`SMS_OVERRIDE_NUMBER`); si esa variable **falta**, **no se envía absolutamente nada** — nunca cae al envío real. Las rutas `recibir`/`entregar`/`cancelar` (ya existentes en `/packages`) disparan la notificación al completar la transición con éxito.

**Blocked by:** 01 — Notificación de evento: mensaje + destino + puerto (dominio). Necesita `notificar_evento`/`NotificationSender`.

**Status:** done · 176 tests verdes

- [x] **`StagingOverrideSender(wrapped, override_number)`**: si `override_number` es `None`/vacío → `.enviar()` **no hace nada** (fail-closed, **nunca** delega al `wrapped`); si está presente → sustituye el destino por `override_number` y delega al `wrapped` con el **mensaje real**.
- [x] **`get_notification_sender()`** (settings lazy, mismo patrón que `secret_key()`): `WEB_ENV=staging` → `StagingOverrideSender(ConsoleNotificationSender(), os.environ.get("SMS_OVERRIDE_NUMBER"))`; cualquier otro valor → `ConsoleNotificationSender()` directo, sin override.
- [x] **Wiring**: `POST /packages/{id}/receive`, `/deliver`, `/cancel` (existentes) llaman a `notificar_evento(paquete, evento, get_notification_sender())` **después** de que la transición de dominio tuvo éxito, antes del PRG. `paquete_lifecycle.py` **no se modifica**.
- [x] Tests HTTP (`TestClient`, `dependency_overrides` para inyectar un sender fake, mismo patrón que `get_db`): `receive`/`deliver`/`cancel` exitosos invocan al sender con destino+mensaje correctos.
- [x] **El test más importante de la rebanada**: `StagingOverrideSender` con `SMS_OVERRIDE_NUMBER` **ausente** → **cero llamadas** al sender envuelto (assert explícito de no-invocación) tras una transición real.
- [x] Con el override **presente**: el destino que llega al sender envuelto **es el número de override**, nunca el teléfono real del residente.
