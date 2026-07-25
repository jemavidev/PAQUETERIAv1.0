# 03 — Cancelar (modal + acción)

**Spec:** `.scratch/packages-staff/spec.md` · **Glosario:** Cancelar, Estados del Paquete, Usuario

**What to build:** El staff **cancela** un paquete `Anunciado` o `Recibido` desde `/packages` con un **motivo obligatorio** (dropdown) y **aviso de irreversibilidad**; quedan registrados el **actor** y el **motivo**.

**Blocked by:** 01 — Lista de paquetes + Recibir (reutiliza el modal compartido y la lista).

**Status:** done · 126 tests verdes

- [x] Modal **Cancelar** (componente compartido) con **dropdown de `MotivoCancelacion` obligatorio** + aviso de que es **irreversible**.
- [x] `POST /packages/{id}/cancel`: `motivo` **obligatorio** → `cancel(session, paquete, current_staff, motivo)`; motivo vacío → **error, sin efecto**; **PRG** a `/packages`; **404** si no existe.
- [x] Cancelar un paquete en estado **terminal** (`Entregado`/`Cancelado`) (`TransicionInvalida`) → **error, sin efecto**.
- [x] El actor (`cancelled_by_usuario`) y el `cancel_reason` quedan registrados.
- [x] Tests HTTP: cancelar desde `Anunciado` **y** desde `Recibido` → `Cancelado` con actor + motivo; sin motivo → sin efecto; cancelar un terminal → sin efecto; la acción exige sesión.
