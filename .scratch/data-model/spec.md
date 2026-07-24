# Spec — Modelo de datos: Persona / Apartamento / Paquete-snapshot + árbol Alembic limpio

Status: ready-for-agent
Feature: data-model
Branch: PaqueteXv.2
Fuente de verdad: `CODE/docs/refactoring/SYSTEM_REBUILD_BRIEF.md` §6/§14 · `CONTEXT.md` (glosario) · `CODE/docs/refactoring/DATABASE_CONSTRAINTS.md` (fuente de migración, no de herencia)

---

## Problem Statement

El modelo de datos actual no puede representar el dominio real del conjunto residencial:

- **Cliente = Teléfono único e inmutable.** La tabla `customers` fuerza `phone unique`, así que una persona *es* su teléfono. No hay forma de que una identidad estable amplíe sus datos ni de separar "quién anuncia" de "a nombre de quién llega".
- **`display_name` huérfano.** El Paquete guarda un `display_name` de texto libre suelto, sin identidad detrás. Un nombre escrito ahí no pertenece a nadie: no tiene teléfono, ni apartamento, ni historia.
- **Apartamento = 3 columnas sueltas.** `building_name` / `tower` / `apartment` viven como texto sobre `customers`. No son una entidad: no se pueden compartir entre convivientes, ni corregir en un solo lugar, ni congelar en el tiempo.
- **El Paquete cuelga de un solo `customer_id`.** No distingue Anunciante de Destinatario, y si el cliente cambia de apartamento, los paquetes viejos "se mudan con él": la historia se reescribe sola.
- **El árbol Alembic está roto.** 38 migraciones con **3 raíces desconectadas** (`down_revision = None`), estados que no coinciden entre RDS / contenedor prod / repo, y cicatrices manuales (`fix_migration_conflict.py`, `INSTRUCCIONES_MIGRACION.md`, `INSTRUCCIONES_FIX_MIGRACION.md`). `alembic upgrade head` no reconstruye el estado real.

Desde la perspectiva del staff y del residente, esto se traduce en: nombres que no llevan a ningún lado, apartamentos que se corrigen cliente por cliente, y un paquete de hace tres meses que de repente muestra la torre nueva a la que se mudó el residente.

## Solution

Un modelo nuevo, construido desde cero, con el **Teléfono como llave universal de la Persona** y el **Paquete como snapshot inmutable** de su contexto de entrega:

- **Persona** — identidad estable anclada en un Teléfono que siempre existe. Tiene nombre, un Apartamento *actual* opcional y mutable, y datos ampliables. Se crea implícitamente al anunciar.
- **Apartamento** — entidad ligera (Conjunto → Torre → Apartamento), creable sobre la marcha, opcional, que agrupa Teléfonos. La membresía es mutable: mudarse o desvincularse siempre está disponible.
- **Paquete** — al anunciarse **congela** una foto inmutable de `{anunciado_por (teléfono), nombre_destinatario, teléfono_destinatario (si hay), apartamento}`. Mudarse después nunca reescribe paquetes viejos.
- **Usuario (staff)** — entidad separada, con rol, para que cada acción sobre un paquete pueda registrar quién la hizo.
- **Árbol Alembic limpio** — una **sola raíz**, una migración baseline que construye el modelo nuevo, sin cicatrices. Las rebanadas posteriores descienden de esa raíz sin volver a fragmentar el grafo.

Todo se ejercita a través de un **servicio de aplicación de dominio** (registro / membresía) probado contra un Postgres efímero real construido con `alembic upgrade head`.

## User Stories

