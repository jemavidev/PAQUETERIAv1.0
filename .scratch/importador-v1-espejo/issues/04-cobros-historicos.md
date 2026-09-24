# 04 — Cobros históricos

**What to build:** las estadísticas de cobro de la v2 muestran el historial real de la v1 desde noviembre de 2025. Cada paquete entregado de la v1 tiene su Cobro, copia fiel de lo que cobró la v1 (ver `../spec.md`, historias 37-38).

**Blocked by:** 03 — Autoría del staff

**Status:** done

- [x] Un Cobro por cada paquete `ENTREGADO` importado: `monto_base` = `monto_total` = `total_amount` de la v1 como entero, bodegaje en 0, `cobrado_en` = `delivered_at` y `cobrado_por` = "Operador v1 (sin identificar)".
- [x] No se recalcula con las reglas de la v2 (sin exención de primera entrega ni bloques de bodegaje).
- [x] Un paquete que pasa de recibido a entregado en la v1 obtiene su Cobro en la siguiente pasada.
- [x] Si en la v1 un paquete deja de estar entregado, su Cobro importado se borra y el caso queda en el reporte como anómalo.
- [x] Esa es la única excepción al Cobro append-only, y solo aplica a paquetes con `origen_v1_id`. Queda documentada en el modelo.
- [x] No se crean movimientos de saldo ni registros de SMS.
- [x] El servicio de estadísticas del tablero incluye los cobros importados (prueba de integración).
