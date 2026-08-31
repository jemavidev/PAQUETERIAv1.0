# 273 — `/residentes` tab Dirección: espacio picker↔botones cuando el toggle no aparece

**Pedido original (cliente):** "Veo que después de 'Mudar residente de
apartamento' no dejaste espacio entre 'picker-apto-input-direccion' y
'Guardar Dirección', está pegado y solo se corrige si el toggle está
visible, corrígelo por favor."

**Status:** implementado

## Diagnóstico

Seguimiento a issue 270/271: el margen entre el picker y la fila de
botones vivía SOLO en el `mb-3 mt-3` del `<div>` que envuelve al
toggle "Mudar residente de apartamento" -- como issue 270 lo esconde
por completo cuando `mi_ocupante` es `None`, en ese caso no quedaba
ningún elemento con margen entre el picker y los botones.

## Implementación

`customers_manage/detail.html` -- `mt-3` agregado directo a la fila
`<div class="flex gap-2">` (Guardar Dirección/Quitar), que no depende
de si el toggle se renderiza. Con el toggle presente, su `mb-3`
colapsa con este `mt-3` (sibling block margins en flujo normal, mismo
resultado visual de antes); sin el toggle, este margen queda solo y
alcanza igual.

## Verificación

Suite completa de los 4 archivos tocados en el mismo lote (issue 272):
537 passed. Verificado en vivo contra una persona SIN Ocupante activo
(`/residentes/1e0674e4-.../?tab=direccion`, toggle ausente): la clase
`flex gap-2 mt-3` está presente en el HTML servido.
