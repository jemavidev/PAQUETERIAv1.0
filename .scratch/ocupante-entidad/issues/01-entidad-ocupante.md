# 01 — Entidad Ocupante: tabla + funciones de dominio

**Qué construir:** Tabla `ocupantes` ligada a `apartamentos`, con Teléfono opcional (respaldado por una Persona real cuando existe) y exactamente un Ocupante "principal" por Apartamento (garantizado a nivel de base de datos). Funciones de dominio para agregar un Ocupante (con o sin teléfono), promoverlo a principal (degradando al anterior) y listar los Ocupantes de un Apartamento.

**Bloqueado por:** Ninguno — la Fase 1 (`/domain-modeling`, `CONTEXT.md` + ADR-0006) ya resolvió el modelo conceptual.

**Estado:** ready-for-agent

- [ ] Migración Alembic nueva (tras `0009`) crea `ocupantes`: `id`, `apartamento_id` (FK), `persona_id` (FK, nullable), `nombre`, `es_principal` (bool), timestamps. Índice único parcial garantiza máximo 1 `es_principal=True` por `apartamento_id`.
- [ ] Modelo ORM `Ocupante` en `app/domain/`, con `__table_args__` idénticos a la migración (paridad esquema↔ORM).
- [ ] `agregar_ocupante(session, apartamento, nombre, telefono=None)`: con teléfono, reutiliza/crea la Persona (`get_or_create_persona`) y liga `persona_id`; sin teléfono, crea un Ocupante liviano. El primer Ocupante de un Apartamento (sin ningún otro previo) debe tener teléfono y queda principal automáticamente.
- [ ] `promover_a_principal(session, ocupante)`: `ValueError` si el Ocupante no tiene `persona_id` (sin teléfono). Si lo tiene, degrada al principal anterior del mismo Apartamento y marca a este como principal, en la misma transacción (nunca 0 ni 2 principales visibles).
- [ ] `listar_ocupantes(session, apartamento)`: todos los Ocupantes del Apartamento, principal primero.
- [ ] `tests/data_model/test_ocupante_service.py` cubre: agregar sin teléfono, agregar con teléfono (reutiliza Persona existente), primer Ocupante queda principal automático, segundo Ocupante NO se auto-promueve, promover sin teléfono falla, promover con teléfono degrada al anterior, listar ordena principal primero.
- [ ] `test_parity_esquema_orm` y `test_migration_graph` (ya existentes) siguen pasando sin cambios.
- [ ] Suite completa (`pytest`) pasa.
