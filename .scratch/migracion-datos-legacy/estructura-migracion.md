# Estructura de migración — PaqueteX legacy ("El Club" v4.0) → PaqueteXv.2

**Status: EJECUTADO COMPLETO — 2026-08-20.** Usuarios, Personas, Paquetes, Preferencias y
Fotos ya corrieron de verdad contra `test.papyrus.com.co`. Scripts reales: `importar.py` y
`copiar_fotos.py`, en esta misma carpeta.

## 9. Ejecución real (2026-08-20)

- **Ensayo local** (`paquetex_dev`, dos corridas): 1ª corrida crea todo sin errores; 2ª corrida
  (mismos datos) confirma idempotencia total — 0 creados, todo "saltado", 0 errores.
- **Corrección de seguridad tras el ensayo:** el chequeo de "¿ya existe este `access_code`?"
  original asumía que si el código ya existía, era porque ya se había migrado. Se corrigió para
  comparar también el teléfono — si el código ya existe pero pertenece a un teléfono distinto,
  se reporta como `COLISIÓN` (posible choque de un código de 4 caracteres generado nativamente
  por v2) en vez de saltarse en silencio y perder el paquete legacy.
- **`--dry-run` contra `test.papyrus.com.co` real** (antes de escribir): **0 colisiones** de
  `access_code` — limpio para proceder.
- **Corrida real contra `test.papyrus.com.co`** (dentro del contenedor `app`, vía
  `docker compose exec`, usando el `DATABASE_URL` real del servidor): `usuarios_creados: 4`,
  `usuarios_saltados: 1` (ya existía), `personas_creadas: 532`, `paquetes_creados: 2107`,
  `preferencias_creadas: 42`, **`errores: []`**.
- **Verificado en la base real post-import:** conteos distintos por clave natural
  (`access_code`, `telefono`) coinciden exactamente con el total de filas — sin duplicados.
  Paquete `71WG` verificado campo por campo (mismo que en los ejemplos de §8.3).
- Archivos temporales con datos reales (`/tmp/migracion` en el servidor, `/tmp/*.json` dentro
  del contenedor) — **borrados** tras confirmar el import.
- **Pendiente:** el ensayo local dejó datos reales de clientes (532 Personas, 2107 Paquetes,
  password hashes reales) en la base de desarrollo local (`paquetex_dev`) — no se limpió
  todavía, queda como decisión (¿la borro con `scripts/paquetex_dev_reset.sh`, o la dejás para
  seguir probando?).
- **Fotos (§5): EJECUTADO — 2026-08-20.** `copiar_fotos.py`, corrido en dos tandas dentro del
  contenedor `app` de `test.papyrus.com.co` (credenciales legacy pasadas por variable de
  entorno efímera, nunca escritas a disco). Key de destino derivada determinísticamente del
  `s3_key` legacy (`paquetes-recibidos-imagenes/legacy_<nombre-original>`), lo que hace el
  script idempotente por URL — verificado con una corrida chica primero (27 fotos, los 9
  paquetes `RECIBIDO`), confirmada pública (`HTTP 200`, `Content-Type: image/webp`, tamaño
  real) antes de escalar a las 6183 restantes. Resultado final: `copiadas: 6156`,
  `saltadas_ya_existe: 27` (las de la corrida chica, correctamente detectadas), `sin_paquete: 0`,
  `errores: []`. Total en base: **6183 `PaqueteFoto`, todas con URL única** (sin duplicados).
  Archivos temporales con credenciales/datos borrados del servidor tras confirmar.

**Fuente investigada en vivo:** `ssh paquetex` (`paquetex.papyrus.com.co`), Postgres RDS
(`paqueteria_v4`, empresa "PAQUETEX EL CLUB"), vía `.env` del servidor. Solo lectura —
no se modificó nada en el servidor legacy.

## 0. Decisiones ya tomadas (conversación 2026-08-19)

| Pregunta | Resolución |
|---|---|
| Alcance de tablas | `users`, `customers`, `packages`, `file_uploads` (ligadas a paquetes), `notifications`, `messages`, `customer_preferences` — corte al día en que se ejecute de verdad. |
| Facturación (`base_fee`/`storage_fee`/`total_amount`/`payment_*`) | **Archivo externo** (CSV/JSON), NO se importa al esquema de v2 — v2 no cobra, es solo referencia histórica por si el cliente pregunta. |
| `notifications` (log de envíos) y `messages` (soporte) | **Archivo externo** también — no hay tabla equivalente en v2 hoy y son telemetría/log, no datos de negocio (ver §2.6). |
| Base destino | Sin definir todavía por el cliente ("lo que tú recomiendes") — **recomiendo diseñar el importador idempotente por clave natural** (§3), para que sirva tanto contra una base vacía como contra `test.papyrus.com.co` (que ya tiene datos reales desde el 2026-08-10). |
| Fotos | **Resuelto (2026-08-19):** dado el conflicto bucket privado/público de legacy (§5), se descarta reusar el bucket legacy — las fotos se **copian** al bucket que v2 ya tiene configurado hoy (el "sistema de buckets orientado a lo que se tiene en este momento"), con la estructura/convención de nombres que v2 ya usa. No hay que repuntar `AWS_S3_BUCKET_NAME` ni tocar `S3FotoStorage` — es un job de copia legacy→v2, no un cambio de arquitectura. **Alcance: histórico completo, las 6129 fotos de los 2089 paquetes** (no solo las 27 de los 9 `RECIBIDO` actuales). |

