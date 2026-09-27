# 244 — `/residentes/{id}`: el título "Ficha de residente" incluye el nombre

**Pedido original (cliente):** "Para la vista /residentes necesito que en
la parte superior 'Ficha de residente' agregues el nombre del usuario
actual donde se está modificando, esto con el fin de saber los datos de
quien se está modificando, podría ser 'Ficha de residente - <Nombre del
residente>'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

`customers_manage/detail.html` -- título de `encabezado_volver` (issue
68/224). `persona` ya es la Persona de la ficha actual (`persona.nombre`).

## Seguimiento (issue 247)

El cliente pidió quitar el prefijo fijo "Ficha de residente - " y dejar
solo el nombre -- ver issue 247.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
