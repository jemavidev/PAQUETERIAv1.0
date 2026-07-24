# Spec — Máquina de estados del Paquete (recibir · entregar · cancelar)

Status: ready-for-agent
Feature: package-lifecycle
Branch: PaqueteXv.2
Depende de: rebanada `data-model` (Persona/Apartamento/Paquete-snapshot), ya en `main`-de-rebuild (commits ac78245…6082b97)
Fuente de verdad: `CODE/docs/refactoring/SYSTEM_REBUILD_BRIEF.md` §6/§7/§14/§15.4 · `CONTEXT.md` (Estados del Paquete) · `CODE/docs/refactoring/PACKAGES_DIAGNOSIS.md`

---

## Problem Statement

El data-model dejó el Paquete con un campo `estado` (`ANUNCIADO`/`RECIBIDO`/`ENTREGADO`/`CANCELADO`), columnas de transición (`received_at`/`received_by_usuario`, `delivered_*`, `cancelled_*`) y `guide_number` — todo **sin lógica que las gobierne**. Hoy el Paquete solo sabe nacer (`announce` → `ANUNCIADO`); no hay forma de **recibirlo, entregarlo ni cancelarlo**, ni reglas que impidan transiciones absurdas (entregar algo que nunca se recibió, recibir algo ya entregado, cancelar algo ya entregado).

Desde la perspectiva del staff: un paquete llega a la portería y no hay cómo marcarlo recibido; un residente lo retira y no hay cómo marcarlo entregado; un anuncio erróneo no se puede anular con trazabilidad. Y el sistema viejo arrastraba modales que se quedaban bloqueados y acciones sin registrar **quién** las hizo (ver `PACKAGES_DIAGNOSIS.md`).

## Solution

Una **máquina de estados** en la capa de dominio que gobierna el ciclo de vida del Paquete con tres transiciones, cada una registrando **quién** (el `Usuario` de la sesión real, nunca hardcodeado) y **cuándo**:

- **Recibir** (`ANUNCIADO → RECIBIDO`): el staff recibe el paquete físico; opcionalmente captura la **Guía** del transportador (escaneada); registra `received_at` + `received_by_usuario`.
- **Entregar** (`RECIBIDO → ENTREGADO`): el staff entrega al residente; registra `delivered_at` + `delivered_by_usuario`.
- **Cancelar** (`ANUNCIADO | RECIBIDO → CANCELADO`): anula el paquete con un **motivo obligatorio** (trazabilidad); registra `cancelled_at` + `cancelled_by_usuario` + `cancel_reason`.

Las transiciones inválidas (saltarse `recibir`, tocar un estado terminal) se **rechazan** con un error de dominio claro. `ENTREGADO` y `CANCELADO` son **terminales**. La lógica vive detrás de la misma costura de servicio de dominio que el data-model, probada contra el mismo Postgres efímero.

## User Stories

