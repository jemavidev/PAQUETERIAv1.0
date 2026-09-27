# 387 — `/consultar`: entregados/cancelados de más de 15 días, ofuscados

**Pedido original (Jesús):** "los anunciados/recibidos siempre se podrán consultar, los entregados/cancelados se ofuscará la información de estos" tras 15 días; "no cambies la lógica de los códigos" (hallazgo 5).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Decisiones

- Sin sesión de staff: un paquete Entregado o Cancelado hace más de 15 días (desde `delivered_at`/`cancelled_at`) se
  sigue encontrando, pero se muestra ofuscado: nombre con iniciales, teléfono enmascarado, sin apartamento, sin fotos,
  sin guía, sin nombres del staff ni cobro; solo estado y fechas.
- Anunciados y Recibidos: sin cambios. Staff: ve todo siempre. Códigos y búsqueda: sin cambios.

## Verificación

- `tests/web/test_consultar_ofuscado.py` (5): Entregado y Cancelado de más de 15 días sin sesión muestran iniciales, teléfono con los últimos 4 dígitos, sin apartamento, fotos, guía ni staff, con nota de privacidad; de menos de 15 días, Recibido viejo y vista de staff, completos.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar en vivo (localhost)". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
