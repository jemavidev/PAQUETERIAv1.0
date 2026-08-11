# 02 — Cupo máximo de Ocupantes: 5 → 10

**What to build:** staff puede registrar hasta 10 Ocupantes activos por unidad (antes 5) — el principal cuenta dentro de ese cupo.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `MAX_OCUPANTES_ACTIVOS` pasa de `5` a `10` en `ocupante_service.py`.
- [ ] `agregar_ocupante` sigue rechazando el 11º Ocupante activo con el mismo mensaje de error (número actualizado).
- [ ] Tests existentes que asumían el límite de 5 se actualizan para el límite de 10 (no se borran, se ajustan al nuevo número).