1. Como **staff**, quiero **recibir** un paquete que estaba `ANUNCIADO`, para reflejar que ya está físicamente en la portería.
2. Como **staff**, quiero que al recibir se registre **quién** lo recibió (yo, desde mi sesión) y **cuándo**, para que la acción sea trazable.
3. Como **staff**, quiero **capturar opcionalmente la Guía** del transportador al recibir (escaneada), para tenerla como referencia sin que sea obligatoria.
4. Como **staff**, quiero recibir un paquete **aunque no tenga Guía**, porque no todos los transportadores la usan.
5. Como **staff**, quiero que el sistema **rechace recibir** un paquete que no está `ANUNCIADO` (ya recibido, entregado o cancelado), para no corromper el ciclo.
6. Como **staff**, quiero **entregar** un paquete que estaba `RECIBIDO`, para reflejar que el residente ya lo retiró.
7. Como **staff**, quiero que al entregar se muestre el **destinatario snapshot** del paquete (nombre/apartamento congelados al anunciar), para confirmar a quién se lo entrego.
8. Como **staff**, quiero que al entregar se registre **quién** entregó y **cuándo**, para trazabilidad.
9. Como **staff**, quiero que el sistema **rechace entregar** un paquete que no está `RECIBIDO` (todavía `ANUNCIADO`, o ya `ENTREGADO`/`CANCELADO`), para no entregar algo que nunca llegó ni re-entregar.
10. Como **staff**, quiero **cancelar** un paquete `ANUNCIADO` que fue un anuncio erróneo, para limpiarlo del flujo.
11. Como **staff**, quiero **cancelar** un paquete `RECIBIDO` (p.ej. devuelto al transportador), para reflejar que ya no se entregará.
12. Como **staff**, quiero que cancelar **exija un motivo obligatorio**, para que quede trazabilidad de por qué se anuló.
13. Como **staff**, quiero que al cancelar se registre **quién** canceló, **cuándo** y **por qué**, para auditoría.
14. Como **staff**, quiero que el sistema **rechace cancelar** un paquete ya `ENTREGADO` o `CANCELADO`, porque son estados finales.
15. Como **staff**, quiero que cancelar me avise que es **irreversible**, para no anular por error.
16. Como **auditor**, quiero que cada Paquete conserve el rastro de sus transiciones (estado actual + timestamps + actor por cada una), para reconstruir su historia.
17. Como **arquitecto**, quiero que el **actor de cada transición salga de la sesión real** y nunca de un id hardcodeado, para que la trazabilidad sea confiable (invariante del dominio).
18. Como **staff**, quiero que recibir/entregar/cancelar sean operaciones **idempotentes en su rechazo**: intentar una transición inválida no cambia nada ni deja el paquete a medias.
19. Como **residente** (vía `/search`, rebanada posterior), quiero que el estado que consulto sea el que la máquina de estados garantiza, para ver información fiable.
20. Como **desarrollador**, quiero **una sola función por transición** (recibir/entregar/cancelar), sin rutas legacy paralelas, para no repetir el desorden del sistema viejo (invariante del brief §14).

## Implementation Decisions

### La máquina de estados (encoda la decisión — derivado del brief §6/§7)

Estados y transiciones permitidas (el resto se rechaza):

```
              announce
   (nada) ───────────────▶ ANUNCIADO
                              │  │
                     receive  │  │  cancel (motivo)
                              ▼  ▼
                          RECIBIDO ──────────┐
                              │  │           │
                      deliver │  │ cancel    │
                              ▼  ▼ (motivo)  │
                         ENTREGADO      CANCELADO   ◀── (terminales: rechazan todo)
```

| Transición | Desde | Hasta | Escribe |
|---|---|---|---|
| `receive` | `ANUNCIADO` | `RECIBIDO` | `received_at`, `received_by_usuario_id`, `guide_number?` |
| `deliver` | `RECIBIDO` | `ENTREGADO` | `delivered_at`, `delivered_by_usuario_id` |
| `cancel` | `ANUNCIADO` o `RECIBIDO` | `CANCELADO` | `cancelled_at`, `cancelled_by_usuario_id`, `cancel_reason` (obligatorio) |

`ENTREGADO` y `CANCELADO` son **terminales**: cualquier transición desde ellos se rechaza.

### Módulos y contratos

- **Servicio de dominio** (extiende la costura del data-model — `app/domain/`): un módulo de transiciones del Paquete con `receive(session, paquete, actor, guide_number=None)`, `deliver(session, paquete, actor)`, `cancel(session, paquete, actor, motivo)`. `actor` es un `Usuario` (el staff de la sesión). Cada función valida el estado de origen y, si es inválido, lanza un error de dominio (`TransicionInvalida`) **sin mutar nada**.
- **`actor` obligatorio y tipado**: las tres transiciones exigen un `Usuario`; no hay default ni id hardcodeado (invariante del brief §14 / `CONTEXT.md`). El `Usuario` ya existe como entidad (data-model).
- **`cancel` exige `motivo`**: string no vacío; si falta o es vacío → `ValueError`. El conjunto de motivos canónicos (dropdown de la UI) se modela como un **enum `MotivoCancelacion`** VARCHAR-backed (mismo patrón que `EstadoPaquete`), con un set inicial a acordar (p.ej. `ANUNCIO_ERRONEO`, `DEVUELTO_AL_TRANSPORTADOR`, `NO_RECLAMADO`, `OTRO`); `cancel_reason` guarda su etiqueta.
- **`guide_number` en `receive`**: opcional; si se pasa, se persiste; el emparejamiento anuncio↔paquete sigue siendo por nombre/teléfono (no por guía) — el diseño solo deja la guía como referencia (brief §7).

### Cambios de esquema (migración `0004`, descendiente de `0003`)