**⚠️ Hallazgo importante (2026-08-19), responde "¿es obligatorio para algún flujo ya
iniciado?":** el sistema legacy **está en uso ahora mismo, en producción real** — al pedir
ejemplos para este documento, encontré paquetes con `announced_at` de *minutos* antes de la
consulta. Ningún flujo de v2 depende de esta migración (v2 opera de forma independiente y ya
está probado), pero el corte de datos ("hasta hoy") **es un objetivo móvil, no una foto fija**:
cualquier importador real tiene que asumir que legacy sigue recibiendo anuncios/recepciones/
entregas mientras se prepara la corrida, y decidir qué pasa con lo que cambie entre el
snapshot de prueba y la corrida final (ya apuntado en §6).

## 1. Volumetría real (medida hoy, 2026-08-19)

| Tabla legacy | Filas | Nota |
|---|---:|---|
| `users` | 7 (5 en alcance real, ver §8.1) | 5 activos (1 ADMIN + 4 OPERADOR) + 2 inactivos excluidos de la migración: `test_cache` (cuenta de prueba) y `Santiago Arrazola` (ex-operador, decisión 2026-08-19: no migra) |
| `customers` | 531 (los 531 migran, ver §6) | 531 teléfonos únicos (sin duplicados) — 2 con email, 0 con documento, 0 con torre/apartamento; 33 sin ningún paquete asociado, migran igual como Persona pura |
| `packages` | 2089 | 100% con `customer_id` y `guide_number`; 9 siguen `RECIBIDO` hoy (el más reciente, ayer) |
| `file_uploads` | 6129 | 100% `IMAGEN`; 27 pertenecen a los 9 paquetes `RECIBIDO` actuales |
| `package_announcements_new` | 2099 (0 migran) | 10 nunca llegaron a convertirse en `packages` (anuncios abandonados) — **se descartan, no entran al importador** |
| `customer_preferences` | 7 | de 531 clientes — el resto nunca tocó configuración, corren con el default de la app vieja |
| `notifications` | 6514 | 100% SMS/EMAIL, `SENT`/`FAILED` — log de envíos, no contenido de negocio |
| `messages` | 2 | soporte general, ninguno ligado a un paquete |
| Rango operativo | — | `packages.announced_at` va de 2025-11-25 a 2026-08-18 — sistema activo hasta ayer |
| Facturación/inventario (`invoices*`, `products*`, `suppliers*`, `rates`, `cufe_records`) | ~0-37 | módulo de facturación electrónica/proveedores, prácticamente sin uso — **no se investiga más, no aplica al alcance** |

**Compatibilidad ya confirmada** (por qué esta migración es más simple de lo que parece):
- Los enums de estado/tipo/condición/rol **ya usan el mismo vocabulario en español** que v2
  (`RECIBIDO`/`ENTREGADO`/`CANCELADO`, `NORMAL`/`EXTRA_DIMENSIONADO`, `BUENO`/`REGULAR`/`ABIERTO`,
  `ADMIN`/`OPERADOR`) — mapeo directo, sin tabla de traducción.
- Los teléfonos de `customers` **ya están en la forma canónica E.164** que usa
  `normalizar_telefono` de v2 (`+573001234567`) — no hace falta limpieza.
- Los `password_hash` de `users` son **bcrypt `$2b$12$`**, el mismo algoritmo y costo que usa
  `staff_service.py` en v2 — técnicamente portables tal cual (ver §6 sobre si conviene igual).

## 2. Mapeo tabla por tabla

### 2.1 `users` → `Usuario`

| legacy | v2 | Transformación |
|---|---|---|
| `id` (int) | — | no existe en v2 (PK es UUID) — se necesita un **cruce id-legacy → uuid-v2** (§3) si algo más lo referencia |
| `full_name` | `nombre` | tal cual |
| `email` | `email` | tal cual (ya es la llave de login en ambos sistemas) |
| `password_hash` | `password_hash` | copiar tal cual — mismo formato bcrypt, **hereda la contraseña actual sin forzar cambio** (decisión 2026-08-19, ver §6) |
| `role` (`ADMIN`/`OPERADOR`) | `rol` | mapeo directo, mismos valores |
| `is_active` | `activo` | **filtro de entrada al importador, no solo un campo a copiar** — de las 7 filas legacy, 2 están `is_active=false` y **quedan excluidas del import** (decisión 2026-08-19, ver §8.1: `test_cache` por ser cuenta de prueba, `Santiago Arrazola` por decisión explícita). Solo migran las **5 filas `is_active=true`**, todas con `activo=true` en v2. |
| `username`, `phone`, `created_at`, `updated_at` | — | **no tienen destino en v2** (`Usuario` no tiene `username` ni `phone`) — se descartan |

