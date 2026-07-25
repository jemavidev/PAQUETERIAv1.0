# 02 — Entregar (modal + acción)

**Spec:** `.scratch/packages-staff/spec.md` · **Glosario:** Entregar, Contexto de entrega (snapshot), Usuario

**What to build:** El staff **entrega** un paquete `Recibido` desde `/packages`; el **modal Entregar** muestra el **destinatario snapshot** (nombre + apartamento congelados al anunciar) para confirmar a quién se le entrega, y queda registrado el **actor**.

**Blocked by:** 01 — Lista de paquetes + Recibir (reutiliza el modal compartido y la lista).

**Status:** done · 126 tests verdes

- [x] Modal **Entregar** (componente compartido) que muestra el **destinatario snapshot** (`recipient_name` + apartamento snapshot) en **solo lectura**, para confirmar quién retira.
- [x] `POST /packages/{id}/deliver` → `deliver(session, paquete, current_staff)`; **PRG** a `/packages`; **404** si no existe.
- [x] Entregar un paquete **no** `Recibido` (`TransicionInvalida`) → **error, sin efecto**.
- [x] El actor registrado (`delivered_by_usuario`) = el staff de la sesión.
- [x] Tests HTTP: entregar un `Recibido` → `Entregado` con actor correcto; entregar inválido → sin efecto; la acción exige sesión.
