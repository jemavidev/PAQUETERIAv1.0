# 278 — Seguimiento a [[277]]: badges a 2da fila, íconos más grandes, ancho fluido

**Pedido original (cliente):** "creo que seria mejor si tanto la opcion de
las pildoras 'Auto y Principal' en caso que apliquen se bajen a una
segunda fila, permitiendo un poco mas de espacio y unos iconos de accion
un poco mas grandes, de que forma lo puedes hacer lo mas ajustable
posible orientado a dispositivos moviles"

**Status:** verificado (desplegado y confirmado en test.papyrus.com.co)

## Alcance

`customers_manage/_resultados.html` (tabla plana de `/residentes`,
mismo mobile-only scope que [[277]]):

1. Badges "Auto"/"Principal" (columna Nombre): en mobile pasan a su
   propia fila debajo del nombre (antes: `flex-wrap` los bajaba de forma
   incidental solo cuando no cabían, no era intencional). Técnica:
   contenedor exterior `flex flex-col` en mobile / `sm:flex-row` en
   desktop; los badges viven en un `<div>` interno con `sm:contents` --
   en mobile es una fila propia, desde `sm:` desaparece como caja (deja
   de contar como "segunda fila") y sus hijos vuelven a ser ítems
   directos del flex original (mismo comportamiento de hoy en desktop,
   0 cambios ahí).
2. Con el nombre ya sin competir por espacio con los badges en la misma
   línea, su ancho máximo en mobile pasa de un valor fijo (`max-w-[90px]`,
   [[277]]) a uno fluido con `clamp()`: `max-w-[clamp(120px,38vw,220px)]`
   -- escala con el ancho real del dispositivo en vez de un solo número
   mágico para todos los tamaños (pedido explícito: "lo mas ajustable
   posible"). `table-fixed` con columnas en `%` se consideró y se
   descartó -- más ajustable en teoría, pero exige asignar ancho a las
   4 columnas incluyendo la oculta (Teléfono) y es bastante más frágil
   de mantener; `clamp()` en el único punto que lo necesitaba (Nombre)
   da el mismo resultado con mucho menos superficie de cambio.
3. Íconos de Acciones: vuelven a su tamaño normal (`h-8 w-8`, el mismo
   que ya usa desktop y la ficha) -- el shrink a `h-7 w-7` de [[277]]
   se retira, ya no hace falta con el espacio recuperado del punto 1.
   Gap vuelve a `gap-1.5` (antes `gap-1` en mobile).
4. Padding horizontal de celdas: se re-evalúa `px-1` de [[277]] caso por
   caso para que el total siga sin generar scroll lateral.

## Verificación

Mismo método que [[277]]: iframes same-origin inyectados sobre la página
real en dev local (`sm:`/media queries evalúan contra el ancho de cada
iframe) -- probado en 7 anchos de mobile a la vez (340, 360, 375, 390,
393, 414, 428px), no solo uno, dado que el pedido explícito era "lo mas
ajustable posible" y no un solo breakpoint.

Resultado: **0px de overflow desde 360px en adelante** (cubre la
inmensa mayoría de dispositivos reales -- Android moderno arranca en
~360px, iPhone SE 2/3 en 375px). Por debajo de eso (340px, gama muy
vieja/rara hoy) queda un remanente de 14px -- los pisos ya no dan para
más sin degradar más la usabilidad (íconos/píldoras ya cerca de su
tamaño mínimo legible/tocable).

Hallazgo en el camino (no era el problema real, pero se corrigió de
paso): el `<div>` interno de Auto/Principal (la "segunda fila") se
estiraba (`align-items: stretch`, comportamiento por defecto de
`flex-col`) hasta ocupar todo el ancho del contenedor en vez de
ajustarse a su propio contenido -- se agregó `items-start` (mobile) +
`w-fit` para que cada fila mida lo que realmente necesita. El
verdadero ancho mínimo de la columna Nombre resultó estar dado por la
fila con AMBAS píldoras juntas (Auto + Principal, ~109px, más ancho que
cualquier nombre truncado) -- se achicó su padding (`px-1.5` en mobile)
para bajarlo.

Suite completa (`pytest tests/web/test_customers_manage.py`): 151
passed, sin regresiones. Desktop (`sm:` en adelante, probado a 1000px)
sin cambios visibles -- píldoras siguen inline junto al nombre, íconos
en su tamaño de siempre.
