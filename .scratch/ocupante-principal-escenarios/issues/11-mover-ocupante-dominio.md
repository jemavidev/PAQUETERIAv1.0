# 11 — Mover residentes entre unidades — dominio

**What to build:** función de dominio que mueve a un Ocupante activo **no-principal** de su unidad actual a una unidad nueva, en un solo paso (da de baja en la anterior + agrega en la nueva, en la misma operación) — sin exigir el paso manual de "dar de baja" primero. Nunca aplica a un principal: si la Persona es principal de su unidad actual, se mantiene el bloqueo de siempre (mismo mensaje: promové a otro primero, o desvinculate si estás solo).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Nueva función en `ocupante_service.py` (o extensión de una existente) que, dado un Ocupante activo no-principal y una unidad destino, hace la baja + el alta en una sola operación de dominio.
- [ ] Si la Persona es principal de su unidad actual, la función rechaza con el mismo mensaje que ya existe hoy (no se mueve, ni siquiera si está sola en su unidad).
- [ ] Respeta las restricciones existentes de la unidad destino (cupo máximo del ticket 02, catálogo cerrado).
- [ ] Tests de dominio en `tests/data_model/test_ocupante_service.py`: mover un no-principal exitosamente, bloqueo cuando es principal (solo y con otros), unidad destino llena.
