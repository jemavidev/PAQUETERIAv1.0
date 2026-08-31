# 268 — Pulso visual breve al refrescar la página (F5/botón recargar)

**Pedido original (cliente):** "existe la posibilidad de mostrar que la
página se actualizó, de qué forma podría pasar esto, algo pequeño pero
que se note" -- propuesto por Claude: detectar un refresh REAL
(`performance` Navigation Timing, no cualquier carga/navegación normal)
y disparar un pulso breve. Cliente confirmó: "pulso breve solo en
refresh real".

**Status:** implementado

## Verificación

`base.html` es compartido por toda la app -- corrida completa
(`tests/web` + `tests/data_model`): 1259 passed. Sin navegador
conectado esta sesión, no se pudo confirmar visualmente el pulso en un
refresh real -- la lógica (detección vía Navigation Timing +
animación CSS) se verificó por lectura de código, no en vivo.

## Alcance

`base.html` (layout compartido por TODA la app, no solo /residentes o
/mis-datos -- la señal es genérica, no depende de ninguna vista
puntual): una barra delgada (3px, `--site-brand`, ancho completo, fija
arriba de todo con `z-index` por encima del header) que barre de
izquierda a derecha y se desvanece en ~500ms, SOLO cuando
`performance.getEntriesByType('navigation')[0].type === 'reload'`
(con fallback al `performance.navigation.type` legado para navegadores
viejos) -- nunca en una navegación normal (click en un link, submit de
un form, etc.), que es justo la señal que se pidió.