1. Como **staff**, quiero que al anunciar un paquete con teléfono + nombre se cree automáticamente una **Persona** si no existía, para no tener que registrar clientes por separado.
2. Como **staff**, quiero que si vuelvo a anunciar con un teléfono ya conocido se reutilice la **misma Persona**, para no generar duplicados de identidad.
3. Como **staff**, quiero que dos escrituras del mismo número con formato distinto (con/sin espacios, con/sin indicativo) se resuelvan a **una sola Persona**, para que el Teléfono funcione de verdad como llave estable.
4. Como **residente**, quiero que mi **Teléfono** sea mi identidad a lo largo de todo el sistema, para que mis paquetes y mis datos siempre me pertenezcan aunque cambie de apartamento.
5. Como **residente**, quiero **ampliar mis datos** (email, documento, segundo contacto) sobre mi Persona existente, para completar mi registro sin crear una identidad nueva.
6. Como **staff**, quiero anunciar un paquete **a nombre de otra persona registrada** (con su teléfono), para que el Destinatario sea esa Persona y no yo.
7. Como **staff**, quiero anunciar un paquete a nombre de **solo un nombre sin teléfono**, para que ese nombre quede **bajo el teléfono de quien anuncia** y nunca falte una identidad.
8. Como **residente que anuncia**, quiero que cuando doy un **nombre sin teléfono** como Destinatario, el sistema no invente una Persona sin llave, para respetar que no hay personas sin teléfono.
9. Como **staff**, quiero que cada Paquete guarde **dos referencias independientes** — Anunciante y Destinatario —, para saber quién avisó y a nombre de quién llega, aunque coincidan o no.
10. Como **staff**, quiero crear un **Apartamento** sobre la marcha con solo Conjunto/Torre/Apartamento, para no frenar la operación por catálogos previos.
11. Como **staff**, quiero que si escribo un Apartamento que ya existe (mismo Conjunto/Torre/Apto) el sistema **reutilice** el existente, para no duplicar unidades.
12. Como **staff**, quiero poder anunciar aunque **no haya Apartamento** (opcional), para no bloquear el flujo cuando falta el dato.
13. Como **residente**, quiero tener **un** Apartamento *actual* a la vez, para reflejar dónde vivo hoy sin ambigüedad.
14. Como **residente**, quiero poder **mudarme** a otro Apartamento cuando cambie de casa, para que mis paquetes futuros salgan a la unidad correcta.
15. Como **residente**, quiero poder **desvincularme** de todo Apartamento, para representar que ya no vivo en el conjunto sin perder mi identidad.
16. Como **staff**, quiero **declarar una unidad a propósito** (`/announce-new` o el cliente en `/customer/verify`) asignando un Apartamento a varios Teléfonos de una vez, para agrupar convivientes deliberadamente.
17. Como **staff**, quiero que al declarar la unidad los demás Teléfonos del grupo **hereden** el Apartamento automáticamente, para no teclear la misma dirección uno por uno.
18. Como **staff**, quiero que un **"a nombre de" casual** en `/announce` **no** agrupe apartamentos, para que un favor puntual entre torres distintas no contamine la unidad de nadie.
19. Como **staff**, quiero poder **corregir** una herencia errónea moviendo o desvinculando cualquier Teléfono afectado, para que ningún agrupamiento sea irreversible.
20. Como **staff**, quiero que al **anunciar** el Paquete **congele** el contexto de entrega `{anunciado_por, nombre_destinatario, teléfono_destinatario?, apartamento}`, para que ese paquete conserve sus datos de principio a fin.
21. Como **residente que se mudó**, quiero que mis **paquetes viejos sigan mostrando el apartamento de entonces**, para que la historia no se reescriba con mi dirección nueva.
22. Como **staff**, quiero que mudar a una Persona **no altere ningún snapshot** de paquetes ya anunciados, para confiar en que lo entregado es trazable a como estaba en su momento.
23. Como **staff**, quiero que el Paquete tenga un **Estado** del ciclo de vida (`Anunciado` / `Recibido` / `Entregado` / `Cancelado`), para saber en qué punto está.
24. Como **staff**, quiero que el esquema soporte registrar **quién** y **cuándo** en cada transición (actor tomado de la sesión, nunca hardcodeado), para tener trazabilidad de las acciones.
25. Como **staff**, quiero que `guide_number` sea **opcional** en el Paquete, porque no todos los transportadores la usan y no se captura al anunciar.
26. Como **arquitecto**, quiero que el emparejamiento anuncio↔paquete siga siendo **por nombre/teléfono** del Destinatario y que el esquema deje espacio para **promover la guía a llave a futuro**, para no cerrarme esa puerta.
27. Como **administrador**, quiero que el **staff (Usuario)** sea una entidad separada de la Persona, con rol `ADMIN` / `OPERADOR`, para que la identidad y los privilegios del staff no se mezclen con los residentes.
28. Como **DevOps**, quiero un **árbol Alembic de una sola raíz**, para que `alembic upgrade head` sobre un Postgres vacío construya el esquema completo sin sorpresas.
29. Como **DevOps**, quiero que `upgrade head` → `downgrade base` **haga round-trip limpio**, para poder confiar en las migraciones dentro de CI.
30. Como **DevOps**, quiero que desaparezcan las **cicatrices de migración** (`fix_migration_conflict.py`, `INSTRUCCIONES_*MIGRACION*.md`), para no arrastrar arreglos manuales del sistema viejo.
31. Como **tester**, quiero probar los invariantes del dominio a través de **un solo servicio de aplicación** contra un Postgres real efímero, para cubrir el comportamiento sin acoplarme a nombres de columna.
32. Como **arquitecto**, quiero que las rebanadas siguientes (eventos, notificaciones, credenciales de auth, fotos de paquete) **desciendan de esta raíz** sin volver a fragmentar el grafo, para mantener el árbol sano.
33. Como **owner**, quiero que el modelo nuevo **no cree tablas** para subsistemas fuera de alcance (facturas / productos / CUFE), para que el rebuild quede liviano.

