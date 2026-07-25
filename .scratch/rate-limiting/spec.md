# Spec — Rate limiting de login y solicitud de OTP

Status: ready-for-agent
Feature: rate-limiting
Branch: PaqueteXv.2
Depende de: `staff-auth` (`/auth/login`), `customer-otp-auth` (`/auth/customer/request-otp`).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §3 (Redis se mantiene para cache/rate-limit) · referencia de forma (no de código): `src/app/middleware/rate_limiting.py` viejo (slowapi + Redis, `5/minute` en login, "restrictivo por costos" en SMS).

---

## Problem Statement

Nada impide **fuerza bruta contra contraseñas de staff** en `/auth/login`, ni **spam de solicitudes de OTP** en `/auth/customer/request-otp` (que el día que exista un proveedor SMS real, cuesta dinero por cada solicitud — el sistema viejo ya lo marcaba explícitamente como "restrictivo por costos"). El hashing lento (bcrypt) y el máximo de intentos por código OTP ya construidos ayudan, pero no sustituyen un límite de **solicitudes por origen**. Verifiqué antes de escribir esta spec que la cookie de sesión ya usa `SameSite=Lax` (mitiga razonablemente el CSRF clásico) — eso bajó la prioridad de ese follow-up frente a este hueco, que sigue sin ninguna mitigación.

## Solution

Un **límite de solicitudes por IP** en las dos rutas de mayor riesgo — `POST /auth/login` y `POST /auth/customer/request-otp` — que rechaza con **429** cuando se excede, con un mensaje claro. La lógica vive en la **capa web** (es un concern de infraestructura/seguridad, no una regla de negocio de dominio — mismo criterio que ya separó `current_staff`/sesiones en `app/web/`, no en `app/domain/`).

## User Stories

1. Como **operador de sistema**, quiero que **intentos repetidos de login** desde el mismo origen se **limiten**, para dificultar la fuerza bruta de contraseñas.
2. Como **staff legítimo**, quiero que un límite razonable **no me bloquee** en el uso normal (algún error de tecleo ocasional), para no volverme la víctima de mi propia protección.
3. Como **operador de sistema**, quiero que **solicitudes repetidas de OTP** desde el mismo origen se **limiten**, para evitar abuso que —cuando haya un proveedor SMS real— generaría costo.
4. Como **residente legítimo**, quiero poder **reintentar pedir un código** un número razonable de veces (p.ej. si no me llegó), sin que el límite sea absurdamente estricto.
5. Como **quien excede el límite**, quiero un mensaje **claro** ("demasiados intentos, espera un momento"), no un error genérico confuso.
6. Como **arquitecto**, quiero que el límite se aplique **por IP**, consistente con el enfoque del sistema viejo (`get_remote_address`), como primera línea de defensa (no por cuenta/email — eso es una mejora futura).
7. Como **desarrollador**, quiero que la lógica de conteo sea un **puerto reemplazable** (mismo patrón que `OtpSender`/`NotificationSender`), para poder enchufar Redis en producción sin tocar las rutas.
8. Como **operador de sistema**, quiero que si el backend de conteo **falla** (p.ej. Redis caído, en el futuro), el sistema **no se caiga** — mejor dejar pasar la solicitud (fail-open) que bloquear todo el login por una dependencia caída.
9. Como **QA**, quiero probar el rate limit de punta a punta sin depender de un servidor Redis real en CI.

## Implementation Decisions

### Puerto + implementación en memoria (capa web, `app/web/rate_limit.py`)

- **`RateLimiter`** (Protocol): `permitir(clave: str, limite: int, ventana_segundos: int) -> bool` — `True` si la solicitud puede pasar (y cuenta hacia el límite), `False` si se excedió.
- **`InMemoryRateLimiter`**: ventana fija (`fixed-window`, mismo enfoque que el `slowapi` viejo) usando un diccionario en proceso — correcta para desarrollo, tests, y un despliegue de **un solo worker**. Documentada su limitación explícita: en un despliegue con **varios workers/procesos**, cada uno cuenta por separado (subestima el total real) — **Redis es el backend correcto para producción multi-worker**, pero su integración queda **fuera de esta rebanada** (ver Out of Scope; mismo patrón de honestidad que la integración real de SMS en `package-notifications` — no se escribe código de infraestructura externa sin poder probarlo).
- **Dependencia FastAPI** `rate_limit(nombre: str, limite: int, ventana_segundos: int)`: fábrica que devuelve una dependencia inyectable en la ruta; usa `request.client.host` como clave (`f"{nombre}:{ip}"`). Si el `RateLimiter` configurado lanza una excepción inesperada, **fail-open** (se deja pasar la solicitud) — la disponibilidad del login no debe depender de la infraestructura de conteo.

