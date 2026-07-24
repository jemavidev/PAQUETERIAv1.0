---
status: accepted
---

# Árbol Alembic de raíz única (baseline nueva; RDS = fuente de datos, no de esquema)

El rebuild parte de una **migración baseline con una sola raíz** (`down_revision = None` exactamente una vez) que construye el modelo nuevo. Se **retira** el historial viejo (38 migraciones con **3 raíces desconectadas**, cuyos estados no coinciden entre RDS / contenedor prod / repo) y sus cicatrices manuales (`fix_migration_conflict.py`, `INSTRUCCIONES_*MIGRACION*.md`). Las 28 tablas de RDS dejan de ser el esquema a heredar y pasan a ser la **fuente de datos** para una migración de datos aparte.

## Considered Options

- **Continuar el historial existente** (enlazar las 3 raíces y seguir migrando). Rechazado: arrastra un grafo roto que ya causó incidentes; `alembic upgrade head` no reconstruye el estado real.
- **Introspección/autogenerar desde RDS.** Rechazado: RDS es el esquema *viejo*, y el modelo nuevo (§6 del brief) es deliberadamente distinto.

## Consequences

- `alembic upgrade head` sobre un Postgres vacío construye el esquema completo nuevo; `upgrade head` → `downgrade base` hace round-trip limpio (gate de CI).
- Se pierde la continuidad del historial de migraciones — aceptado a cambio de un grafo sano.
- Las rebanadas siguientes (eventos, notificaciones, credenciales de auth, fotos) añaden migraciones **descendientes de esta raíz**; el árbol permanece de raíz única.