## Implementation Decisions

### Entidades del modelo nuevo (esta rebanada crea la baseline)

- **Persona** — surrogate key propia; `telefono` en forma **canónica normalizada** con **restricción única** y NOT NULL (es la llave universal); `nombre`; `apartamento_actual_id` (FK nullable, mutable); campos ampliables nullable (`email`, `documento`/tipo, segundo contacto); timestamps. Es el **ancla de identidad del cliente**; las credenciales de cliente (OTP) las posee la rebanada de auth, no esta.
- **Apartamento** — surrogate key; columnas `conjunto`, `torre`, `apartamento` (la jerarquía como columnas de una **sola tabla ligera**, no tres tablas); **restricción única** sobre la terna normalizada `(conjunto, torre, apartamento)`; timestamps. Semántica **get-or-create** por esa terna ("creable sobre la marcha" + dedup).
- **Paquete** — surrogate key + llave(s) de negocio existentes (`tracking_number`/`access_code`); **campos-snapshot congelados al anunciar**: `announced_by_phone`, `recipient_name`, `recipient_phone` (nullable) y el **snapshot de apartamento** como columnas denormalizadas (`snapshot_conjunto` / `snapshot_torre` / `snapshot_apartamento`) — **valores copiados, nunca FK** (un FK seguiría a la Persona al mudarse y reescribiría la historia). `estado` (enum del ciclo de vida); `guide_number` nullable; timestamps de transición (`announced_at`/`received_at`/`delivered_at`/`cancelled_at`) y FK-de-actor nullable por transición hacia `Usuario`.
- **Usuario (staff)** — entidad separada, `rol` enum `ADMIN`/`OPERADOR`. Esta rebanada define **el esqueleto mínimo** que necesitan las FK de actor; las columnas de credencial (password fuerte) las posee la rebanada de auth.

### Referencia del Anunciante vs snapshot del Destinatario

- El **Anunciante** siempre es una Persona real (siempre tiene Teléfono, y el Teléfono de una Persona es estable). Por eso el Paquete referencia al Anunciante por **FK a Persona** *y además* congela `announced_by_phone` como parte del snapshot — ambos coinciden por construcción.
- El **Destinatario** puede ser un **nombre sin teléfono**, así que **no** se modela por FK: se congela como `recipient_name` (+ `recipient_phone` nullable) bajo el Teléfono del Anunciante. Un Destinatario que sí es una Persona registrada se resuelve en el momento del anuncio, pero lo que queda en el paquete es el snapshot, no una referencia viva.
- El **snapshot de apartamento** es el Apartamento resuelto para la entrega en el instante del anuncio (el `apartamento_actual` de la Persona destinataria, o el del Anunciante si el Destinatario es un nombre sin teléfono), **copiado como texto** y nunca mutado después.

### "Grupo misma unidad" y herencia

- **No** hay entidad "grupo" persistente. El grupo *es* el conjunto de Personas que comparten el mismo `apartamento_actual`.
- **Declarar la unidad** es el *acto* (`declare_unit(apartamento, [teléfonos/nombres])`) que asigna `apartamento_actual = apartamento` a todos los Teléfonos declarados a la vez — eso **es** la herencia. Un "a nombre de" casual en `announce` **no** toca `apartamento_actual` de nadie más que del contexto del propio paquete.
- **Corregibilidad** = `move_resident(teléfono, apartamento|None)` disponible siempre; ninguna herencia es irreversible.