### 2.2 `customers` → `Persona`

| legacy | v2 | Transformación |
|---|---|---|
| `id` (uuid) | — | UUID legacy y UUID v2 **no tienen que coincidir** — igual conviene un cruce id-legacy → uuid-v2 (`packages.customer_id` depende de esto) |
| `phone` | `telefono` | tal cual (ya canónico, ver §1) — es la clave natural de emparejamiento (§3) |
| `full_name` (o `first_name ~ ' ' ~ last_name`) | `nombre` | usar `full_name` directo, ya viene armado |
| `email` | `email` | tal cual (solo 2 de 531 lo tienen) |
| `document_number`, `document_type` | `documento`, `tipo_documento` | tal cual — pero **0 de 531 tienen esto**, así que en la práctica quedan `NULL` para todos |
| `tower`, `apartment`, `building_name`, `floor`, `address_*` | `apartamento_actual_id` | **sin dato migrable — 0% de los 531 tiene torre/apartamento diligenciado en legacy.** Todas las Personas migradas entran con `apartamento_actual_id = NULL` ("Sin apartamento"), igual que hoy hace `get_or_create_persona` cuando no hay match. El staff las asigna manualmente después, con el flujo que ya existe. |
| `whatsapp_usuario`... | — | legacy no tiene este concepto (no existía WhatsApp-only en "El Club") — todas las Personas migradas necesariamente tienen `telefono`, nunca solo-WhatsApp |
| `is_active`/`is_vip`/`total_packages_*`/`total_spent`/`notes`/`preferred_language` | — | sin destino en v2 (dominio de v2 no rastrea esto) — se descartan, o van al archivo externo de referencia si el cliente quiere conservar el histórico de "cliente VIP"/notas |
| `segundo_contacto` (v2) | — | sin origen en legacy — queda `NULL` para todas las migradas |

### 2.3 `packages` → `Paquete`

Nota conceptual importante: **legacy no distingue "quién anuncia" de "para quién es"** — un
solo `customer_id` por paquete. v2 sí distingue (`announced_by_persona_id` obligatorio vs.
`recipient_name`/`recipient_phone`, la costura que se tocó varias veces esta semana en
`corregir_destinatario`). Para paquetes migrados, **ambos roles apuntan a la misma Persona**
(no hay forma de reconstruir la distinción retroactivamente).

| legacy | v2 | Transformación |
|---|---|---|
| `id` (int) | — | cruce id-legacy → uuid-v2 (para que `file_uploads` pueda resolver `paquete_id`) |
| `tracking_number` **(⚠️ no `access_code`, ver corrección abajo)** | `access_code` | tal cual |
| `access_code` (el campo legacy que se llama así) | — | **sin destino en v2** — ver corrección abajo |
| `guide_number` | `guide_number` | tal cual (100% de los legacy lo tienen) |
| `package_type` | `package_type` | mapeo directo (`NORMAL`/`EXTRA_DIMENSIONADO`, mismos valores) |
| `package_condition` | `package_condition` | mapeo directo (`BUENO`/`REGULAR`/`ABIERTO`, mismos valores) |
| `status` | `estado` | mapeo directo (`RECIBIDO`/`ENTREGADO`/`CANCELADO`, mismos valores — hoy no hay ningún `ANUNCIADO` en legacy) |
| `customer_id` → `customers.full_name`/`.phone` | `announced_by_persona_id` **y** `recipient_name`/`recipient_phone` | mismo Persona para los dos roles (ver nota arriba) |
| `display_name` | `recipient_name` | usar si existe; si no, cae a `customers.full_name` |
| `announced_at`/`received_at`/`delivered_at`/`cancelled_at` | mismos campos | copiar tal cual — **normalizar a UTC** (legacy mezcla `timestamp with time zone` y `without time zone` según la tabla, ver §6) |
| `created_by`/`updated_by` (id de `users`) | `announced_by_usuario_id`/etc. | **100% NULL en las 2107 filas actuales — no hay dato que migrar acá.** Ver corrección abajo sobre `package_history.changed_by` como fuente alternativa parcial. |
| `tower`/`apartment`/`snapshot_*` | `snapshot_conjunto`/`snapshot_torre`/`snapshot_apartamento` | **sin dato — quedan NULL**, mismo motivo que en `customers` (§2.2) |
| `posicion` (slot físico único) | — | **sin equivalente en v2.** Si el nuevo sistema también usa casilleros físicos numerados, esto es una brecha real a decidir (ver §6) — si no, se descarta sin problema |
| `base_fee`/`storage_fee`/`total_amount` | — | **archivo externo**, no se importa (decisión ya tomada, §0) |
| `cancel_reason` | `cancel_reason` | **corrección:** NO viene de `package_events.cancellation_reason` (100% NULL, ese campo nunca se usó) — viene de `package_history.observations`, texto libre `"Cancelado por: <motivo>."` en las 8 filas `CANCELADO` que existen hoy. Ver ejemplos abajo. |

#### ⚠️ Corrección importante (2026-08-19, encontrada al pedir ejemplos reales)

Legacy tiene **dos códigos distintos** por paquete, y mi primer mapeo asumió mal cuál es cuál:

