# 382 — Contador de días: solo cuenta mientras está Recibido

**Pedido original (Jesús):** "los días solo se cuentan desde que se recibe el paquete, después de entregado este debería dejar de contarse, esto debe aplicar tanto para consultar como para las vistas de mis datos" (hallazgo 8).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Recibido: días desde la recepción hasta ahora (igual que hoy).
- Entregado: días entre recepción y entrega, congelados (dejan de contar al entregar).
- Anunciado / Cancelado sin recepción: sin contador. Cancelado tras recibir: congelado al cancelar.
- Aplica a `/consultar` y a `/mis-paquetes`.

## Verificación

- `tests/data_model/test_dias_en_porteria.py` (5) + una en `test_search.py` y otra en `test_mis_paquetes.py` (fallaban antes): Anunciado sin contador, Recibido cuenta hasta hoy, Entregado y Cancelado-tras-recibir congelados.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
