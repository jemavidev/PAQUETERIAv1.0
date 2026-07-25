# 01 — Rate limiting en login y solicitud de OTP

**Spec:** `.scratch/rate-limiting/spec.md` · **Fuente:** brief §3 (Redis para rate-limit), referencia de forma `rate_limiting.py` viejo

**What to build:** `POST /auth/login` y `POST /auth/customer/request-otp` **rechazan con 429** cuando el mismo origen (IP) excede un número de solicitudes en una ventana de tiempo, con un mensaje claro. Por debajo del límite, ambas rutas funcionan exactamente igual que antes.

**Blocked by:** None — `/auth/login` (staff-auth) y `/auth/customer/request-otp` (customer-otp-auth) ya existen y están probadas.

**Status:** ready-for-agent

- [ ] **Puerto `RateLimiter`** (Protocol, `permitir(clave, limite, ventana_segundos) -> bool`) en `app/web/rate_limit.py` (capa web, no dominio) + **`InMemoryRateLimiter`** (ventana fija, diccionario en proceso).
- [ ] Dependencia FastAPI `rate_limit(nombre, limite, ventana_segundos)`: usa `request.client.host` como clave; si el `RateLimiter` configurado **lanza una excepción**, la solicitud **pasa igual** (**fail-open** — la disponibilidad del login no depende de esta infraestructura).
- [ ] `POST /auth/login`: límite **10/60s** por IP. Excedido → **429**, re-renderiza el formulario con "Demasiados intentos. Espera un momento e inténtalo de nuevo."
- [ ] `POST /auth/customer/request-otp`: límite **5/60s** por IP (más estricto). Excedido → **429**, mismo patrón de mensaje.
- [ ] **No** se toca ninguna otra ruta ni el comportamiento existente de ambas (login válido sigue abriendo sesión; OTP válido sigue generando/enviando código) mientras estén **por debajo** del límite.
- [ ] Tests HTTP (`TestClient`, `InMemoryRateLimiter`, sin Redis): solicitudes repetidas de login más allá de 10/60s → la que excede da 429 con el mensaje; por debajo del límite, login válido sigue funcionando igual que en `test_auth.py`; mismo patrón para `request-otp` con su límite de 5; un `RateLimiter` que lanza excepción (inyectado vía `dependency_overrides`) → la ruta **responde normal** (fail-open verificado explícitamente).
