# 244 — `/residentes/{id}`: el título "Ficha de residente" incluye el nombre

**Pedido original (cliente):** "Para la vista /residentes necesito que en
la parte superior 'Ficha de residente' agregues el nombre del usuario
actual donde se está modificando, esto con el fin de saber los datos de
quien se está modificando, podría ser 'Ficha de residente - <Nombre del
residente>'."

**Status:** implementado

## Alcance

`customers_manage/detail.html` -- título de `encabezado_volver` (issue
68/224). `persona` ya es la Persona de la ficha actual (`persona.nombre`).

## Seguimiento (issue 247)

El cliente pidió quitar el prefijo fijo "Ficha de residente - " y dejar
solo el nombre -- ver issue 247.
