# Architecture review — PAQUETEX (CODE/)

**Fecha:** 2026-07-20 · **Rama:** `staging` @ `3223cab` (= `LIVE-PROD`)
**Alcance:** backend Python/FastAPI + Alembic en `CODE/` únicamente.

Ver también: [architecture-review.html](architecture-review.html) (versión con diagramas).

Vocabulario: módulo, interfaz, implementación, profundidad (profundo/superficial), seam, adapter, leverage, locality.

---

## Candidatos, ordenados por impacto

### 1. Colapsar el módulo de ciclo de vida de Package — `Strong` · local-substitutable

**Archivos:** `services/package_service.py` (830 líneas), `services/package_state_service.py` (1247 líneas), `services/package_event_service.py` (432 líneas), `models/package_history.py`, `routes/packages.py:580-611`

**Problema:** tres módulos gestionan el mismo ciclo de vida de Package sin un seam compartido — cada uno escribe su propio historial, ninguno es la fuente de verdad.

**Solución:** un único módulo `PackageLifecycle` con una interfaz de transición de estado; los tres colapsan detrás de ella.

- locality: los bugs de estado se concentran en un módulo
- leverage: una interfaz, todos los call sites
- interfaz se achica; la implementación absorbe los tres services

---

### 2. Un PackageQueryService — dejar de reinventar la paginación — `Strong` · local-substitutable

**Archivos:** `routes/packages.py:203-468,295-332,471+,1573-1672`, `routes/api.py:38-75`

**Problema:** cuatro implementaciones distintas de paginación/filtrado de paquetes, cada una con su propio criterio de límites y ordenamiento.

**Solución:** `PackageQueryService` como interfaz única de consulta; las cuatro rutas la llaman.

- leverage: un lugar para arreglar límites/paginación
- locality: bugs de búsqueda dejan de duplicarse

---

### 3. Deepen de la clasificación de variación de precio — una copia rota en silencio — `Strong` · in-process

**Archivos:** `services/invoice_v2_service.py:654-742,386-417`, `routes/invoices_v2_routes.py:863-897,995-1028`

> ⚠️ **Bug de producción activo:** la segunda copia lanza `AttributeError`, capturado por un `except` desnudo — la clasificación de reventa/consumo cae siempre al mismo valor por defecto sin que nadie lo note.

**Problema:** la regla de clasificación de variación de precio está triplicada; una copia está rota y el error se traga.

**Solución:** una única función de clasificación, testeada, sin duplicados.

- locality: la regla vive en un solo lugar
- quick win: candidato pequeño, aislado, corrige un bug activo

---

### 4. Darle a la composición de routers un seam real — `Strong` · in-process

**Archivos:** `main.py:262-292`, `routes/protected.py:1690,1380`, `routes/admin.py:100`, `routes/api.py:1298`

**Problema:** FastAPI/Starlette resuelve por orden de registro; dos pares de rutas idénticas quedan permanentemente sombreadas:
- `GET /api/admin/users` — `protected.py:1380` gana siempre, `admin.py:100` nunca se ejecuta
- `GET /api/packages/{tracking_number}/history` — `api.py:1298` gana siempre, `protected.py:1690` nunca se ejecuta

Descubierto de forma independiente en dos subsistemas distintos — es un patrón sistémico, no un caso aislado.

**Solución:** un módulo de composición de rutas con una interfaz que rechace colisiones al registrar, en vez de dejarlas en `main.py` implícitas por orden.

- leverage: un seam de registro, colisiones imposibles
- patrón sistémico: mismo defecto en dos módulos no relacionados

---

### 5. Que "no bloqueante" sea una propiedad de la interfaz de S3Service — `Strong` · mock

**Archivos:** `services/s3_service.py`, `routes/images.py`, `routes/packages.py:926-1141`

**Problema:** cada call site decide por su cuenta cómo tolerar fallos de S3 — la propiedad "no bloqueante" vive fuera del módulo, repetida de forma inconsistente.

**Solución:** S3Service expone una interfaz que ya es no bloqueante por diseño; puerto inyectado, adapter real en producción, adapter en memoria en tests.

- dos adapters justifican el seam: S3 real en prod, in-memory en tests
- leverage: la tolerancia a fallos deja de repetirse

---

### 6. Retirar la superficie admin fantasma de protected.py — `Strong` · local-substitutable

**Archivos:** `routes/protected.py:512-1040,1607-1679`, `services/admin_service.py:650-855`, `utils/auth_context.py:265-287`

**Problema:** `protected.py` mantiene su propia superficie admin paralela a `admin.py`, con lógica de permisos repetida.

**Solución:** retirar la superficie duplicada; una sola interfaz admin.

- interfaz se achica: protected.py deja de ser también admin
- locality: permisos de admin en un solo lugar

