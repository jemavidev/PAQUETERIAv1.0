# Spec — Autenticación de clientes (OTP por teléfono + sesión de cliente)

Status: ready-for-agent
Feature: customer-otp-auth
Branch: PaqueteXv.2
Depende de: `data-model` (Persona, Teléfono como llave), `staff-auth` (patrón de sesión/dependencia a replicar para la audiencia cliente), `announce-web`/`search-web` (capa web pública).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §9/§14 · `CONTEXT.md` (Persona, Teléfono, "Usuario = staff; Persona/Cliente = residente") · ADR-0004

---

## Problem Statement

El residente no tiene forma de **probar que es dueño de su teléfono**. Hoy anuncia con nombre+teléfono sin verificación (cualquiera puede escribir el teléfono de otro), y no existe sesión de cliente — lo que bloquea `/customer/verify` (autoedición de datos personales) y cualquier acción futura que deba **confiar** en que quien la ejecuta es esa Persona (p.ej. confirmar notificaciones a su nombre). El brief exige **OTP por teléfono** para clientes (baja fricción, ya lo dan al anunciar) — pero no existe ni la tabla, ni el flujo, ni la sesión.

## Solution

**OTP por teléfono** para clientes: el residente pide un código de 6 dígitos a su teléfono, lo confirma, y obtiene una **sesión de cliente** — independiente de la sesión de staff (dos audiencias separadas, `CONTEXT.md`). Esa sesión produce el `current_customer` (la **Persona** actual) que futuras rebanadas (`/customer/verify`, confirmaciones) usarán como identidad verificada.

- `POST /auth/customer/request-otp`: dado un teléfono, genera un código, lo asocia a ese teléfono con expiración y **máximo de intentos**, y lo **envía** (el envío real de SMS es otra rebanada — aquí el *puerto* de envío existe, con una implementación de desarrollo que no manda SMS real).
- `POST /auth/customer/verify-otp`: dado teléfono + código, si es válido y no expiró/agotó intentos → abre **sesión de cliente** (get-or-create la Persona por teléfono, igual que `announce`) y consume el OTP (no reutilizable).
- `current_customer`: dependencia que lee la sesión de cliente y entrega la **Persona** actual — la pieza que `/customer/verify` usará como gate.
- `POST /auth/customer/logout`: cierra la sesión de cliente.

## User Stories

1. Como **residente**, quiero pedir un **código a mi teléfono**, para verificar que soy yo.
2. Como **residente**, quiero recibir un código de **6 dígitos** con una **expiración corta** (minutos), para que no quede válido indefinidamente.
3. Como **residente**, quiero **confirmar el código** y quedar con **sesión abierta**, sin tener que crear una contraseña.
4. Como **residente**, quiero que un código **incorrecto** se rechace con un mensaje claro, sin abrir sesión.
5. Como **residente**, quiero que tras **varios intentos fallidos** el código quede **invalidado** (no fuerza bruta indefinida), y se me diga que pida uno nuevo.
6. Como **residente**, quiero que un código **expirado** se rechace igual que uno incorrecto, con mensaje claro de que pida uno nuevo.
7. Como **residente**, quiero que un código **ya usado** no pueda reutilizarse (un OTP es de un solo uso).
8. Como **residente nuevo**, quiero que verificar el OTP **cree mi Persona** si no existía (mismo registro implícito que `announce`, por Teléfono), para no duplicar el flujo de alta.
9. Como **residente existente**, quiero que verificar el OTP **reutilice mi Persona** (por teléfono normalizado), sin duplicarme.
10. Como **residente**, quiero **cerrar mi sesión** de cliente cuando termine, desde un dispositivo compartido.
11. Como **arquitecto**, quiero que la **sesión de cliente sea independiente** de la sesión de staff (cookies/keys separadas), para que un residente y un operador puedan estar autenticados en el mismo navegador sin pisarse.
12. Como **desarrollador**, quiero una dependencia **`current_customer`** (paralela a `current_staff`) que entregue la Persona de la sesión, para que rebanadas futuras (`/customer/verify`) la usen como gate.
13. Como **operador de sistema**, quiero que pedir OTPs repetidamente para el mismo teléfono en poco tiempo tenga algún **límite básico** (evitar spam/costo de SMS), aunque el enforcement fino sea de una rebanada posterior.
14. Como **QA**, quiero probar todo el ciclo (pedir → verificar → sesión → logout, y los rechazos) de punta a punta con `TestClient`, sin depender de un proveedor SMS real.
15. Como **dueño**, quiero que el **envío real de SMS** quede detrás de un *puerto* reemplazable, para que la integración real (y el override fail-closed de staging, brief §10) se resuelva en la rebanada de notificaciones sin tocar este flujo.

