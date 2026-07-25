# 01 — Lista de paquetes + Recibir (+ modal compartido)

**Spec:** `.scratch/packages-staff/spec.md` · **Glosario:** Estados del Paquete, Recibir, Guía, Usuario · **ADR:** 0004

**What to build:** El staff abre **`/packages`** (con sesión) y ve la **lista de paquetes** con su estado y destinatario; puede **recibir** un paquete `Anunciado` desde un **modal**, capturando opcionalmente la **Guía**, y queda registrado como **actor**. Establece el **componente de modal compartido** que reutilizan las demás acciones.

**Blocked by:** None — `package-lifecycle` (transiciones) y `staff-auth` (`current_staff`) ya están.

**Status:** ready-for-agent

- [ ] `GET /packages` protegido por `current_staff`: **sin** sesión → redirige a `/auth/login`; **con** sesión → 200 con la lista (estado + `recipient_name` + apartamento snapshot), orden `announced_at` desc. **Sin** columna de Guía/Código (brief §7).
- [ ] **Componente de modal compartido** (bottom-sheet en móvil, título/botones/cierre consistentes) con **Recibir** como primer consumidor; el botón de submit se **re-habilita con `finally`** (bug a no heredar).
- [ ] `POST /packages/{id}/receive`: `guide_number` **opcional** del form → `receive(session, paquete, current_staff, guide_number)`; paquete inexistente → **404**; **PRG** (redirige a `/packages`).
- [ ] Recibir un paquete **no** `Anunciado` (`TransicionInvalida`) → **mensaje de error, sin efecto**; la lista se re-muestra.
- [ ] El actor registrado (`received_by_usuario`) = **el staff de la sesión** (nunca un id enviado por el cliente).
- [ ] Tests HTTP (`TestClient`, staff sembrado como en `test_auth.py`): `/packages` sin sesión → redirige; con sesión → 200 y muestra el estado; `receive` → `Recibido` con actor correcto y guía si se pasa; recibir inválido → sin efecto; `id` inexistente → 404.