- `packages.access_code` — 8 caracteres alfanuméricos (`secrets.choice`, ej. `SVE1P79C`),
  generado por `package_service.py::_generate_access_code()`. **Nunca aparece en el contenido
  real de los SMS que le llegan al cliente** (verificado contra `notifications.message`).
- `packages.tracking_number` — 4 caracteres (`random.choices(..., k=4)`, ej. `HSZN`), generado
  por `announcements_service.py`, ahí literalmente llamado `tracking_code`. **Este SÍ es el que
  aparece en el SMS real** que recibe el cliente, y su longitud/formato coincide exactamente con
  el `access_code` de v2 (`W6JQ`, `6S4B`, etc. — siempre 4 caracteres).

**Mapeo corregido: `legacy.tracking_number → v2.access_code`** (no `legacy.access_code`). El
campo `access_code` de legacy queda sin destino en v2 — es un identificador interno que el
cliente nunca vio.

**Segunda corrección, mismo ejercicio:** `packages.created_by`/`updated_by` (FK a `users.id`)
están en **NULL el 100% de las 2107 filas** — nunca se usaron. La única traza de "quién hizo
qué" que existe de verdad es `package_history.changed_by`, un campo de **texto libre**, no una
FK — y no siempre matchea un `username` real: de los valores encontrados, `rafael`,
`MARIANELLA`, `jveyes`, `jesus` sí coinciden con `users.username` reales, pero `operator_1` no
coincide con ningún usuario existente (probablemente una etiqueta genérica de un flujo
automático viejo). Conclusión: la atribución de actor (`received_by_usuario_id`, etc.) **se
puede resolver parcialmente** cruzando `package_history.changed_by` contra `users.username` — y
para lo que no matchee (como `operator_1`), queda `NULL`.

### 2.4 `file_uploads` → `PaqueteFoto`

| legacy | v2 | Transformación |
|---|---|---|
| `package_id` | `paquete_id` | vía el cruce id-legacy → uuid-v2 de paquetes |
| `s3_url` / `s3_key` | `url` | **no es un copiar-y-pegar directo** — ver §5, requiere resolver primero dónde van a vivir las fotos |
| `filename`, `file_size`, `content_type`, `file_type` | — | **v2 no los guarda** (`PaqueteFoto` solo tiene `id`/`paquete_id`/`url`/`created_at`) — se pierden como metadata estructurada, aunque casi todo es `IMAGEN`/`.webp` de todas formas |
| `created_at` | `created_at` | tal cual |

### 2.5 `customer_preferences` → `PersonaPreferenciaNotificacion`

Cambio de forma: legacy tiene **una fila por cliente** con varias columnas booleanas; v2 tiene
**una fila por combinación (Persona, Canal, Evento)** — hay que "explotar" cada fila legacy en
varias filas v2.

| legacy (una fila) | v2 (produce hasta 8 filas: 2 canales × 4 eventos) |
|---|---|
| `sms_notifications_enabled` AND `notify_package_announced` | fila `(persona, SMS, ANUNCIADO, activo=?)` |
| `sms_notifications_enabled` AND `notify_package_received` | fila `(persona, SMS, RECIBIDO, activo=?)` |
| `sms_notifications_enabled` AND `notify_package_delivered` | fila `(persona, SMS, ENTREGADO, activo=?)` |
| (sin evento CANCELADO explícito en legacy) | fila `(persona, SMS, CANCELADO, ...)` — **sin dato de origen, no crear fila** (queda en el default de v2, ver nota) |
| mismas 4 combinaciones con `email_notifications_enabled` | filas `(persona, EMAIL, <evento>, activo=?)` |
| `notify_payment_due`, `marketing_enabled` | **sin evento/concepto equivalente en v2** — se descartan |
| (canales `LLAMADA`/`WHATSAPP` de v2) | **sin origen en legacy** — no se crean filas, quedan en el default de v2 |

Solo aplica a los **7 clientes que tienen fila en `customer_preferences`**. Los otros 524 no
generan ninguna fila — `preferencia_notificacion_service.preferencia_activa` ya resuelve la
ausencia con su propio default (documentado en `preferencia_notificacion.py`: SMS activo solo
para `ANUNCIADO`), así que no hay que inventar nada para ellos.

### 2.6 `notifications`, `messages`, facturación → archivo externo (NO entran al esquema de v2)

Ya decidido en §0. Estructura sugerida para el/los archivo(s) de referencia:

- `facturacion_legacy.json` — un objeto por paquete migrado: `{tracking_number, access_code,
  base_fee, storage_fee, total_amount, payment_method, payment_amount, payment_received}`
  (los dos últimos vienen de `package_events`, no de `packages`).
- `notifications_legacy.json` (o `.csv`, dado el volumen de 6514 filas) — log crudo, filtrado
  a los paquetes migrados si se quiere acotar el tamaño.
- `messages_legacy.json` — las 2 filas completas, sin transformar (volumen trivial).

Estos archivos se generan **una sola vez, junto con el resto del export**, y viven fuera de la
base de datos de v2 — el objetivo es que alguien pueda abrirlos y buscar manualmente si el
cliente pregunta por un cobro o un mensaje viejo, no que la app los consulte.

