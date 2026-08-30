# 253 — `/residentes/{id}` tab Residentes: desborda en mobile

**Pedido original (cliente):** "Intenta iterar en esta vista y
específicamente el cómo se ve el tab de 'Residentes', necesito que sea
amigable a la vista de cada uno de los componentes y features, adicional
veo que para la versión mobile se ve bastante regular y sobresale del
área donde deberían estar, analiza cuál sería la mejor opción y
corrige."

**Status:** implementado

## Diagnóstico

Cada tarjeta de residente usaba `flex items-center justify-between` con
el nombre/teléfono/badge a la izquierda (sin `min-w-0`, no podía encoger)
y las acciones a la derecha (`shrink-0`, tamaño fijo). Issue 252 movió
Editar/Notificaciones a ese mismo bloque de acciones, que ya tenía
Confirmar/Rechazar-Eliminar -- hasta 4 píldoras en una sola fila junto a
un nombre que tampoco cede espacio. En mobile (`max-w-lg` incluso antes
de `lg:`, issue 225) esa fila es más ancha que la tarjeta -- de ahí el
desborde reportado.

## Fix

- La fila pasa de `flex items-center justify-between` a `flex flex-col
  gap-2 lg:flex-row lg:items-center lg:justify-between` -- en mobile el
  nombre/badge y las acciones se apilan (acciones en su propio renglón,
  con espacio de sobra para envolver); desde `lg:` (mismo quiebre que ya
  usa el ancho de página, issue 225) vuelven a ir lado a lado.
- `min-w-0` en el contenedor del nombre + `truncate` en nombre/teléfono,
  para que un nombre largo no fuerce el ancho de la fila en ningún caso
  (defensivo, incluso ya apilado).
- El bloque de acciones pierde `shrink-0` (ya no compite por espacio con
  el nombre en mobile) y usa `lg:justify-end lg:shrink-0` solo desde el
  quiebre donde vuelve a compartir fila.
