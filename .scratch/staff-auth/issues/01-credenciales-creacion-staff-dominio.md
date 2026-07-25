# 01 — Credenciales de staff + creación (dominio)

**Spec:** `.scratch/staff-auth/spec.md` · **Glosario:** Usuario · **ADR:** 0002 (Alembic raíz única)

**What to build:** Un **administrador** puede crear cuentas de staff con **email + contraseña** (guardada **hasheada**, nunca en claro), y el sistema puede **verificar** esas credenciales. **Solo un ADMIN** crea cuentas; el **primer ADMIN** se siembra por un bootstrap operativo. Todo en la capa de dominio, sin HTTP.

**Blocked by:** None — la entidad `Usuario` (ADMIN/OPERADOR) ya está (data-model).

**Status:** ready-for-agent

- [ ] Migración `0005` **descendiente de `0004`** (raíz única, ADR-0002) que añade a `usuarios`: `email` (**único**, nullable) y `password_hash` (nullable). Constraints con **nombre explícito** en ORM y migración; el guard de paridad esquema↔ORM cubre las columnas; `alembic heads` = 1.
- [ ] Hashing con un algoritmo **fuerte y lento** (bcrypt vía `passlib`, nueva dep del arnés). El `password_hash` guardado **NO** es la contraseña en claro (el test lo verifica).
- [ ] **Política de contraseña fuerte** validada al crear/cambiar (longitud mínima razonable, no vacía/trivial) → `ValueError` si no cumple.
- [ ] `create_staff(session, actor, email, nombre, password, rol)`: exige `actor.rol == ADMIN` (si no, `PermissionError`); **email único** (rechaza duplicado); hashea la contraseña.
- [ ] `create_initial_admin(session, email, nombre, password)`: crea el **primer** ADMIN **sin** actor; **solo** cuando no existe ningún ADMIN (no crea un segundo por esta vía).
- [ ] `verify_credentials(session, email, password) -> Usuario | None`: acepta la correcta; **rechaza la contraseña mala y el email inexistente por igual** (`None`), sin distinguir cuál falló.
- [ ] Tests (Seam A, arnés compartido): admin crea staff; **operador NO puede** (`PermissionError`); email duplicado rechazado; bootstrap crea el primer admin y **no** un segundo; `verify_credentials` acepta la correcta y rechaza mala/inexistente; el hash **no** es la contraseña en claro; contraseña débil rechazada.