### Servicio de aplicación de dominio (la costura de test — Seam A)

Un único módulo de servicio de **registro / membresía** concentra las operaciones que materializan los invariantes. Interfaz de comportamiento (nombres ilustrativos, no rutas):

- `announce(anunciante_telefono, anunciante_nombre, destinatario, apartamento?) -> Paquete` — crea/reutiliza Persona por teléfono normalizado, resuelve Destinatario (Persona registrada | nombre sin teléfono bajo el teléfono del Anunciante), **congela el snapshot**, deja el Paquete en `Anunciado`.
- `declare_unit(apartamento, [teléfonos/nombres])` — get-or-create del Apartamento; asigna `apartamento_actual` a los Teléfonos declarados (herencia).
- `move_resident(telefono, apartamento|None)` — muda o desvincula; **no toca ningún snapshot** existente.

La lógica de la **máquina de estados** (transiciones permitidas y quién puede cada una) **no** vive aquí — esta rebanada solo define el enum `estado` y las columnas de transición.

### Normalización y llaves

- **Teléfono**: normalización canónica (indicativo país por defecto Colombia, strip de espacios/guiones/paréntesis) aplicada **antes** de persistir; la unicidad y el emparejamiento operan sobre la forma canónica.
- **Apartamento**: normalización de casing/espacios en la terna antes del dedup único.
- **Surrogate keys**: se estandarizan **UUID** en las tablas núcleo nuevas (Persona/Apartamento/Paquete/Usuario) por portabilidad del D/R basado en dump/restore (sin coordinación de secuencias). Las llaves de negocio legibles del Paquete (`tracking_number`, `access_code`) se conservan como columnas únicas aparte.

### Árbol Alembic limpio (esta rebanada)

- Una **migración baseline única** con `down_revision = None` **exactamente una vez**, que crea Persona / Apartamento / Paquete / Usuario y sus constraints.
- El directorio de versiones viejo (38 migraciones, 3 raíces) se **retira**; el esquema nuevo **no** se deriva de él. Las 28 tablas de RDS siguen siendo la **fuente de la migración de datos** (rebanada aparte, §11 del brief), no el esquema a heredar.
- Se **eliminan** las cicatrices: `fix_migration_conflict.py`, `INSTRUCCIONES_MIGRACION.md`, `INSTRUCCIONES_FIX_MIGRACION.md`.
- Subsistemas fuera de alcance (facturas / productos / CUFE) **no reciben tablas** en el esquema nuevo. Rebanadas posteriores (eventos de paquete, notificaciones, credenciales de auth, fotos) añaden migraciones **descendientes de esta raíz** — el árbol permanece de raíz única.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento externo observable** a través de la costura de servicio (los invariantes del dominio), no detalles de implementación (nombres de columna, internals de SQLAlchemy). Las constraints de BD que sí son comportamiento observable (unicidad del teléfono, dedup del apartamento) se prueban por su **efecto** (dos anuncios → una Persona), no inspeccionando el DDL.

**Seam A — Servicio de dominio (registro/membresía), contra Postgres efímero real construido con `alembic upgrade head`.** El test-DB se levanta corriendo las migraciones (no `create_all`), de modo que los tests de comportamiento **ejercitan las migraciones de paso**. Casos:

- Anunciar con teléfono nuevo crea Persona; re-anunciar con el mismo teléfono la **reutiliza** (sin duplicado).
- Dos formatos del mismo número → **una** Persona (normalización).
- Anunciar a un **nombre sin teléfono** → snapshot con `recipient_name` bajo el teléfono del Anunciante y `recipient_phone` nulo; **no** se crea Persona sin llave.
- Anunciar **congela** el snapshot; un `move_resident` posterior **no** cambia el snapshot de apartamento del paquete viejo.
- `declare_unit` asigna `apartamento_actual` a todos los Teléfonos declarados (herencia); un "a nombre de" casual en `announce` **no** agrupa apartamentos.
- `move_resident` cambia `apartamento_actual`; desvincular lo pone nulo; ninguno reescribe paquetes viejos.
- Apartamento: mismo `(conjunto,torre,apto)` → **get-or-create** reutiliza el existente.

