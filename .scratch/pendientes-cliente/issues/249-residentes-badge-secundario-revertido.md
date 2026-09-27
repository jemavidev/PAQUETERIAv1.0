# 249 — Seguimiento a issue 248: no mostrar badge "Secundario"

**Pedido original (cliente):** "en caso que sea 'Secundario' simplemente
no lo coloques."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

`customers_manage/detail.html` -- revierte la mitad de issue 248: el
badge junto a "Auto" vuelve a mostrarse SOLO cuando el Ocupante es
Principal (criterio original de issue 69), sin badge para Secundario. El
texto corto "Principal" (en vez de "Residente principal") se queda igual,
eso no se pidió revertir.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
