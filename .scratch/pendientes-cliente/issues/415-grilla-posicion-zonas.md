# 415 — Grilla de Posición: zona azul abajo y bloque pegado arriba

**Pedido original (Jesús, 2026-09-27):** "de que forma puedes hacer que "11, 12, 21 y 22" tengan un fondo azul y adicional a
esto desde "51 hasta 72" no tenga ni padding ni margin en el fondo, quiro que para esto se vea como si esto estubieran
pegados entre si". Sigue al 414 (grilla compacta).

**Status:** verificado (desplegado en test `f17c396`, confirmado por Jesús 2026-09-27)

## Alcance

- 11, 12, 21, 22: fondo azul CLARO en reposo (la seleccionada sigue en azul oscuro con texto blanco, para distinguirla).
- 41 a 72 (filas 4-7): un solo bloque pegado (ajuste del mismo día: "51 y 52 no tendrían espacio ABAJO, eso significa que 41
  y 42 también estarían pegados") -- sin separación entre botones, solo una línea fina entre celdas y
  esquinas redondeadas únicamente en el borde exterior del bloque.
- 11 a 32 siguen como botones sueltos. Mismo orden espejo del estante y mismo un-toque-selecciona.
