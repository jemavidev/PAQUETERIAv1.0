# Spec — `/search` (consultar estado de un paquete)

Status: ready-for-agent
Feature: search-web
Branch: PaqueteXv.2
Depende de: `data-model` (Paquete + snapshot), `package-lifecycle` (estados + timestamps de transición), `announce-web` (capa web). Vista **pública** (sin privilegios).
Fuente de verdad: `SYSTEM_REBUILD_BRIEF.md` §7 · `CONTEXT.md` (Estados del Paquete, Teléfono, Anunciante/Destinatario) · ADR-0004

---

## Problem Statement

Un residente anuncia un paquete y luego **no tiene cómo saber en qué va**. El flujo del staff ya mueve el paquete por sus estados (`Anunciado → Recibido → Entregado`/`Cancelado`), pero el cliente no puede consultarlo: no existe `/search` en el rebuild. Cierra el journey del cliente a medias — puede anunciar, pero no **seguir**. Además el sistema viejo mezclaba en esa vista una **mensajería cliente↔staff** que se elimina.

## Solution

`/search`: una vista **pública** (sin login) donde el residente busca su paquete por su **número de seguimiento** o por su **teléfono**, y ve su **estado actual** y una **línea de tiempo legible** de por dónde ha pasado:

- Por **número de seguimiento** (el que recibió al anunciar) → ve **ese** paquete con su timeline.
- Por **teléfono** → ve la **lista** de sus paquetes (los que anunció o que llegan a su nombre), cada uno con su estado.
- El **timeline** muestra los hitos con su fecha/hora: **Anunciado → Recibido → Entregado**, o **Cancelado** (con su motivo) — legible, no una tabla técnica.
- **Sin mensajería** cliente↔staff (se elimina, brief §7).

Mobile-first, server-rendered, sin auth (el residente consulta con lo que ya tiene: su tracking o su teléfono).

## User Stories

1. Como **residente**, quiero abrir `/search` y ver un buscador simple, para consultar mi paquete sin registrarme.
2. Como **residente**, quiero buscar por mi **número de seguimiento**, para ver directamente ese paquete.
3. Como **residente**, quiero buscar por mi **teléfono**, para ver todos mis paquetes cuando no tengo el número a mano.
4. Como **residente**, quiero ver el **estado actual** del paquete (Anunciado / Recibido / Entregado / Cancelado) de un vistazo, para saber si ya puedo pasar a recogerlo.
5. Como **residente**, quiero una **línea de tiempo** de los hitos con su fecha/hora, para entender por dónde ha pasado sin jerga técnica.
6. Como **residente**, quiero ver, si fue **cancelado**, que lo fue y con qué **motivo**, para saber por qué no llegará.
7. Como **residente que buscó por teléfono**, quiero ver la **lista de mis paquetes** con su estado, para ubicar el que me interesa.
8. Como **residente**, quiero que si **no hay resultados** se me diga con claridad (y sin errores), para reintentar con otro dato.
9. Como **residente**, quiero que mi **teléfono se normalice** al buscar (cualquier formato encuentra lo mismo), consistente con cómo se guardó.
10. Como **residente**, quiero ver a **nombre de quién** llega el paquete (el destinatario snapshot) y su **apartamento** de entonces, para confirmar que es el mío.
11. Como **residente en móvil**, quiero una vista de una sola columna con texto grande, para leerla con el pulgar.
12. Como **residente**, quiero que la consulta **no exija login**, porque es una vista pública de seguimiento.
13. Como **staff**, quiero que la vieja **mensajería cliente↔staff desaparezca** de esta pantalla, para no reintroducir ese subsistema.
14. Como **residente**, quiero que la búsqueda **no revele datos sensibles de otros** más allá de lo que ya implica conocer el tracking/teléfono, para una privacidad razonable.

## Implementation Decisions

### Rutas (capa web, **públicas**)

- **`GET /search`**: formulario con **un campo** ("número de seguimiento o teléfono") + resultados. Sin login.
- Resolución de la consulta (una acción de búsqueda, `GET` con query o `POST`):
  - Si el término coincide con un **`tracking_number`** exacto → muestra **ese** Paquete con su **timeline**.
  - Si no, se interpreta como **teléfono**: se **normaliza** (misma regla canónica del dominio) y se listan los Paquetes cuyo **`announced_by_phone`** o **`recipient_phone`** coincide, cada uno con su estado (enlazando a su timeline por tracking).
  - Si nada coincide → mensaje claro de "sin resultados".
