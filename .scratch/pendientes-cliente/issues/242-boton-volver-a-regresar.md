# 242 — Botón "Volver" → "Regresar" en los modales de confirmación

**Pedido original (cliente):** "Para los botones que aparece 'Volver'
cambialo a 'Regresar'"

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

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

## Limpieza del registro (2026-09-26)

Estado anterior en este archivo: "pendiente" (desactualizado; el índice ya decía "implementado"). Verificado en el código: `components/_modales.html` muestra "Regresar", y el código de la app en MATT es idéntico al desplegado en test (`3ea732f`).