---

### 7. Colapsar el stack OTP/JWT del portal de clientes — `Strong` · local-substitutable

**Archivos:** `routes/customer_preferences_otp.py:65-368`, `services/customer_portal_service.py:74-495`, `routes/customer_preferences.py:36-190`

**Problema:** tres módulos implementan su propia variante de autenticación OTP/JWT para el portal de clientes.

**Solución:** un módulo `CustomerAuth` con una interfaz de verificación; los tres pasan a ser call sites.

- leverage: una interfaz de auth, N call sites
- locality: bugs de sesión se concentran en un módulo

---

### 8. Empujar borrado de clientes + reglas de calidad de datos hacia CustomerService — `Strong` · local-substitutable

**Archivos:** `routes/customers.py:179-284,580-723,725-956`, `services/customer_service.py:467-494`

**Problema:** `routes/customers.py` concentra reglas de borrado y validación de calidad de datos que deberían vivir detrás de la interfaz de `CustomerService`.

**Solución:** mover las reglas al service; la ruta llama a una interfaz de negocio, no ejecuta SQL/validación inline.

- interfaz de la ruta se achica
- locality: reglas de negocio de cliente en un módulo

---

### 9. Compartir el gate de preferencias de notificación entre canales — `Strong` · in-process

**Archivos:** `services/sms_service.py:132-224`, `services/email_service.py:178-273`, `routes/customer_preferences.py:50-93`, `models/user_preferences.py` (`should_send_notification`, líneas 50-100)

**Problema:** `should_send_notification` existe en `models/user_preferences.py`, pero SMS y email reimplementan su propio chequeo de preferencias en vez de pasar por el seam.

**Solución:** los dos canales consultan la misma interfaz de gate antes de enviar.

- leverage: una regla de preferencias, todos los canales

---

### 10. Borrar la flota fantasma — `Strong` · in-process

**Archivos:** 8+ módulos confirmados sin importadores, ~2.300 líneas — parser PDF `_new` abandonado, subsistema de descarga de CUFE muerto, modelos de invoice v1 huérfanos, wrapper S3 duplicado.

**Problema:** reescrituras abandonadas nunca se borraron; sin importadores, cero riesgo de romper nada al borrarlas, pero siguen confundiendo cualquier lectura del árbol de módulos.

**Solución:** borrar los 8+ módulos confirmados muertos.

- locality: el árbol de módulos deja de mentir
- ~2.300 líneas menos, cero riesgo

---

### 11. Reconciliar los dos stacks de almacenamiento de archivos desconectados — `Worth exploring` · local-substitutable

**Archivos:** `services/file_management_service.py`, `routes/files.py`, `services/s3_service.py`

**Problema:** `file_management_service.py` y `s3_service.py` resuelven almacenamiento de archivos sin compartir un seam — cada uno con su propio criterio de rutas y validación.

**Solución:** un módulo de almacenamiento único detrás de una interfaz.

- leverage: un criterio de almacenamiento

---

### 12. Darle a la capa de rutas una interfaz por donde testear — `Worth exploring` · local-substitutable

**Archivos:** `routes/public.py:502-678`, `routes/invoices_v2_routes.py:163,168,198,814-861`, cero archivos de test bajo `src/`

> ⚠️ No hay ningún archivo de test bajo `src/` — cualquier deepening en este repo carece hoy de una interfaz estable para testear a través de ella.

**Problema:** rutas de 1900+ líneas mezclan HTTP, SQL y lógica de negocio inline; no existe una interfaz de módulo contra la cual escribir tests.

**Solución:** extraer una interfaz de negocio por subsistema y testear contra ella, no contra la ruta HTTP.

- interfaz es la superficie de test

---

### 13. Delegar los contadores de badges de header a MessageService — `Worth exploring` · local-substitutable

**Archivos:** `services/header_notification_service.py:27-214`, `services/message_service.py:202-209`

**Problema:** `header_notification_service.py` recalcula conteos que `message_service.py` ya conoce.

**Solución:** header delega el conteo a la interfaz de MessageService.

- leverage: un solo lugar que sabe contar mensajes

---

## Top recommendation

### 1. Colapsar el módulo de ciclo de vida de Package

Es simultáneamente el enredo más grande y el que tiene el rastro de evidencia más claro: los últimos tres commits en `staging`/`3223cab` (`3223cab`, `6889048`, `71ce5c8`) son bugs que se rastrean directamente a esta falta de profundidad. Resolverlo despeja el terreno para el candidato 2, porque ambos viven en `packages.py`.

**Segundo lugar:** candidato 3 (clasificación de variación de precio) — es el único candidato que representa un comportamiento de producción activamente incorrecto en vez de deuda pura, y es lo bastante chico para arreglarse de forma aislada como quick win.
