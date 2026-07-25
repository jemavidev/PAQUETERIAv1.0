# Spec — `/announce-new` (declarar unidad, staff)

Status: ready-for-agent
Feature: announce-new
Branch: PaqueteXv.2
Depende de: `data-model` (`declare_unit`, `get_or_create_apartamento` — ya existen y están probados), `staff-auth` (`current_staff`).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §6.4/§7 · `CONTEXT.md` (Herencia de apartamento, Apartamento) · ADR-0003

---

## Problem Statement

**Declarar una unidad a propósito** — el acto que, junto a `/customer/verify`, dispara la herencia de apartamento (§6.4) — hoy **solo puede hacerlo el cliente** desde su propio perfil, uno a la vez (`declare_unit` con un solo miembro). El brief exige que el **staff** también pueda hacerlo, y con **nombres ilimitados por apartamento** de una sola vez (§7) — p.ej. cuando llega un residente nuevo con toda su familia y el staff registra la unidad completa en un solo paso, sin que cada uno tenga que verificar su teléfono por separado primero.

Antes de escribir esta spec verifiqué algo importante: **`/announce` (anunciar un paquete) ya es una vista pública sin autenticación** — un operador en el mostrador puede usarla tal cual para anunciar en nombre de un residente. Por eso **esta rebanada no reimplementa el anuncio de paquetes** — sería una capacidad redundante. El hueco real es exclusivamente la **declaración de unidad en lote**, que hoy no existe en ninguna vista de staff.

## Solution

`/announce-new`: vista **de staff** (gated por `current_staff`, cualquier rol — es una tarea operativa rutinaria, no administrativa) donde el operador selecciona o crea un **Apartamento** (Conjunto/Torre/Apartamento) y declara **una lista de residentes** (nombre + teléfono, **ilimitados**) que pasan a compartir ese Apartamento como su actual — reutilizando `get_or_create_apartamento` + `declare_unit` **sin cambios de dominio**, exactamente como ya hace `/customer/verify` pero para **varios miembros a la vez** en lugar de uno.

## User Stories

1. Como **staff**, quiero abrir `/announce-new` y **crear o seleccionar un Apartamento** (Conjunto/Torre/Apartamento), para declarar la unidad de una familia/grupo.
2. Como **staff**, quiero agregar **nombres ilimitados** (cada uno con su teléfono) a esa unidad, para registrar a todos los residentes de una vez.
3. Como **staff**, quiero que declarar la unidad **una la a todos** los teléfonos listados a ese Apartamento **a la vez** (la herencia real, §6.4), no uno por uno.
4. Como **staff**, quiero que si el Apartamento **ya existía**, se **reutilice** (no se duplique) — consistente con el resto del sistema.
5. Como **staff**, quiero que si alguno de los teléfonos que agrego **ya es una Persona conocida**, se **reutilice** (no se duplique), y si es nueva, se **registre implícitamente** con el nombre que doy.
6. Como **staff**, quiero que declarar esta unidad **no afecte** a residentes de **otros** apartamentos ni reescriba el snapshot de paquetes ya anunciados (invariantes ya garantizados por `declare_unit`, verificados aquí en el contexto de esta vista).
7. Como **staff**, quiero un **mínimo de un teléfono** por envío (no declarar una unidad vacía), y que cada fila exija **teléfono y nombre** — un teléfono sin nombre, o viceversa, se rechaza con mensaje claro.
8. Como **staff**, quiero ver una **confirmación** con los residentes que quedaron unidos a la unidad, para verificar que el registro fue correcto.
9. Como **staff (cualquier rol)**, quiero acceder a `/announce-new` sin necesitar privilegios de administrador, porque es una tarea operativa rutinaria (a diferencia de `/admin/staff`).
10. Como **staff sin sesión**, quiero ser **redirigido a `/auth/login`**, para que esta vista no quede expuesta.
11. Como **desarrollador**, quiero que esta vista **no invente dominio nuevo** — reutiliza `get_or_create_apartamento`/`declare_unit` tal cual, mismo patrón que `/customer/verify`.

## Implementation Decisions

### Ruta (capa web — gated por `current_staff`, cualquier rol)

