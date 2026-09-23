# 372 — `/administracion/estadisticas-cobro`: optimizar para dispositivos móviles (sin scroll lateral)

**Pedido original (Jesús):** "optimiza para dispositivos moviles, por ejemplo la seccion de
'Estadísticas de cobro' es necesario hacer side scrolling para poder ver todos los botones,
creo que esto lo puedes mejorar para que todo se visualice en la misma pagina, analiza si
algun otro necesita otro tipo de ajustes".

**Status:** implementado en la propuesta (`:8011`, commit sobre el del 371; lo actual, `:8010`, no se toca); pendiente que Jesús lo confirme en su navegador

## Contexto

El scroll lateral no existe en lo actual (`:8010`, sus botones de periodo se ajustan en varias
filas): lo introdujo la propuesta del [[370]], que en móvil puso los 8 periodos en una fila
deslizable. Se corrige ahí. La segunda parte del pedido ("analiza si algún otro necesita ajustes")
se atiende con una auditoría medida en 360 / 390 / 414 / 768 px (desbordes horizontales, áreas de
toque, tamaños de letra, tablas que esconden columnas) y se arreglan los hallazgos.

## Resultado (2026-09-21)

Auditoría medida en 360 / 390 / 414 / 768 px, antes -> después (a 390 px):

| | antes | después |
|---|---|---|
| contenedores con scroll lateral | 1 (periodos: 686 px en 303) | 0 |
| elementos que se salen del ancho | 1 (y 16 a 360 px: la columna de "Ahora" a 366 px) | 0 |
| áreas de toque < 40 px | 35 (botones de 30 px, enlaces de 16-18 px) | 0 |
| textos con letra < 12 px | 37 | 0 |
| alto de la página | 7.374 px | 8.519 px (+15 %) |

Cambios: periodos en grilla de 3 columnas (los 8 a la vista); Tipo / Cobro / Torre como campos
con la etiqueta arriba y chips en grilla de 2 columnas; filtros visibles al cargar con botón
"Filtros (n)" para plegarlos; `grid-cols-1` en las 9 grillas (la causa del recorte a 360 px: la
columna implícita `auto` la estiraba el contenido de una tabla); botones >= 40 px; letra >= 12 px;
las 2 tablas ("Requieren atención", "Detrás de las cifras") pasan a listas de filas tocables con
TODOS los datos (antes se escondían Torre · Apto, tipo, fecha, "por cobrar"); Tiempos promedio sin
valores partidos; Operación y calidad con el operador a todo el ancho; padding móvil más compacto.

**Compromisos:** la página es ~15 % más alta; los filtros abiertos ocupan buena parte de la primera
pantalla (se pliegan con "Filtros"). A 768 px quedan 14 códigos de tabla de 47x32 px.
**Idea no hecha:** limitar las listas móviles a 5 filas con "Ver las 10" (recorta ~900 px).
