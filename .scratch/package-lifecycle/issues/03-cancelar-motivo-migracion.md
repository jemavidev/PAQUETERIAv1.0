# 03 — Cancelar (+ motivo obligatorio + migración `cancel_reason`)

**Spec:** `.scratch/package-lifecycle/spec.md` · **Glosario:** Estados del Paquete, Cancelar, Usuario · **ADR:** 0002 (Alembic raíz única)

**What to build:** El staff **cancela** un paquete `ANUNCIADO` o `RECIBIDO` con un **motivo obligatorio**: queda `CANCELADO` (estado terminal), con **quién** canceló, **cuándo** y **por qué**. Cancelar es irreversible.

**Blocked by:** 01 — Recibir (+ infraestructura de transiciones). Reutiliza `TransicionInvalida` y `receive` (para probar cancelar desde `RECIBIDO`). Independiente del 02.

**Status:** ready-for-agent

- [ ] Migración `0004` **descendiente de `0003`** (`down_revision = "0003_paquetes"`) que añade `cancel_reason` a `paquetes` (VARCHAR nullable). Árbol de **raíz única** (ADR-0002), `alembic heads` = 1 al final; NO edita migraciones previas.
- [ ] Enum `MotivoCancelacion` **VARCHAR-backed** (mismo patrón que `EstadoPaquete`), set inicial: `ANUNCIO_ERRONEO`, `DEVUELTO_AL_TRANSPORTADOR`, `NO_RECLAMADO`, `OTRO`.
- [ ] `cancel(session, paquete, actor, motivo)`: `{ANUNCIADO | RECIBIDO} → CANCELADO`; escribe `cancelled_at` (now), `cancelled_by_usuario_id = actor.id`, `cancel_reason = motivo`.
- [ ] `motivo` vacío o `None` → `ValueError`, paquete **intacto**.
- [ ] **Rechaza** (`TransicionInvalida`, sin efecto) desde `ENTREGADO` o `CANCELADO` (terminales).
- [ ] `actor` es un `Usuario` **obligatorio**.
- [ ] Guard de paridad esquema↔ORM extendido a `cancel_reason` (da `[]`); Seam B round-trip verde con la migración `0004` (que también baja).
- [ ] Tests: cancelar desde `ANUNCIADO` **y** desde `RECIBIDO`; sin motivo → `ValueError`; rechazo desde `ENTREGADO`/`CANCELADO` sin efecto.
