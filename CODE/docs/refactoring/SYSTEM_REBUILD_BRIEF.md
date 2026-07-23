# PAQUETEX — Brief del sistema nuevo (rebuild guiado por el sistema anterior)

**Fecha:** 2026-07-20 · **Refinado por grilling:** 2026-07-22
**Naturaleza:** no es un PR ni una serie de parches. Es un **sistema nuevo** cuyo diseño se informa del anterior: se conserva lo que funciona (look & feel, dominio, flujos probados), se rediseña la arquitectura, la base de datos parte de cero, y se corrige el código con bugs o ineficiente a su paso.
**Consumido por:** el siguiente paso de MATT (`/to-spec` → `/to-tickets`). El diseño ya pasó por una sesión de grilling; las decisiones quedaron en §6, §4, §5, §10, §14.
**Restricción dura asociada:** [DATABASE_CONSTRAINTS.md](DATABASE_CONSTRAINTS.md) — describe la base **actual** (28 tablas RDS) como fuente de verdad para la migración final, no como esquema a heredar.

---

## 1. Visión en una frase

Sistema de gestión de paquetería para un conjunto residencial, **mobile-first (90% celular)**, con dos audiencias: **staff con privilegios** que administra paquetes, y **clientes sin privilegios** (residentes, registrados o no) que anuncian y consultan. Debe correr en **AWS Lightsail** y ser **portable a cualquier nube** para recuperación ante desastres.

## 2. Principio rector: liviano y portable

Liviano y fácil de mantener gobierna cada decisión. **Corrección de sizing (grilling):** la meta inicial de $5/mes se descartó con evidencia — el box de producción actual (~1 GB / 2 vCPU) **ya vive en swap sin la base de datos encima** (74 MiB libres, ~1.5 GB en swap; la DB está en RDS). Meter Postgres a un box de $5 lo hunde igual. Sizing acordado: **prod ≈ 2 GB** (app+Postgres+Redis+Caddy cómodos), **staging ≈ 1 GB**. "Liviano" se logra recortando el stack (ver §3), no forzando RAM insuficiente.

---

## 3. Toolstack objetivo

| Capa | Decisión | Por qué |
|---|---|---|
| Backend | **FastAPI** (se mantiene) | El problema nunca fue el framework sino la organización del código. Liviano, ya conocido. |
| Frontend | **Server-rendered + Tailwind + Alpine/HTMX** (se mantiene) | Cero proceso Node en runtime. El look & feel ya es sólido. Un SPA iría contra "liviano". |
| DB | **PostgreSQL auto-hospedado en contenedor** (sale RDS), en el box de ~2 GB | Ver §5. RDS ata a AWS y encarece; el D/R portable se logra con dumps→S3, no con RDS. |
| Jobs background | **Consolidar en uno**: `BackgroundTasks` de FastAPI (fire-and-forget) + APScheduler in-process (periódicos) | Hoy corren **dos** sistemas en paralelo (Celery+Beat+broker Redis **y** un scheduler asyncio propio). Dos procesos Python que sobran. |
| Cache / rate-limit | **Redis** (se mantiene, deja de ser broker) | Ya lo usan `cache_manager.py` y `rate_limiting.py` — trabajo real. |
| Proxy / SSL | **Caddy** (reemplaza nginx+certbot) | Un binario, HTTPS automático, config mínima. |
| Observabilidad | **Logs estructurados a stdout + monitor externo (UptimeRobot) sobre `/health` + Sentry free** | Quitar Prometheus+Grafana+node-exporter: 3 contenedores pesados sin sentido en la caja. |
| Escaneo códigos de barra | **`@zxing/browser` (ZXing)** en navegador — motor **multi-formato** | Requisito (grilling): reconocer la **mayor variedad posible** de símbolos — Code128, Code39, EAN-8/13, UPC-A/E, ITF, Codabar, QR, DataMatrix, PDF417, Aztec. ZXing cubre el abanico más amplio en navegador (por encima de `html5-qrcode`, centrado en QR). Cámara del móvil, sin app nativa. Ver §7 modal Recibir. |

