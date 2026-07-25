# 02 — Rutas web OTP + sesión de cliente + `current_customer`

**Spec:** `.scratch/customer-otp-auth/spec.md` · **Glosario:** Persona · **ADR:** 0004 (capa web clean-room)

**What to build:** El residente pide y verifica su OTP desde `/auth/customer/*` y obtiene una **sesión de cliente independiente** de la sesión de staff. La dependencia **`current_customer`** entrega la Persona de esa sesión — la pieza que `/customer/verify` usará como gate.

**Blocked by:** 01 — OTP de cliente: pedir + verificar (dominio). Necesita `request_otp`/`verify_otp`.

**Status:** done · 149 tests verdes

- [x] **Sesión de cliente independiente**: misma técnica que staff (`SessionMiddleware`, cookie firmada) pero con **clave propia** en el diccionario de sesión (`persona_id`, distinta de `usuario_id`) — ambas sesiones coexisten en el mismo navegador sin pisarse.
- [x] `GET /auth/customer/login` → 200: formulario de teléfono.
- [x] `POST /auth/customer/request-otp`: teléfono → `request_otp(...)` (con el sender de dev) → muestra la pantalla "ingresa el código".
- [x] `POST /auth/customer/verify-otp`: teléfono + código → `verify_otp(...)`; válido → **abre sesión de cliente** + redirige; inválido → mensaje **genérico**, sin sesión.
- [x] `POST /auth/customer/logout`: cierra **solo** la sesión de cliente (**exige** sesión).
- [x] Dependencia **`current_customer`**: lee `persona_id` de la sesión → entrega la `Persona`; sin sesión válida → 401.
- [x] Una **ruta protegida de prueba** con `current_customer` (paralela a `/auth/admin/check` de staff): sin sesión rechaza; con sesión expone la Persona correcta.
- [x] Tests (web `TestClient`, patrón `test_auth.py`): `request-otp` → 200; `verify-otp` válido abre sesión + redirige; inválido → mensaje genérico sin sesión; ruta protegida sin/con sesión; `logout` cierra solo la sesión de cliente; **login como staff no afecta `current_customer` y viceversa** (coexistencia verificada explícitamente).