- **`GET /announce-new`**: formulario con campos de Apartamento (Conjunto/Torre/Apartamento) + una lista **dinámica** de filas nombre+teléfono (agregar/quitar filas en el cliente, patrón JS simple sin dependencias, consistente con el resto de la capa web).
- **`POST /announce-new`**: valida que venga **al menos un miembro** (nombre+teléfono, ambos presentes por fila) y los tres campos del Apartamento; llama `get_or_create_apartamento(...)` + `declare_unit(apartamento, miembros)`; éxito → **confirmación** listando los residentes unidos a la unidad (PRG).
- **Validación**: Apartamento incompleto (falta algún campo de los 3), o cero miembros, o una fila con nombre sin teléfono (o viceversa) → error claro, **nada se persiste** (mismo patrón "todo o nada" de `/customer/verify`: se valida **antes** de llamar a dominio).
- **Sin cambios en dominio.** `get_or_create_apartamento`/`declare_unit` se reutilizan exactamente como están.

### Decisión que resuelve una tensión del brief (documentada explícitamente)

- El brief dice "nombres ilimitados por apartamento, **con o sin teléfono**". Pero `declare_unit` (y el invariante ADR-0003 — el Teléfono es la llave universal de la Persona) **exige** teléfono para que alguien se una al grupo como Persona real. **Decisión:** en esta pantalla, **todo miembro de la unidad declarada debe tener teléfono** — un "nombre sin teléfono" **no** tiene existencia propia fuera del snapshot de un Paquete (`CONTEXT.md`) y por tanto **no puede** ser miembro de una unidad declarada aquí. Esa clase de nombre solo aparece más tarde como Destinatario de un anuncio puntual (`/announce`, `Destinatario.solo_nombre`), no como residente registrado de la unidad.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento observable por HTTP** — que la vista exige sesión de staff (cualquier rol, a diferencia de `/admin/staff`); que declarar una unidad con varios miembros los une **a todos** a la vez; que reutiliza Apartamento/Persona existentes sin duplicar; que la validación "todo o nada" no persiste nada a medias — **no** re-testea los invariantes de `declare_unit`/`get_or_create_apartamento` en sí (ya cubiertos en `tests/data_model/test_declarar_unidad.py`).

**Costura (EXISTENTE, ninguna nueva):** **HTTP con `TestClient`**, sesión de staff vía `create_initial_admin`/`create_staff` + `/auth/login` (patrón de `test_packages.py`). Casos: sin sesión → redirige; sesión de **OPERADOR** (no solo ADMIN) → 200 (a diferencia de `/admin/staff`); `POST` con 3 miembros nuevos → los 3 quedan con el mismo `apartamento_actual`; Apartamento ya existente → se reutiliza (conteo de Apartamentos no crece); un teléfono ya conocido → se reutiliza esa Persona (conteo de Personas no crece para ese teléfono); fila con nombre sin teléfono → error, nada se persiste; Apartamento incompleto → error, nada se persiste; cero miembros → error.

**Prior art:** `tests/data_model/test_declarar_unidad.py` (los invariantes de dominio, no se re-testean), `tests/web/test_customer_verify.py` (patrón de "todo o nada" + reutilización de Apartamento/Persona), `tests/web/test_packages.py` (sesión de staff). Construir **test-first** con `/tdd`.

## Out of Scope

- **Anunciar un paquete desde esta vista** — `/announce` (público, sin auth) ya cubre esa capacidad; el staff puede usarla directamente en el mostrador. Confirmado explícitamente antes de escribir esta spec para no duplicar.
- **Editar/eliminar una unidad ya declarada** — corrección de herencia errónea ya existe vía `move_resident` (dominio); una UI dedicada para eso es una extensión futura, no esta rebanada.
- **Nombres sin teléfono como miembros de la unidad** — decisión explícita arriba: no son miembros de la unidad, solo existen como snapshot de un Paquete puntual.
- **Restricción a solo ADMIN** — deliberadamente **no**: cualquier staff (`current_staff`) puede declarar unidades, es tarea operativa rutinaria.

## Further Notes

- **Por qué no reimplementar el anuncio de paquete aquí:** verificado que `/announce` es público y sin gate — el staff ya lo usa tal cual desde el mostrador. Construir un segundo formulario de anuncio "para staff" sería trabajo redundante sin capacidad nueva real (contraste con `admin-staff`, donde sí había una brecha genuina).
- **Tensión resuelta del brief** ("con o sin teléfono"): documentada arriba como decisión explícita, coherente con ADR-0003 y el glosario de `CONTEXT.md` — no una improvisación silenciosa.
- **Consumo aguas abajo:** ninguna otra rebanada depende de ésta; es un consumidor más de `declare_unit`, igual que `/customer/verify`.
