# 53 — `/consultar`: quitar las flechas del visor de fotos, dejar solo swipe

**Pedido original (cliente):** "remove the arrows on the images, lets the
swipe funtionality working as it is, just remove the 2 arrows for now"

**Status:** implementado

## Contexto

Ajuste sobre el visor de fotos de [[52]] (recién desplegado) — antes de que
el cliente confirmara en vivo el resto de esa entrega, pidió quitar los dos
botones de navegación (anterior/siguiente) superpuestos en la imagen,
dejando la navegación entre fotos solo por swipe.

## Implementación

`app/web/templates/components/_visor_fotos.html`:

- Eliminados los dos `<button data-visor-anterior>` / `<button
  data-visor-siguiente>` (con sus SVG de flecha) y su wiring en JS
  (`btnAnterior`/`btnSiguiente`).
- El swipe (gesto de 1 dedo sin zoom activo) queda sin cambios — es la
  única forma de navegar entre fotos con touch ahora.
- Las flechas de teclado (← →) y Escape se mantienen intactas como
  respaldo para quien usa el visor con mouse/teclado en escritorio (sin
  swipe disponible ahí, y ya no hay botón visible tampoco — "por ahora",
  según el pedido, así que se dejó ese respaldo en vez de quitar toda forma
  de navegar sin swipe).
- El contador ("1 / 3") se mantiene — sigue siendo útil sin las flechas
  para saber cuántas fotos hay y en cuál se está.

## Verificación

- Sintaxis del `<script>` con `node --check`, Jinja con `Environment.parse()`.
- `tests/web/test_search.py`: 16/16 (ningún test dependía de los botones
  eliminados).
- Pendiente: confirmar en `test.papyrus.com.co` que el swipe sigue
  funcionando igual sin las flechas.