## 3. Claves de emparejamiento (para que el importador sea idempotente)

Recomendado — el importador debe poder correr más de una vez sin duplicar, sin importar si la
base destino está vacía o ya tiene datos reales:

| Entidad | Clave natural para "ya existe, no dupliques" |
|---|---|
| `Usuario` | `email` (único en ambos sistemas) |
| `Persona` | `telefono` (canónico, único en ambos sistemas — y ya es la identidad universal de v2, ADR-0003) |
| `Paquete` | `access_code` (único en ambos) |
| `PaqueteFoto` | no tiene clave natural propia — atarla a "ya migré este `file_uploads.id`" vía la tabla de cruce (abajo) |
| `PersonaPreferenciaNotificacion` | `(persona_id, canal, evento)` — ya es `UNIQUE` en v2 |

**Tabla de cruce (recomendación propia, no pedida explícitamente):** una tabla puente temporal
`legacy_id_map(entidad, id_legacy, id_v2)` — se llena durante el import y permite: (a) resolver
FKs entre pasos (`file_uploads.package_id` → `Paquete.id`) sin tener que re-consultar por clave
natural cada vez, (b) volver a correr el importador y saltarse lo ya migrado, (c) auditar
después "esta fila de v2 vino de tal fila legacy". Se puede armar como tabla real (barata de
crear y borrar) o como archivo (CSV/JSON) si se prefiere no tocar el esquema de v2 para esto.

## 4. Orden de ejecución (por dependencias FK)

```
1. Usuario                    (sin dependencias)
2. Persona                    (sin dependencias)
3. Paquete                    (depende de Persona; opcionalmente de Usuario para los *_usuario_id)
4. PaqueteFoto                (depende de Paquete)
5. PersonaPreferenciaNotificacion   (depende de Persona)
   -- en paralelo, sin tocar la BD de v2 --
6. Exports externos (facturación, notifications, messages)
```

## 5. Fotos — la tensión pendiente de resolver

Esto ya se investigó antes en este mismo proyecto (`.scratch/fotos-multiples-s3/spec.md`,
2026-08-02) y quedó resuelto de una forma que el pedido de hoy reabre:

- **Legacy** (`s3_service.py`): bucket `elclub-paqueteria`, sube con `ACL='private'`, sirve por
  URL firmada con expiración (~1h) — correcto ahí porque ese bucket también guarda facturas
  sensibles. Prefijo real observado: `YYYY/MM/DD/packages/announcement_<code>/receive/
  <code>_<timestamp>_<seq>.webp`.