### Wiring en las rutas

- **`POST /auth/login`**: límite de **10 solicitudes / 60 segundos** por IP. Excedido → **429**, re-renderiza `auth/login.html` con mensaje "Demasiados intentos. Espera un momento e inténtalo de nuevo."
- **`POST /auth/customer/request-otp`**: límite de **5 solicitudes / 60 segundos** por IP (más estricto — es el vector "cuesta SMS"). Excedido → **429**, mismo patrón de mensaje sobre `auth/customer_login.html`.
- **No se añade** a otras rutas en esta rebanada (scope acotado a las dos de mayor riesgo real); la dependencia queda lista para reutilizarse en cualquier otra ruta sin trabajo adicional.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento observable por HTTP** — que tras N solicitudes el límite responde 429 con mensaje claro, que dentro del límite todo funciona normal, y que el fallo del backend de conteo no bloquea la ruta (fail-open) — no la implementación interna del contador.

**Costura (EXISTENTE, ninguna nueva de infraestructura):** **HTTP con `TestClient`**, usando el `InMemoryRateLimiter` (sin Redis en CI). Casos: `POST /auth/login` repetido más allá del límite → 429 en la solicitud que lo excede; por debajo del límite → sigue funcionando (login válido abre sesión igual que antes); `POST /auth/customer/request-otp` repetido más allá de su límite (más bajo) → 429; un `RateLimiter` que lanza excepción → la ruta **sigue respondiendo normal** (fail-open, verificado explícitamente).

**Prior art:** `tests/web/test_auth.py`/`test_customer_auth.py` (las rutas ya probadas, este ticket solo añade el límite encima sin romper sus casos existentes), `tests/web/test_notifications.py` (patrón de puerto + dependencia inyectable con `dependency_overrides`). Construir **test-first** con `/tdd`.

## Out of Scope

- **Backend Redis real** — el puerto queda listo; conectar una implementación Redis (INCR+EXPIRE) es un cambio de una sola implementación cuando se despliegue multi-worker, y no se escribe código no verificable contra un Redis real en este entorno (mismo patrón que la integración SMS real).
- **Límite por cuenta/email** (en vez de solo IP) — mejora futura; el sistema viejo tampoco lo tenía más allá de IP.
- **Rate limiting en otras rutas** (`/packages/*`, `/announce`, `/customer/verify`, `/announce-new`, `/admin/staff`) — fuera de alcance; la dependencia queda reutilizable si se decide extenderlo.
- **CSRF** — evaluado y **despriorizado** (no ignorado): `SameSite=Lax` ya mitiga razonablemente el caso clásico; no es el hueco más urgente ahora mismo.
- **Bloqueo de cuenta (lockout)** tras N intentos fallidos de login — distinto de rate-limit por IP; no incluido.

## Further Notes

- **Por qué no `slowapi`:** el sistema viejo lo usaba, pero trae su propio middleware/storage abstraction pensado para Redis desde el inicio; para esta rebanada (in-memory, puerto propio, sin Redis aún) un contador de ventana fija hecho a mano es más simple, más fácil de testear sin infraestructura externa, y consistente con el patrón de puertos ya usado (`OtpSender`, `NotificationSender`) en vez de adoptar una librería completa para una necesidad pequeña.
- **Fail-open, no fail-closed** — decisión deliberadamente **distinta** al override de notificaciones de staging (que es fail-closed a propósito, porque ahí el riesgo era filtrar SMS reales). Aquí el riesgo de fail-closed sería peor: una caída del backend de conteo dejaría a **todo el staff sin poder iniciar sesión**. Disponibilidad > protección perfecta en este caso específico.
- **Consumo aguas abajo:** la dependencia `rate_limit(...)` queda lista para cualquier ruta futura que la necesite, sin trabajo adicional.
