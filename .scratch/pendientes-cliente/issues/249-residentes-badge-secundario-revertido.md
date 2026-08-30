# 249 — Seguimiento a issue 248: no mostrar badge "Secundario"

**Pedido original (cliente):** "en caso que sea 'Secundario' simplemente
no lo coloques."

**Status:** implementado

## Alcance

`customers_manage/detail.html` -- revierte la mitad de issue 248: el
badge junto a "Auto" vuelve a mostrarse SOLO cuando el Ocupante es
Principal (criterio original de issue 69), sin badge para Secundario. El
texto corto "Principal" (en vez de "Residente principal") se queda igual,
eso no se pidió revertir.
