# 247 — `/residentes/{id}`: título deja solo el nombre, sin "Ficha de residente - "

**Pedido original (cliente):** "Elimina este texto 'Ficha de residente -
', se ve mejor solo el nombre del residente."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

Seguimiento directo a issue 244 (mismo `encabezado_volver` de
`customers_manage/detail.html`). El título pasa a ser directamente
`persona.nombre`, sin el prefijo fijo.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