## Implementation Decisions

### Esquema (migración `0006`, descendiente de `0005`)

- Tabla nueva `otps_cliente`: `id` (UUID), `telefono` (canónico, indexado — no único, un teléfono puede pedir varios OTPs en el tiempo), `codigo_hash` (el código **no** se guarda en claro, se hashea igual que una contraseña — mismo principio que `staff-auth`), `intentos` (contador, default 0), `max_intentos` (p.ej. 5), `expira_en` (timestamp), `verificado_en` (nullable — marca de consumo), `created_at`. Índice sobre `telefono` para la búsqueda del OTP vigente. Constraints con nombre explícito (paridad esquema↔ORM). Árbol Alembic de raíz única (ADR-0002): `heads` = 1.
- Referencia de forma (no de esquema): el `CustomerOTP` viejo (`codigo`, `intentos`, `max_intentos`, `expira_en`, `verificado`) confirma que estos campos son el diseño de dominio correcto; el rebuild **no hereda** su tabla (UUID limpio, sin los campos `is_expired`/booleanos redundantes — la expiración se **calcula** contra `expira_en`, no se cachea en un booleano que puede desincronizarse).

### Servicio de dominio (costura existente — Seam A)

- `request_otp(session, telefono, sender) -> None`: normaliza el teléfono; genera un código de 6 dígitos aleatorio criptográficamente seguro; lo hashea y persiste con `expira_en = now + N minutos` (p.ej. 5); invoca `sender.enviar(telefono, codigo)` (el *puerto*, ver abajo) con el código **en claro** (el sender lo entrega al canal SMS; el dominio no lo retiene).
- `verify_otp(session, telefono, codigo) -> Persona`: busca el **OTP vigente** más reciente para ese teléfono (no verificado, no expirado, intentos < máximo); si no hay uno vigente o el código no coincide → incrementa `intentos` (si aplica) y lanza `ValueError` genérico ("código inválido o expirado"); si coincide → marca `verificado_en`, y hace **get-or-create** de la Persona por teléfono (mismo patrón que `announce`/`get_or_create_persona`) — el nombre para la creación implícita puede ser un placeholder mínimo si aún no se conoce (ajustable en `/customer/verify`).
- **Puerto de envío** (`OtpSender`, interfaz mínima): `enviar(telefono, codigo) -> None`. Esta rebanada entrega una implementación de **desarrollo/test** (registra el código sin mandar SMS real — p.ej. log o captura en memoria para los tests). La integración real (Twilio/proveedor + override fail-closed de staging, brief §10) es la rebanada de **notificaciones**; el puerto ya deja el punto de extensión.

### Sesión y dependencias (capa web — ADR-0004, patrón de `staff-auth`)

- **Sesión de cliente independiente**: misma técnica (`SessionMiddleware`, cookie firmada) pero con su **propia clave** en el diccionario de sesión (`persona_id`, distinta de `usuario_id` de staff) — ambas sesiones pueden coexistir en el mismo navegador sin conflicto.
- **`current_customer`**: dependencia paralela a `current_staff` que lee `persona_id` de la sesión y entrega la `Persona`; sin sesión válida → 401 (el 401→redirect ya existe en el app para staff; aquí se define su propio destino, p.ej. `/auth/customer/login` si una vista lo requiere — esta rebanada no monta ninguna vista gated todavía, solo la dependencia y las rutas de OTP).

