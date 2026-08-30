# 247 — `/residentes/{id}`: título deja solo el nombre, sin "Ficha de residente - "

**Pedido original (cliente):** "Elimina este texto 'Ficha de residente -
', se ve mejor solo el nombre del residente."

**Status:** implementado

## Alcance

Seguimiento directo a issue 244 (mismo `encabezado_volver` de
`customers_manage/detail.html`). El título pasa a ser directamente
`persona.nombre`, sin el prefijo fijo.
