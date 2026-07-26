# 02 — Checkbox de preferencia en `/customer/verify` y `/customers/manage/{id}` (web)

**Spec:** `.scratch/notification-preferences/spec.md`

**What to build:** El cliente activa/desactiva sus notificaciones desde su propio perfil (`/customer/verify`); el staff puede hacerlo por él desde `/customers/manage/{id}`. Ambos reutilizan `set_notificaciones_activas`, en el **mismo** formulario/envío que ya edita los datos personales — sin ruta nueva.

**Blocked by:** 01 — Preferencia de notificaciones + regla unificada de fallback (dominio). Necesita `set_notificaciones_activas`.

**Status:** done · 223 tests verdes

- [x] Checkbox "Recibir notificaciones por SMS" añadido al formulario de `/customer/verify` (prellenado con el estado actual). Un checkbox **desmarcado no se envía** en el `POST` (semántica HTML) — la ruta interpreta su **ausencia** como `False`, a diferencia del resto de campos (cuya ausencia significa "no tocar").
- [x] El cambio de preferencia se aplica en el **mismo** `POST` que `update_datos_personales`, con el mismo **todo o nada**: si el email es inválido, tampoco se aplica el cambio de preferencia de ese envío.
- [x] Mismo checkbox y mismo patrón añadido a `/customers/manage/{persona_id}` (ficha de staff).
- [x] Tests HTTP (`TestClient`, patrón `test_customer_verify.py`/`test_customers_manage.py`/`test_notifications.py`): desactivar desde `/customer/verify` → una transición posterior (`receive` sobre un paquete de esa Persona, con `dependency_overrides` del sender) **no** dispara el sender; reactivar restaura el envío; staff desactivando desde `/customers/manage/{id}` → mismo efecto; checkbox desmarcado no rompe el guardado del resto de campos (nombre/email se guardan igual).