- Read-only: ninguna mutación.

### La línea de tiempo (desde las columnas de transición, sin event-log)

- El timeline se arma con los campos que el Paquete ya tiene: `announced_at`, `received_at`, `delivered_at`, `cancelled_at` (+ `cancel_reason`). No requiere una tabla de eventos aparte (fuera de alcance).
- Se muestran solo los hitos **ocurridos** (timestamps no nulos), en orden, con fecha/hora legible; el **estado actual** se resalta. Si `Cancelado`, se muestra el **motivo**.
- **Privacidad:** el timeline del cliente **no** expone al operador (`*_by_usuario`) — el actor es para auditoría interna, no para el residente.

### Lectura / consulta

- Un **read** para la búsqueda (consulta directa o un pequeño helper): por `tracking_number` exacto, y por teléfono canónico contra `announced_by_phone`/`recipient_phone`. Devuelve lo necesario para pintar el resultado (estado, destinatario snapshot, apartamento snapshot, timestamps, motivo).
- Se muestra el **destinatario snapshot** (`recipient_name` + apartamento snapshot) del paquete, no el estado actual de ninguna Persona (coherente con ADR-0001).

### UI

- Server-rendered, mobile-first (patrón de `/announce`): un buscador, y abajo el resultado (un paquete con timeline, o la lista por teléfono). **Sin** ningún resto de mensajería.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento observable por HTTP** — que buscar por tracking devuelve el paquete y su estado; que buscar por teléfono lista los paquetes de esa persona; que el timeline refleja los hitos ocurridos; que "sin resultados" se maneja sin error — no el HTML exacto ni los internals.

**Costura (EXISTENTE, ninguna nueva):** **HTTP con `TestClient`** (arnés `tests/web`), **sin** autenticar (vista pública). Se siembran paquetes vía el servicio de dominio (`announce` + transiciones de `package-lifecycle`) para montar los estados. Casos:
- `GET /search` → 200 con el buscador.
- Buscar por **tracking** de un paquete `Anunciado` → muestra el paquete y su estado; el timeline tiene el hito Anunciado.
- Tras `receive`/`deliver`, el timeline del paquete muestra los hitos Recibido/Entregado con sus marcas.
- Un paquete `Cancelado` muestra el estado y el **motivo**.
- Buscar por **teléfono** (en varios formatos) → lista los paquetes de esa persona (como anunciante y como destinatario), normalizando el teléfono.
- Término sin coincidencias → "sin resultados", 200, sin error.
- La vista **no** requiere sesión (a diferencia de `/packages`).

**Prior art:** `tests/web/test_announce.py` (rutas públicas + `client.db`), `tests/data_model/test_*` (para sembrar estados con el dominio). Construir **test-first** con `/tdd`.

## Out of Scope

- **Mensajería cliente↔staff** — se elimina; no se reintroduce.
- **Autenticación / OTP de clientes** — `/search` es pública; el OTP de clientes es otra rebanada.
- **Log de eventos rico** (`package_events`/`package_history` con quién/notas) — el timeline se arma de los timestamps del Paquete; un event-log detallado es mejora posterior.
- **Notificaciones** (avisar al cliente por SMS/WhatsApp) — rebanada aparte.
- **`/customer/verify`** (autoedición de datos del cliente) — otra rebanada (requiere OTP).
- **Paginación / filtros** de la lista por teléfono — mejora posterior (volumen bajo).

## Further Notes

- **Privacidad (decisión abierta, elijo default):** buscar por teléfono lista los paquetes de ese número — cualquiera que conozca el teléfono los ve. Es el comportamiento del sistema viejo y lo que el residente espera; lo mantengo **público**, pero anoto que una mejora futura podría **exigir OTP** para el listado por teléfono (dejando el tracking como consulta pública sin fricción). El timeline **no** expone al operador.
- **Timeline sin event-log:** suficiente para el cliente con los 4 timestamps + motivo; si se necesita "quién/notas" por hito, entra la rebanada de event-log.
- **Consumo aguas abajo:** el patrón de búsqueda pública y el render de timeline los reutilizará cualquier vista de detalle de paquete.
