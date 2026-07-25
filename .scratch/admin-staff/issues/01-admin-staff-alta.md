# 01 — `/admin/staff` (alta de cuentas de staff)

**Spec:** `.scratch/admin-staff/spec.md` · **Glosario:** Usuario, "Solo un ADMIN crea cuentas de staff" · **ADR:** 0004

**What to build:** Un **ADMIN** con sesión abre `/admin/staff` y da de alta una cuenta de staff (email, nombre, contraseña, rol ADMIN/OPERADOR), reutilizando `create_staff` **sin cambios de dominio**. Un **operador** (no admin) es rechazado; sin sesión, redirige a login.

**Blocked by:** None — `create_staff`/`require_admin` (staff-auth) ya están y están probados.

**Status:** done · 181 tests verdes

- [x] `GET /admin/staff` **gated por `require_admin`**: sin sesión → redirige a `/auth/login`; sesión de OPERADOR → **403**; sesión de ADMIN → 200 con el formulario (email, nombre, contraseña, selector de rol).
- [x] `POST /admin/staff`: valida presencia básica (email/nombre/contraseña no vacíos) antes de llamar a dominio; llama `create_staff(db, actor=<admin de la sesión>, email, nombre, password, rol)`; éxito → confirmación (PRG). El **actor** sale de la sesión (`require_admin`), nunca de un campo del formulario.
- [x] `PermissionError`/`ValueError` de `create_staff` (no-admin — no debería ocurrir dado el gate, pero se maneja igual; email duplicado; contraseña débil) → re-render con mensaje, **sin** crear ninguna cuenta.
- [x] Campos vacíos → error **antes** de llamar a `create_staff`.
- [x] Retirar la ruta placeholder `/auth/admin/check` (creada en `staff-auth` solo para probar `require_admin`) — queda obsoleta, nada más la referencia.
- [x] Tests HTTP (`TestClient`, patrón `test_packages.py`/`test_auth.py`): sin sesión → redirige; sesión de OPERADOR → 403; sesión de ADMIN → 200 en GET; `POST` válido crea el `Usuario` (verificado en `client.db`) con confirmación; email duplicado → error sin segunda cuenta; contraseña débil → error sin cuenta; campos vacíos → error. **No** se re-testea la regla de negocio de `create_staff` (ya cubierta en `test_staff_service.py`) — solo el cableado HTTP.