**Seam B — Grafo de migración (aserción delgada):** un solo `head`; `upgrade head` → `downgrade base` **round-trip** limpio sobre Postgres vacío.

**Herramientas y prior art:** `pytest` + un servicio **Postgres real efímero en CI** (contenedor en GitHub Actions), según la recomendación del brief §12. `httpx`/`TestClient` de FastAPI queda para las rebanadas de rutas (`/announce`, `/customer/verify`), no para esta. **No hay prior art útil**: los 63 tests existentes son de CUFE/facturas/productos/parser (fuera de alcance) y el modelo de cliente/ciclo de vida **no tiene cobertura** — esta rebanada **establece** el patrón de test de integración del dominio núcleo. Construir **test-first** con `/tdd`.

## Out of Scope

- **Rutas HTTP** (`/announce`, `/customer/verify`, `/announce-new`, `/packages`, `/search`, `/admin`, …) — rebanadas posteriores; aquí solo la capa de servicio de dominio.
- **Lógica de la máquina de estados** del Paquete (transiciones permitidas y quién puede cada una) — solo se define el enum `estado` + columnas de transición.
- **Log de eventos** (`package_events` / `package_history`), **notificaciones** (SMS/WhatsApp) y su integración al modelo de eventos.
- **Autenticación** — OTP de clientes y contraseña de staff; aquí solo el esqueleto de la tabla `Usuario` y el ancla de identidad de cliente en Persona.
- **Migración de datos** desde las 28 tablas de RDS (§11) — rebanada aparte; esta define el **esquema destino**, no importa datos.
- **Roster persistente de "nombres sin teléfono" por Apartamento** en `/announce-new` — se **difiere** (ver Further Notes, cabo 1). Esta rebanada representa el nombre sin teléfono **solo** en el snapshot del Paquete.
- **Escáner de códigos de barra** y captura de `guide_number` en el modal Recibir.
- **Facturas / Productos / CUFE** — fuera de todo el rebuild.
- **Fotos de paquete** (`file_uploads` acotado) — rebanada de fotos, desciende de esta raíz.

## Further Notes

**Cabos de diseño resueltos en esta spec** (los 6 identificados al analizar §6):

1. **"Nombre sin teléfono" ¿se persiste o vive solo en el snapshot?** — Decisión: en esta rebanada vive **solo en el snapshot del Paquete** (respeta "no hay personas sin llave"). El roster persistente de nombres-sin-teléfono por Apartamento que sugiere `/announce-new` se **difiere**; si el owner lo quiere persistente, requeriría un constructo `Ocupante(apartamento_id, nombre)` — decisión de la rebanada `/announce-new`, no se construye ahora.
2. **Modelado del "grupo misma unidad"** — Decisión: **sin entidad de grupo**; el grupo = Personas con el mismo `apartamento_actual`; `declare_unit` es el acto que asigna la membresía (= herencia).
3. **Forma del `apartment_snapshot`** — Decisión: **columnas de texto denormalizadas copiadas** (queryables para `/search`), nunca FK.
4. **Normalización del Teléfono** — Decisión: forma canónica antes de persistir; unicidad/emparejamiento sobre la canónica.
5. **Dedup del Apartamento** — Decisión: único sobre la terna normalizada; get-or-create.
6. **Historial de membresía de Apartamento** — Decisión: **sin tabla de historial** en esta rebanada (liviano; el invariante lo cubre el snapshot del Paquete). Documentado como upgrade futuro si algún día se necesita la historia completa de mudanzas de una Persona.

**ADRs:** no existe aún `docs/adr/` — ninguna contradicción con decisiones previas. Estas cinco decisiones estructurales (Teléfono-llave, snapshot inmutable, Apartamento agrupador mutable, herencia por declaración, staff separado) son candidatas naturales a los **primeros ADRs** del repo vía `/domain-modeling`.

**Relación con el código viejo:** `models/customer.py`, `models/package.py`, `models/announcement_new.py` son la cara **"desde"** de la migración de datos (§11), **no** se extienden. El `guide_number unique NOT NULL` de `package_announcements_new` es un bug a **no heredar** (el anuncio no captura guía).

**Consumo aguas abajo:** esta spec alimenta `/to-tickets`. Todo lo demás del rebuild (announce, search, customers, packages, notificaciones) **cuelga** de este modelo.
