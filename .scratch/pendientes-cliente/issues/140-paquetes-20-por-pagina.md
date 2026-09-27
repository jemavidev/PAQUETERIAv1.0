# 140 — `/paquetes`: 20 por página (revierte issue del 2026-08-13)

**Pedido original (cliente):** "como podrías aumentar a 20 la cantidad de paquetes listados"
(en el marco de la conversación sobre paginación, issue [[139]]).

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

- `_POR_PAGINA` en `packages/routes.py`: `10 → 20`. Ese `10` no era casual — venía de una
  decisión explícita del 2026-08-13 (skill `prototype`, ganador "Grid denso", que pidió bajar
  de 20 a 10). Se documentó en el propio comentario del código que volvió a 20 por este pedido,
  sin perder el porqué del cambio anterior.
- `/residentes` ya estaba en 20 — sin cambios ahí.

## Verificación

- `test_paginacion_con_mas_de_10_paquetes` renombrado a
  `test_paginacion_con_mas_de_20_paquetes`, ajustado a la nueva cantidad de páginas.
- Suite completa: sin regresiones (ver [[139]]).
- Pendiente: deploy a test.papyrus.com.co.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