**Deuda de código a colapsar de paso:** dos servicios S3 duplicados (`s3_service.py` + `s3_storage_service.py`) → uno. El scheduler duplicado (arriba). Y las cicatrices de migraciones (`fix_migration_conflict.py`, `INSTRUCCIONES_*MIGRACION*.md`) desaparecen al partir el árbol Alembic de cero.

---

## 4. Infraestructura y CI/CD (2 instancias + GitHub)

**Flujo:** desarrollo local → push a GitHub → deploy automático a **staging** → aprobación manual → deploy a **producción**.

- **2 instancias Lightsail**: **prod ≈ 2 GB**, **staging ≈ 1 GB** (más barato), cada una con su propio Postgres en contenedor. Sizing acordado en grilling — ver §2.
- **GitHub Actions**: push a `main` → build imagen Docker → push a **GitHub Container Registry (ghcr.io, gratis)** → deploy a staging por SSH (`docker compose pull && up -d`) → `alembic upgrade head` automático en staging.
- **Gate a producción**: **GitHub Environments** con *required reviewers* en el environment `production`. El workflow se pausa esperando tu clic. Nativo de GitHub, sin herramienta extra. En prod, `alembic upgrade head` **con confirmación manual** (por el historial de incidentes de migraciones).
- **Secrets** (llaves SSH, credenciales S3) como GitHub Secrets. Nunca el `.pem` en el repo.

## 5. Disaster / Recovery sin RDS — y **más** portable que RDS

Requisito real: *"poder iniciar este proyecto en cualquier otra instancia de la nube."* RDS **no** cumple eso — te ata a AWS. La estrategia propuesta lo cumple mejor:

- **Datos (Postgres):** `pg_dump` automático (formato custom, comprimido) por cron → subido a **almacenamiento de objetos S3-compatible** (S3, o Cloudflare R2 / Backblaze B2 si se quiere salir de AWS), **cifrado y versionado**, con política de retención (p.ej. horarios 48 h + diarios 30 d).
- **Imágenes:** ya viven en S3 (`file_uploads.s3_key/s3_url`, durabilidad 11 nueves). Solo hay que **activar versioning** en el bucket. Ese es tu D/R de imágenes, sin cambios.
- **Runbook de recuperación:** provisionar cualquier instancia (cualquier nube) → `git clone` → `.env` → `docker compose up` → restaurar último dump desde S3 → imágenes ya están en S3. **RTO = minutos.**
- **RPO acordado (grilling): ~1 hora.** `pg_dump` **horario** → S3 (retención 48 h horarios + 30 d diarios). En el peor caso se pierden ~1 h de movimientos (unos pocos paquetes re-tecleables por el staff) — aceptable para el volumen. **WAL archiving** queda documentado como upgrade futuro (RPO casi-cero) si el volumen lo justifica, no se implementa de entrada.
- **Trade-off honesto:** RDS daba PITR al segundo y failover gestionado; esto da recuperación al último dump horario. Se aceptó a cambio de portabilidad total y costo.

## 6. Base de datos nueva — el cambio de modelo central (resuelto en grilling)

El corazón del rebuild. Todo lo demás (announce, search, customers, packages) cuelga de aquí. El modelo actual **no puede** representar lo que se necesita: hoy `cliente = teléfono` (único), el apartamento son 3 columnas sueltas sobre `customers`, y el paquete cuelga de **un** `customer_id` + un `display_name` de texto libre huérfano. Modelo nuevo, decidido pregunta a pregunta:

### Principios del modelo

