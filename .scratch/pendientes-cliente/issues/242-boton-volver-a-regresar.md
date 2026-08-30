# 242 — Botón "Volver" → "Regresar" en los modales de confirmación

**Pedido original (cliente):** "Para los botones que aparece 'Volver'
cambialo a 'Regresar'"

**Status:** pendiente

## Alcance

`components/_modales.html::modal_confirmacion` -- el botón de cancelar
("Volver", texto fijo, `mostrar_volver=True` por default) es el único
lugar de todo el código donde "Volver" aparece hoy como texto de botón
visible; se usa desde CUALQUIER modal de confirmación de la app (no solo
Residentes -- también /paquetes, cancelar/eliminar, etc.), así que el
cambio es al nivel del macro compartido, no vista por vista.

`components/_breadcrumbs.html::encabezado_volver` tiene un default
`texto_volver='Volver'` en su firma, pero el único llamador real
(`customers_manage/detail.html`) siempre lo sobreescribe con "Volver a
Residentes" -- ese default nunca se renderiza como "Volver" bare hoy, así
que queda fuera de este pedido (no hay ningún botón visible que decir).