### Rutas (capa web, públicas salvo logout que exige sesión)

- `GET /auth/customer/login`: formulario de teléfono (pedir OTP).
- `POST /auth/customer/request-otp`: teléfono → genera+envía OTP (vía el sender de dev) → muestra la pantalla de "ingresa el código".
- `POST /auth/customer/verify-otp`: teléfono + código → abre sesión de cliente + redirige (a una página mínima de confirmación; `/customer/verify` la reemplazará).
- `POST /auth/customer/logout`: cierra la sesión de cliente.
- Mensajes de rechazo **genéricos** (código inválido/expirado no distingue causa), igual que el login de staff.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento externo observable** — pedir OTP genera un código verificable (vía el sender de test, no un SMS real); el código correcto abre sesión y el incorrecto no; expiración e intentos agotados rechazan; el OTP no es reutilizable; `current_customer` entrega la Persona correcta y es independiente de `current_staff`.

**Costuras (ambas EXISTENTES, ninguna nueva):**
- **Dominio (Seam A):** `request_otp`/`verify_otp` contra Postgres efímero, con un `OtpSender` **fake/en memoria** para los tests (captura el código sin red). Casos: pedir OTP genera un registro con `codigo_hash` (no el código en claro); verificar el código correcto crea/reutiliza la Persona y marca `verificado_en`; código incorrecto → `ValueError`, sin sesión; expirado → rechazado; tras `max_intentos` fallidos → rechazado aunque el código sea correcto; verificar dos veces el mismo código → la segunda falla (no reutilizable).
- **HTTP (Seam web):** `TestClient`, patrón de `tests/web/test_auth.py`. Casos: `request-otp` → 200 con el paso siguiente; `verify-otp` válido → abre sesión de cliente + redirige; inválido → mensaje genérico, sin sesión; una ruta de prueba con `current_customer` → sin sesión rechaza, con sesión expone la Persona correcta; sesión de **staff** y de **cliente** coexisten sin pisarse (login como staff no afecta `current_customer` y viceversa); `logout` cierra solo la sesión de cliente.

**Prior art:** `tests/web/test_auth.py` (login/sesión de staff, mismo patrón a replicar), `tests/data_model/test_staff_service.py` (hashing + rechazo genérico). Construir **test-first** con `/tdd`.

## Out of Scope

- **Envío real de SMS/WhatsApp** y el override fail-closed de staging (brief §10) — rebanada de **notificaciones**; aquí solo el puerto `OtpSender` con su implementación de desarrollo.
- **`/customer/verify`** (autoedición de datos personales) — consume `current_customer`, pero es otra rebanada.
- **Rate-limiting real** de solicitudes de OTP (más allá de lo que la expiración/intentos ya acotan) — endurecimiento posterior (mismo follow-up que login de staff).
- **MFA / recuperación** — no aplica a clientes (OTP ya es el segundo factor de facto).
- **Vistas gated por `current_customer`** más allá de una ruta mínima de prueba — las vistas reales (`/customer/verify`) son rebanadas aparte.

## Further Notes

- **Independencia de sesiones** (staff vs cliente) es una decisión de diseño concreta que otras rebanadas darán por sentada — vale la pena verificarla explícitamente en los tests (coexistencia sin pisarse), no solo asumirla.
- **Placeholder de nombre** al crear la Persona vía OTP (sin nombre conocido aún): se deja como decisión menor de implementación (p.ej. cadena vacía o "Residente" hasta que `/customer/verify` lo complete) — no es un invariante de dominio, es UX de arranque.
- **Consumo aguas abajo:** `current_customer` es la pieza que `/customer/verify` y cualquier confirmación futura ("soy yo quien acepta esta notificación") usarán como identidad verificada.