- Añadir `cancel_reason` a `paquetes` (VARCHAR nullable; obligatorio **a nivel de servicio** solo en `cancel`, no a nivel de columna porque los no-cancelados no lo tienen). Constraint/columna con **nombre explícito** en ORM y migración (paridad esquema↔ORM).
- **Sin** columnas nuevas para recibir/entregar: `received_*`/`delivered_*`/`guide_number` ya existen (data-model). El árbol Alembic permanece de **raíz única** (`0001→0002→0003→0004`), ADR-0002.

### Errores de dominio

- `TransicionInvalida(estado_actual, transicion)` — origen no permitido; el paquete queda **intacto**.
- `ValueError` — `cancel` sin motivo.
- Las funciones son transaccionales: validan **antes** de mutar; un rechazo no deja timestamps/actores a medias.

## Testing Decisions

**Qué es un buen test aquí:** verifica **comportamiento externo observable** a través de la costura de servicio — el estado resultante, los timestamps/actor escritos, y que las transiciones inválidas se rechacen sin efecto — no los internals de SQLAlchemy.

**Costura:** la **misma** que el data-model (Seam A, servicio de dominio contra el Postgres efímero construido con `alembic upgrade head`; fixtures `db_session`/`migrated_db_url` ya existen). **No se crea costura nueva.** El guard de paridad esquema↔ORM existente cubrirá `cancel_reason` al importar el modelo.

**Casos (mapean a las user stories):**
- Recibir un `ANUNCIADO` → `RECIBIDO`, con `received_at` y `received_by_usuario` = el actor; con y sin `guide_number`.
- Entregar un `RECIBIDO` → `ENTREGADO`, con `delivered_*` = actor/now.
- Cancelar desde `ANUNCIADO` y desde `RECIBIDO` → `CANCELADO`, con `cancel_reason` + `cancelled_*`.
- `cancel` sin motivo → `ValueError`, paquete intacto.
- Rechazos: entregar un `ANUNCIADO`; recibir un `RECIBIDO`/`ENTREGADO`; cualquier transición desde `ENTREGADO`/`CANCELADO` → `TransicionInvalida`, y el paquete **no cambia** (estado ni timestamps).
- El actor se persiste como el `Usuario` pasado (no null, no hardcodeado).

**Prior art:** los tests de la rebanada data-model (`tests/data_model/test_*.py`) — mismo patrón `pytest` + Postgres efímero. Construir **test-first** con `/tdd`. Un `Usuario` de prueba se crea en el arranque del test (la entidad ya existe).

## Out of Scope

- **Rutas HTTP y modales** (`/packages`, modales Recibir/Entregar/Cancelar, bottom-sheet móvil, escáner ZXing) — rebanada de UI posterior; aquí solo la lógica de dominio.
- **Escaneo de código de barras** (ZXing en navegador) — la captura de la guía aquí es solo el parámetro `guide_number`.
- **Log de eventos / timeline** (`package_events`/`package_history`) y el historial legible de `/search` — rebanada aparte.
- **Notificaciones** (SMS/WhatsApp al recibir/entregar) y su override de staging — rebanada de notificaciones.
- **`/announce-new`** (anuncio por staff, que sí setea `announced_by_usuario`) — rebanada de announce.
- **Migración de datos** desde RDS.
- **Promoción de la Guía a llave de emparejamiento** — el esquema deja espacio, no se implementa (brief §7).

## Further Notes

- **Reusa el actor de la sesión (invariante duro).** Este slice define la **firma** (`actor: Usuario` obligatorio); de dónde sale el `Usuario` (sesión autenticada) lo cablea la rebanada de auth/HTTP. Aquí el test inyecta un `Usuario` real.
- **Bug a no heredar** (`PACKAGES_DIAGNOSIS.md`): los modales viejos se quedaban bloqueados. No aplica a esta capa de dominio, pero la rebanada de UI que la consuma debe re-habilitar el botón con `finally`. Se anota para esa rebanada.
- **Motivos de cancelación**: el enum inicial es una propuesta; el set definitivo es un detalle de UX que puede afinarse sin romper el esquema (VARCHAR-backed).
- **Consumo aguas abajo:** esta rebanada alimenta `/to-tickets`. La UI de `/packages`, las notificaciones y el timeline de `/search` cuelgan de esta máquina de estados.