1. **Teléfono = llave universal de la persona.** Siempre existe; es la identidad estable.
2. **Destinatario sin teléfono propio = un "nombre" bajo el teléfono de quien anuncia.** No hay personas sin llave. Esto elimina el `display_name` huérfano de hoy: ese nombre ahora vive bajo una identidad real (un teléfono) y, vía ese teléfono, bajo un apartamento.
3. **Apartamento = agrupador mutable, opcional.** Una persona tiene **un apartamento *actual*** que puede **cambiar (mudarse) o desvincularse** cuando sea. No es 1↔1 permanente; es 1↔1 *en el tiempo* (secuencial), no varios apartamentos a la vez.
4. **Herencia automática de apartamento, corregible.** Cuando a un teléfono de un grupo "misma unidad" se le asigna un apartamento, los demás del grupo lo heredan. El grupo se forma al **declarar la unidad a propósito** (staff en `/announce-new`, o el cliente en `/customer/verify`) — **no** por un "a nombre de" casual en `/announce`, que agruparía por error (ej.: un favor puntual entre personas de torres distintas). Y como mudarse/desvincular está siempre disponible, cualquier herencia errónea es corregible.
5. **El paquete congela (snapshot) su contexto de entrega al anunciarse:** `{anunciado_por (teléfono), nombre_destinatario, teléfono_destinatario (si hay), apartamento}` quedan **inmutables** en el paquete. Si la persona se muda después, los paquetes viejos **siguen mostrando el apartamento de entonces** — la mudanza nunca reescribe la historia. Esto materializa "los datos permanecen de principio a fin en cada paquete".

### Consecuencias de esquema

- **Persona** (llave: teléfono): nombre, apartamento_actual_id (nullable, mutable), datos de registro ampliables (email, doc, 2º contacto…), rol de auth de cliente (OTP).
- **Apartamento** (conjunto → torre → apto): entidad ligera, creable sobre la marcha, puede existir o no.
- **Paquete**: campos-foto `announced_by_phone`, `recipient_name`, `recipient_phone` (nullable), `apartment_snapshot` — más el estado del ciclo de vida. `guide_number` nullable (ver §7 Recibir).
- **Staff = entidad separada** (tabla `users`, roles ADMIN/OPERADOR). No es una Persona/cliente; auth distinta (ver §9-auth).
- **Registro implícito**: la Persona se crea al anunciar (teléfono + nombre). Amplía datos desde `/customer/verify`.
- **Árbol Alembic limpio**: una sola raíz. Se acaba el problema de las 3 raíces desconectadas del sistema viejo.

## 7. Vistas — **con** vs **sin** privilegios

### Sin privilegios (clientes, registrados o no)
`/announce`, `/search`, `/help`, `/terms`, `/privacy`, `/cookies`, `/customer/verify`, `/auth/login`, `/auth/forgot-password`.

- **`/announce`** — conservar nombre + teléfono + T&C. **Quitar** número de guía. **Agregar** selector de "a nombre de quién" (yo mismo / otra persona registrada con su teléfono / solo un nombre sin teléfono → queda bajo el teléfono de quien anuncia, §6). Este "a nombre de" casual **no** agrupa apartamentos (§6.4).
- **`/search`** — se mantiene. **Quitar** la mensajería cliente↔staff. Historial de estados **claro y legible** (timeline, no tabla), apoyado en `package_events` / `package_history`.
- **`/help`, `/terms`, `/privacy`, `/cookies`** — sin cambios.
- **`/customer/verify`** — tablero de autoedición de datos personales (el formulario completo de Residencia + contacto secundario). Arreglar sus bugs actuales **como parte** del rebuild.
- **`/auth/login`, `/auth/forgot-password`** — sin cambios. **OTP por teléfono se mantiene** para clientes.

### Con privilegios (staff)
`/packages`, `/announce-new`, `/customers/manage`, `/admin`.

- **`/packages`** (vista principal) — **quitar columna Guía/Código** (sin uso). **Unificar los modales** en un componente compartido (mismo título/botones/cierre) para consistencia. En móvil, modales como **bottom-sheet**.
  - Modal **Recibir** → **escaneo multi-formato** por cámara del navegador (ZXing; ver §3): el mayor abanico de símbolos 1D/2D. El número capturado va a `guide_number` como **referencia del transportador** — **opcional** (no todos los operadores la usan hoy). El emparejamiento anuncio↔paquete físico se hace **por nombre/teléfono** del destinatario. Diseñar dejando espacio para **promover la guía a llave de emparejamiento a futuro** sin romper el esquema (nos preparamos, no obligamos).
  - Modal **Entregar** → mostrar claramente el **destinatario snapshot** del paquete (§6.5) para confirmar quién retira; menos campos, botones grandes.
  - Modal **Cancelar** → **motivo obligatorio** (dropdown) para trazabilidad + aviso de irreversibilidad.
