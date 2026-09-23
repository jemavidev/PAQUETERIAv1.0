# 382 — Contador de días: solo cuenta mientras está Recibido

**Pedido original (Jesús):** "los días solo se cuentan desde que se recibe el paquete, después de entregado este debería dejar de contarse, esto debe aplicar tanto para consultar como para las vistas de mis datos" (hallazgo 8).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Decisiones

- Recibido: días desde la recepción hasta ahora (igual que hoy).
- Entregado: días entre recepción y entrega, congelados (dejan de contar al entregar).
- Anunciado / Cancelado sin recepción: sin contador. Cancelado tras recibir: congelado al cancelar.
- Aplica a `/consultar` y a `/mis-paquetes`.

## Verificación

- `tests/data_model/test_dias_en_porteria.py` (5) + una en `test_search.py` y otra en `test_mis_paquetes.py` (fallaban antes): Anunciado sin contador, Recibido cuenta hasta hoy, Entregado y Cancelado-tras-recibir congelados.
