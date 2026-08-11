# 03 — Dominio: promover a principal también confirma

**What to build:** `promover_a_principal` marca `confirmado_en` (si todavía era `None`) además de `es_principal=True`, sin importar si se llama desde el botón "Promover" explícito o desde un disparador automático — nunca debe quedar un Ocupante `es_principal=True` sin confirmar.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `promover_a_principal` marca `confirmado_en = ahora()` cuando estaba `None`, en la misma operación que marca `es_principal=True`.
- [ ] Si el Ocupante ya estaba confirmado antes de promoverse, `confirmado_en` no se pisa (conserva la fecha original).
- [ ] El principal anterior (si había) se sigue degradando en la misma transacción, sin cambios ahí.
- [ ] Test de dominio en `tests/data_model/test_ocupante_service.py`: promover un Ocupante `pending` lo deja `es_principal=True` **y** `confirmado_en` no nulo.