- **`/announce-new`** — declara la **unidad a propósito**: nombres **ilimitados** por apartamento, con o sin teléfono; por defecto el del que anuncia. Este flujo **sí** forma el grupo "misma unidad" que dispara la herencia de apartamento (§6.4). Info siempre ligada a un apartamento (registrado o no).
- **`/customers/manage`** — acotar a: buscar clientes, ver/editar info personal, gestión de notificaciones, eliminar cliente.
- **`/admin`** — rediseño una vez definido el resto: **alta de staff (solo un admin crea cuentas de staff)**, plantillas de notificación, gestión de residencias.

### Eliminar por completo
- **`/messages`** y todo el backend de mensajería/consultas asociado.

### Fuera de alcance (otra reestructuración)
- **`/invoices`, `/products`, Facturas/CUFE** — no se tocan en este rebuild.

## 8. Header / Footer

- **Header** — conservar: logo, anunciar, consultar, login (login solo para registrados con/sin privilegios). Considerar en móvil una **barra inferior fija** con las 3 acciones (mejor alcance del pulgar); logo minimalista arriba.
- **Footer** — conservar: "Desarrollado por JEMAVI | © 2026 PAPYRUS", "Ayuda", "WhatsApp", "Teléfono". Enlaces **`tel:` y `wa.me/` reales**, no solo texto.

## 9. Notificaciones + autenticación

**Notificaciones (SMS / WhatsApp):** se mantienen (existen `sms_configuration`, `sms_message_templates`, `sms_service.py`). Se conserva el mecanismo, integrándolo al nuevo modelo de eventos de paquete. **Salvaguarda de staging obligatoria** — ver §10.

**Autenticación (grilling):**
- **Clientes** — **OTP por teléfono** (bajo fricción, ya dan el teléfono).
- **Staff** — **usuario/email + contraseña fuerte**, entidad separada (`users`). Elegido sobre OTP-para-staff porque las cuentas de staff tienen poder destructivo (recibir/entregar/cancelar) y no deben depender del proveedor SMS para entrar a operar; OTP-SMS solo es débil para privilegiados (SIM swap). **MFA opcional a futuro.** **Solo un admin crea cuentas de staff.**

## 10. Sincronización staging ← producción (con datos reales, seguro)

Staging debe probar con **datos reales lo más actualizados posible**, reutilizando los mismos dumps del D/R (§5):

1. **Restore bajo demanda (grilling):** el staff pulsa "refrescar staging desde prod" → baja el último dump de prod desde S3 → lo restaura en el Postgres de staging. **No** automático nocturno: así hay menos ventanas con PII fresca en staging y quien dispara la sync sabe que el override debe estar puesto.
2. **Postura de PII (grilling):** se conservan **datos reales** (teléfonos/correos **intactos**) para máximo realismo — el owner priorizó realismo sobre ofuscar. Como el override queda como **única** barrera, debe ser **fail-closed**: `SMS_OVERRIDE_NUMBER` / `EMAIL_OVERRIDE` en el `.env` de staging redirigen **toda** notificación a un solo número/correo de prueba, y **si la config del override falta o no se puede leer, staging NO envía ningún mensaje a nadie** (deniega por defecto, nunca cae al envío real). Un solo guardia, pero que falla hacia el lado seguro.

## 11. Migración de datos (al final del rebuild)

- **Estrategia:** importar **lo viable**; el resto encaja con el tiempo. La base nueva puede arrancar y poblarse incrementalmente.
- **Fuente de verdad:** las 28 tablas reales de RDS (ver `DATABASE_CONSTRAINTS.md`), **no** los archivos de migración.
- **Mapeo al nuevo modelo (§6):**
  - cada `customers` (teléfono) → **Persona** (teléfono = llave);
  - columnas sueltas `building_name`/`tower`/`apartment` → crear/enlazar **Apartamento** y fijar el apartamento_actual de la persona;
  - cada `packages` → **snapshot** de `{anunció, nombre destinatario, teléfono, apartamento}` con los datos de ese paquete tal como estaban;
  - `display_name` actual → `recipient_name` del snapshot.