- **v2 hoy** (`s3_foto_storage.py`, ya activo en producción — confirmado que
  `AWS_S3_BUCKET_NAME`/`AWS_S3_ACCESS_KEY_ID`/`AWS_S3_SECRET_ACCESS_KEY` ya están configurados
  en `test.papyrus.com.co`): bucket **separado a propósito** ("staging, distinto del real de
  producción"), sube con `ACL='public-read'` — necesario porque `/consultar` es pública sin
  sesión y no hay flujo para refrescar una URL firmada vencida.

**Resuelto (2026-08-19):** dado el conflicto privado/público de arriba, se descarta reusar el
bucket legacy — en vez de repuntar v2 hacia `elclub-paqueteria`, **las fotos se copian hacia el
bucket que v2 ya tiene configurado hoy**, con la convención de nombres/prefijo que
`S3FotoStorage` ya usa (`AWS_S3_PREFIX_FOTOS`, hoy `paquetes-recibidos-imagenes/`). Cero cambios
de arquitectura en v2 — es un job de copia legacy→v2, no un rewiring de `S3FotoStorage`.

**Plan concreto:**
1. Por cada `file_uploads` en alcance: `get_object` del bucket legacy (`elclub-paqueteria`,
   con las credenciales que ya están en `ssh paquetex`, ACL privada) → `put_object` al bucket
   de v2 (credenciales ya presentes en `test.papyrus.com.co`, ver `AWS_S3_BUCKET_NAME`/
   `AWS_S3_ACCESS_KEY_ID`/`AWS_S3_SECRET_ACCESS_KEY` confirmados en su `.env`) con
   `ACL='public-read'`, bajo el prefijo propio de v2 — mismo flujo que ya hace
   `S3FotoStorage.guardar`, solo que el `contenido: bytes` viene de S3 en vez de un
   `UploadFile` del formulario.
2. La URL resultante (`https://<bucket-v2>.s3.<region>.amazonaws.com/<prefijo>/<key>`) es la
   que se guarda en `PaqueteFoto.url` — no se reutiliza ni se referencia el `s3_url`/`s3_key`
   legacy para nada, una vez copiada la foto es 100% independiente del sistema viejo.
3. **Resuelto (2026-08-19): alcance completo** — las 6129 fotos de los 2089 paquetes, no solo
   las 27 de los 9 `RECIBIDO` actuales. Mismo criterio que el resto de la migración ("hasta el
   día de hoy" ya significaba histórico completo para `packages`/`customers`; esto lo alinea).

## 6. Qué agregaría yo (no lo mencionaste, pero lo marcaría antes de construir el importador)

- **`package_announcements_new` con 10 filas sin `package_id`** — son anuncios que el cliente
  legacy nunca confirmó como paquete recibido/físico. **Resuelto (2026-08-19): se descartan**,
  no se convierten en `Paquete` en v2.
- **33 `customers` sin ningún `package`** — clientes registrados que nunca tuvieron actividad.
  **Resuelto (2026-08-19): migran igual**, como Persona pura (identidad, sin paquetes
  asociados) — el directorio completo de 531 Personas entra al importador, no solo los que
  tienen actividad.
- **Fecha de corte móvil**: "hasta hoy" va a significar una fecha distinta el día que
  realmente corras el importador (los 9 `RECIBIDO` de hoy bien podrían ser `ENTREGADO` para
  entonces). El importador necesita tomar el snapshot en el momento de la corrida, no una
  fecha fija — y hay que decidir qué pasa si un paquete cambia de estado en legacy *entre* que
  se prueba el importador y se corre "de verdad" (¿se re-corre completo, o solo el delta?).
- **Zona horaria mixta en legacy**: algunas tablas usan `timestamp with time zone`
  (`packages`, `file_uploads`) y otras `timestamp without time zone`
  (`package_history`, `customers`, `customer_preferences`) — normalizar todo a UTC al importar,
  v2 es consistente en `DateTime(timezone=True)` en todas sus tablas.
- **Contraseñas de staff — resuelto (2026-08-19): se heredan tal cual.** El `password_hash`
  bcrypt (`$2b$12$`) de los 5 usuarios en alcance se copia directo a v2, sin forzar cambio en
  el primer login — cada uno sigue entrando con la misma contraseña que ya usa hoy en legacy.
- **Reporte de la corrida**: cada ejecución del importador (aunque sea en modo referencia)
  debería dejar un resumen — cuántas filas entraron, cuántas se saltaron por ya existir,
  cuántas se rechazaron y por qué. Sin esto es difícil confiar en una corrida contra una base
  que ya tiene datos reales.
- **Modo simulación (`--dry-run`)**: poder correr todo el mapeo sin escribir nada, para
  validar conteos antes de tocar `test.papyrus.com.co` de verdad.
- **`posicion`** (slot físico único de legacy, ej. casillero numerado): si el nuevo sistema
  también opera con posiciones físicas asignadas, es una brecha real — v2 hoy no tiene ese
  concepto. Si no aplica al nuevo flujo, se descarta sin problema.

## 7. Qué necesito para que el importador real sea posible (checklist)

1. **Credenciales operativas para el job de copia S3-a-S3** (6129 objetos, alcance completo ya
   confirmado): técnicamente ya existen en ambos extremos (lectura en `ssh paquetex`, escritura
   ya configurada en `test.papyrus.com.co`) — falta decidir DESDE DÓNDE corre el job (¿la misma
   sesión que ya tiene `ssh paquetex`? ¿un script que vos corrés con ambas credenciales a
   mano?), no si existen. A ese volumen conviene pensar en throttling/reintentos, no un loop
   simple sin manejo de fallos parciales.
2. **Acceso de escritura a la base de v2 destino**: hoy solo puedo escribir en el Postgres
   local de desarrollo directamente; contra `test.papyrus.com.co` el único canal que uso hoy es
   el mecanismo de CI/CD (mismo truco que el reset de datos del 2026-08-19) — si el importador
   real va a correr contra un servidor, necesito saber si se ejecuta así o si vas a correrlo vos
   mismo con un script que yo te entregue.

Nada de esto bloquea tener la estructura de arriba lista para cuando decidas construir el
importador — son las preguntas que sí van a bloquear el *código*, no el documento.

## 8. Ejemplos reales, campo por campo (pedido 2026-08-19)

Datos reales de hoy, consultados en vivo contra `ssh paquetex`. Formato: `Legacy → v2`. Se
omiten los campos 100% vacíos en legacy (`document_number`, `tower`/`apartment`, etc.) — ya
están marcados como "sin dato" en el mapeo de §2, mostrar 5 ejemplos de `NULL → NULL` no aporta.

### 8.1 `Usuario` (de `users`)

| Campo | 5 ejemplos reales (`legacy → v2`) |
|---|---|
| `full_name` → `nombre` | `JESUS VILLALOBOS → JESUS VILLALOBOS` · `RAFAEL TORRES → RAFAEL TORRES` · `JESUS MARIA VILLALOBOS → JESUS MARIA VILLALOBOS` · `MARIANELLA VILLALOBOS ESCOBAR → MARIANELLA VILLALOBOS ESCOBAR` · `MAYERLIN TERESA ZABALA → MAYERLIN TERESA ZABALA` |
| `email` → `email` | `jveyes@gmail.com` · `rafael@papyrus.com.co` · `jesus@papyrus.com.co` · `maryvillaescobar@gmail.com` · `mayte.2794@gmail.com` (tal cual, sin transformar) |
| `role` → `rol` | `ADMIN → ADMIN` (×2) · `OPERADOR → OPERADOR` (×5) — mapeo directo |
| `is_active` → `activo` | `t → true` (×5, staff real) · `f → false` (×2 — **ver hallazgo abajo**) |
| `password_hash` → `password_hash` | formato `$2b$12$...` en los 7 — se copia el hash completo tal cual (no lo imprimo acá, son credenciales reales) |
| `username`, `phone` | **sin destino en v2** — se descartan (`Usuario` no tiene estos campos) |

**⚠️ Hallazgo:** mi conteo original (§1) decía "todos `is_active=true`" — **estaba mal**, nunca
lo verifiqué campo por campo, solo agrupé por `role`. La realidad: **5 activos, 2 inactivos**.

**Decisión (2026-08-19, confirmada):** ninguno de los 2 inactivos migra.
- `test_cache` (`email=test@cache.com`, `full_name="Test Cache User"`) — cuenta de prueba, nunca
  fue staff real.
- `Santiago Arrazola` (`username=Santiago`, `OPERADOR`, inactivo) — ex-operador real, pero
  confirmado que **no se migra**.

**Candidatos reales a migrar: 5** (1 ADMIN + 4 OPERADOR, todos activos) — `jveyes`, `rafael`,
`jesus`, `MARIANELLA`, `maye`. Ninguno de los 2 inactivos entra al importador ni como staff
desactivado de referencia.

### 8.2 `Persona` (de `customers`)

| Campo | 5 ejemplos reales (`legacy → v2`) |
|---|---|
| `phone` → `telefono` | `+573146007619 → +573146007619` · `+573023873660 → +573023873660` · `+573135694070 → +573135694070` · `+573012785583 → +573012785583` · `+573016550168 → +573016550168` (ya canónico, cero transformación) |
| `full_name` → `nombre` | `GISHE HERRERA → GISHE HERRERA` · `ISAAC GALLO → ISAAC GALLO` · `KATHERINE GUERRERO → KATHERINE GUERRERO` · `KAREN SOFIA → KAREN SOFIA` · `WENDY RAMOS → WENDY RAMOS` |
| `email` → `email` | de estos 5, los 5 vienen vacíos (`→ NULL`) — solo 2 de 531 clientes en todo legacy tienen email |
| `document_number`/`tower`/`apartment` | **0% de 531 tiene esto** — todas las Personas migradas quedan con `documento`/`tipo_documento`/`apartamento_actual_id` en `NULL` |
| `is_vip`/`total_spent`/`notes` | **sin destino en v2** — se descartan |

### 8.3 `Paquete` (de `packages`)

| Campo | 5 ejemplos reales (`legacy → v2`) |
|---|---|
| `tracking_number` → `access_code` **(⚠️ campo corregido, ver §2.3)** | `71WG → 71WG` · `ZJ1T → ZJ1T` · `G1J8 → G1J8` · `T9MB → T9MB` · `X1VR → X1VR` |
| `access_code` legacy (8 chars, ej. `2UGMRQIA`) | **sin destino** — nunca lo ve el cliente, se descarta |
| `guide_number` → `guide_number` | `PAPYRUS-SSAVA9 → PAPYRUS-SSAVA9` · `PAPYRUS-USW170 → PAPYRUS-USW170` · `PAPYRUS-QBROWK → PAPYRUS-QBROWK` · `PAPYRUS-4D64UR → PAPYRUS-4D64UR` · `PAPYRUS-8QTVR9 → PAPYRUS-8QTVR9` (tal cual) |
| `status` → `estado` | `ENTREGADO → ENTREGADO` (×3) · `RECIBIDO → RECIBIDO` (×2) — mismos valores |
| `customer.full_name`/`.phone` → `recipient_name`/`recipient_phone` **y** `announced_by_persona_id` | `YAZMIN CASTELLAR / +573157240960` · `YURANIS PERES / +573167996512` · `MARJOR BUITRAGO / +573002916095` · `ALEXÁNDER QUINTERO / +573186379282` · `KAREN VELASQUEZ / +573013949701` (mismo par en los dos roles v2, ver nota conceptual §2.3) |
| `announced_at`/`received_at`/`delivered_at` → mismos campos | ej. paquete `71WG`: `announced_at 2026-08-19 20:49:22 → 2026-08-19 20:49:22 UTC` · `received_at 2026-08-19 20:52:35 → ...` · `delivered_at (vacío, sigue RECIBIDO) → NULL` |
| `cancel_reason` (vía `package_history.observations`, no `package_events`) | los 8 paquetes `CANCELADO` reales: `1BAZ`, `QSQD`, `JSPH`, `EHFQ`, `HF5N` → los 5 tienen la MISMA observación textual: `"Cancelado por: otro."` → se mapea a `cancel_reason = "OTRO"` (sin el prefijo "Cancelado por:") |
| `created_by`/`updated_by` → `announced_by_usuario_id`/etc. | **100% NULL en las 2107 filas** — sin dato, ver hallazgo en §2.3 |

### 8.4 `PaqueteFoto` (de `file_uploads`)

| Campo | 5 ejemplos reales (`legacy → v2`, ilustrativo — la copia real aún no corrió) |
|---|---|
| `s3_key`/`s3_url` → `url` | `2026/08/19/packages/announcement_71WG/receive/71WG_20260819_155305_003.webp` (privado, `elclub-paqueteria`) → `https://<bucket-v2>.s3.<region>.amazonaws.com/paquetes-recibidos-imagenes/<uuid>_71WG_003.webp` (público, bucket de v2) — mismo patrón para las otras 4: `71WG_002.webp`, `71WG_001.webp`, `ZJ1T_003.webp`, `ZJ1T_002.webp` |
| `filename`/`file_size`/`content_type`/`file_type` | **sin destino** — `PaqueteFoto` solo guarda `url`, se pierde esta metadata estructurada (aunque el 100% es `IMAGEN`/`.webp` de todos modos) |

### 8.5 `PersonaPreferenciaNotificacion` (de `customer_preferences`, solo 7 filas existen)

Un ejemplo real completo (cliente `+573004948166`), mostrando la "explosión" de una fila legacy
en varias filas v2:

| legacy (una fila) | → | v2 (filas resultantes) |
|---|---|---|
| `sms_notifications_enabled=true`, `notify_package_announced=false` | → | `(persona, SMS, ANUNCIADO, activo=false)` |
| `sms_notifications_enabled=true`, `notify_package_received=true` | → | `(persona, SMS, RECIBIDO, activo=true)` |
| `sms_notifications_enabled=true`, `notify_package_delivered=true` | → | `(persona, SMS, ENTREGADO, activo=true)` |
| `email_notifications_enabled=true`, `notify_package_announced=false` | → | `(persona, EMAIL, ANUNCIADO, activo=false)` |
| `email_notifications_enabled=true`, `notify_package_received=true` | → | `(persona, EMAIL, RECIBIDO, activo=true)` |
| `notify_payment_due=true`, `marketing_enabled=false` | → | **sin destino** — v2 no tiene evento de cobro ni canal de marketing, se descartan sin crear fila |

Los otros 524 clientes (de 531) no tienen fila en `customer_preferences` — **no generan ninguna
fila v2 tampoco**, corren con el default de `preferencia_notificacion_service` (§2.5).

### 8.6 Archivo externo — `facturación` (de `package_events`, no entra al esquema de v2)

| Campo | 5 ejemplos reales |
|---|---|
| `base_fee`/`storage_fee`/`total_amount` | los 5 paquetes más recientes: `1500.00 / 0.00 / 1500.00` — **idéntico en los 5**, es la tarifa fija `NORMAL` del `.env` (`BASE_DELIVERY_RATE_NORMAL=1500`), no un cálculo caso a caso |
| `payment_received` | **`false` en las 876 filas que tienen `total_amount`** — nunca se marcó un pago como recibido en todo el sistema. El "cobro" es un número calculado que nunca se concilió contra un pago real |
| `payment_method`/`payment_amount` | vacíos en el 100% de la muestra — mismo patrón, campo diseñado pero nunca usado operativamente |

Esto cambia un poco el valor del archivo de "facturación": no es un histórico de cobros
reales, es un histórico de **tarifas calculadas que nunca se cobraron** — igual vale la pena
conservarlo como referencia, pero no es "cuánto pagó cada cliente".

### 8.7 Archivo externo — `messages` (2 filas, completas)

| Campo | Los 2 registros reales |
|---|---|
| `subject` | `PAQUETE MA8P` · `PAQUETE IHSQ` — ambos ligados a un paquete por el código en el asunto, NO por `package_id` (ese campo quedó `NULL` en los 2) |
| `sender_name`/`sender_phone` | `YEISON VANEGAS / +573225160912` · `DORIS SUAREZ / +573106520142` |
| `status` | `RESPONDIDO` en los 2 — ambas consultas de soporte ya fueron atendidas, no quedan pendientes |

### 8.8 Archivo externo — `notifications` (6514 filas, muestra)

| Campo | 5 ejemplos reales (los más recientes) |
|---|---|
| `notification_type`/`event_type`/`status` | `SMS / PACKAGE_DELIVERED / FAILED` (×4) · `SMS / PACKAGE_DELIVERED / FAILED` — la muestra más reciente son puros envíos fallidos, consistente con el 33% de fallo global visto en §1 (2144 de 6458 SMS) |
| `recipient` | teléfonos reales de clientes (`+573003682789`, `+573167996512`, etc.) — mismo dato que ya vive en `customers.phone`, no aporta identidad nueva |

---

**Resumen directo a tu pregunta ("qué necesito migrar exactamente"):** de las ~50 columnas
totales entre las 7 tablas en alcance, las que de verdad tienen dato real y mapeo en v2 son:
`users` (5 de sus 10 columnas), `customers` (3 de 22), `packages` (7 de 20, con 2 correcciones
de esta ronda), `file_uploads` (1 de 9, vía copia S3), `customer_preferences` (parcial, explota
a otra forma). El resto — o no tiene dato real en legacy (torre/apartamento, documento), o no
tiene destino en v2 (facturación, username, notas, VIP), o resultó ser un campo que nunca se
usó operativamente (`created_by`, `payment_received`).