- **Imágenes S3:** re-vincular `s3_key`/`s3_url` existentes a los paquetes migrados (los objetos S3 no se mueven, solo se re-referencian).
- **"Encaja con el tiempo":** los apartamentos/torres que falten se completan a medida que los clientes usan `/customer/verify`.

## 12. Testing / CI — recomendación

**Hallazgo:** hay 63 archivos de test, pero casi todos son de CUFE/facturas/products/parser — **justo lo que queda fuera de alcance**. El ciclo de vida del paquete y el modelo de cliente **no tienen cobertura**.

**Recomendación (no perseguir 100%, cubrir donde un bug duele):**
- **Tests de integración** de los flujos núcleo: máquina de estados del paquete (anunciar→recibir→entregar→cancelar), modelo Residencia/apartamento, auth OTP. `pytest` + `httpx`/`TestClient` de FastAPI.
- **Contra un Postgres real efímero en CI** (servicio Docker en GitHub Actions) — así se prueban también las migraciones.
- Este es el **gate** que hace que "si todo pasa como se debe" signifique algo antes de aprobar el deploy a prod.
- Para el dominio núcleo, construir **test-first** con el skill `/tdd`.

## 13. Entregable final

Una **guía para usuario final en `.md`**, lo más **didáctica** posible (cualquiera la entiende sin fricción): explica cada punto del refactor, cómo queda toda la solución y cómo es el **nuevo flujo** (anunciar → recibir → entregar → consultar), diferenciando qué ve un cliente y qué ve el staff.

---

## 14. Decisiones cerradas por el owner

| Tema | Decisión |
|---|---|
| **Modelo de datos** | Teléfono = llave universal; destinatario sin tel = nombre bajo el tel del anunciante; apartamento = agrupador mutable (secuencial, no simultáneo); herencia corregible; **paquete = snapshot inmutable** (§6). |
| **Sizing** | Prod ≈ 2 GB, staging ≈ 1 GB. $5 descartado con evidencia de swap (§2). |
| **D/R** | pg_dump **horario** → S3 cifrado/versionado; **RPO ~1 h**; WAL = upgrade futuro; imágenes en S3 con versioning (§5). |
| **Staging** | Restore **bajo demanda**; datos reales intactos + override **fail-closed** (§10). |
| Auth clientes | OTP por teléfono. |
| Auth staff | Usuario/email + contraseña fuerte; MFA opcional futuro; solo un admin crea staff (§9). |
| Escáner / guía | Multi-formato (ZXing); `guide_number` opcional, referencia del transportador; match por nombre/tel; preparado para volverse llave a futuro (§7). |
| `file_uploads` | **Solo fotos de paquete** (facturas/CUFE fuera → se recorta el resto). |
| Migración | Importar lo viable; mapeo al modelo §6; el resto encaja con el tiempo (§11). |
| SMS/WhatsApp | Se mantienen; integrar al nuevo modelo de eventos. |
| Facturas/CUFE, Products | Fuera de alcance. |
| Testing/CI | Según recomendación (§12). |

## 15. Cabos por resolver en el spec

Las 5 preguntas del grilling quedaron resueltas (§14). Pendiente para la fase de `/to-spec`, ya como detalle de implementación:

1. **Eventos que disparan notificación** (¿anunciado / recibido / entregado? ¿SMS y WhatsApp o uno solo por evento?).
2. **Promoción de "nombre sin teléfono" a Persona** el día que esa persona registre su propio teléfono (¿fusión de historial?).
3. **Estrategia de ramas del rebuild** (rama de larga vida `rebuild/v2` + features por ticket; el repo trae historial de ramas enredado — ver notas de sesión).
4. **Detalle de la máquina de estados** del paquete (transiciones permitidas, quién puede cada una) para el componente de modal compartido (ver `PACKAGES_DIAGNOSIS.md`).
