# 348 — `/paquetes`: fondo de fila según el estado del paquete

**Pedido original (cliente):**
"de que forma puedes puedes diferenciar los paquetes, el uno del otro, te
comente que podria ser una especie de forndo o backgraund segun el estado
actual de cada paquete" (segunda vez que lo pide -- la primera fue
respondida con una recomendación alternativa, borde lateral de color, para
evitar competir con las píldoras de color que ya lleva la fila; el cliente
reafirmó la idea original de fondo).

**Status:** implementado, pendiente confirmar visualmente

## Implementación

`packages/_resultados.html`: nuevo mapa `fila_fondo` (mismo criterio de
color por Estado que `estado_colores`, ya usado en el código de acceso y
la píldora de Torre/Apto) aplicado a cada `<tr>`:

- ANUNCIADO: `bg-amber-50 hover:bg-amber-100`
- RECIBIDO: `bg-blue-50 hover:bg-blue-100`
- ENTREGADO: `bg-emerald-50 hover:bg-emerald-100`
- CANCELADO: `bg-red-50 hover:bg-red-100`

Un tono MÁS CLARO (-50) que `estado_colores` (-100) a propósito: la fila ya
lleva adentro el código de acceso (y a veces Torre/Apto) en el tono -100 de
ese mismo color -- si la fila entera usara el mismo -100, esa píldora
perdería contraste contra su propio fondo. El hover profundiza el mismo
color (-100) en vez de saltar a un gris neutro, para no "apagar" la
clasificación al pasar el mouse.

Aplica en desktop Y mobile por igual (la fila es la misma `<tr>` en ambos
casos, no hay una versión mobile-only de esto).

## Ronda 2 (mismo issue, pedido de seguimiento del cliente)

**Pedido:** "puedes agregar un borde tenue pero que se distinga"

**Contexto:** dos filas SEGUIDAS del mismo Estado comparten el mismo
`bg-{color}-50` -- sin un borde que las distinga, se fundían entre sí. El
`divide-y divide-slate-100` gris que tenía el `<tbody>` quedaba casi
invisible sobre el fondo de color.

**Implementación:** `border-b border-{color}-200` agregado al mismo mapa
`fila_fondo`, un borde por fila en el MISMO color de esa fila (se nota
incluso entre dos filas idénticas, sin agregar un color nuevo a la
paleta). El `divide-y divide-slate-100` del `<tbody>` se retira -- quedaría
redundante con el borde propio de cada fila. Fallback (estado sin mapear,
no debería ocurrir en la práctica) mantiene `border-slate-100` como antes.

## Ronda 3 (mismo issue, pedido de seguimiento del cliente)

**Pedido:** "necesito que el fondo sea menos tenue, cambia solo un poco"

**Implementación:** el fondo sube un escalón, de `-50` a `-100` (mismo tono
que ya usa la píldora de código de acceso en `estado_colores`) y el hover
de `-100` a `-200`, mismo criterio de "un escalón más oscuro" de siempre.
La píldora de código de acceso sigue distinguiéndose de su propio fondo
por el borde (`-200`, un tono más oscuro que su relleno) y el texto en
negrilla, no por el color de relleno -- se acepta ese contraste algo menor
a cambio del fondo más visible pedido. Se reconstruyó `tailwind.css`
(faltaban `hover:bg-amber-200`/`hover:bg-emerald-200` compiladas).

## Ronda 4 (mismo issue, pedido de seguimiento del cliente)

**Pedido:** "creo que puedes bajar un poco la intensidad de los colores,
estan muy fuertes"

**Contexto:** el mismo tono `-100` que se ve bien en una píldora chica
(código de acceso) resultó demasiado saturado extendido sobre un área
grande (la fila entera). Volver a `-50` habría repetido la queja de la
ronda 2 ("muy tenue").

**Implementación:** `bg-{color}-100/60` (opacidad 60%) en reposo -- un
punto intermedio real entre `-50` y `-100` sólido, en vez de saltar a otro
escalón completo de la paleta de Tailwind. `hover:bg-{color}-200` se
queda sólido (sin opacidad) -- es un estado transitorio al pasar el mouse,
no la "intensidad en reposo" de la que se quejó el cliente. Se reconstruyó
`tailwind.css` (las 4 clases con `/60` no estaban compiladas).

## Tests

`test_packages.py`: 229 passed en las 4 rondas, sin cambios necesarios
(ningún test dependía de la clase `hover:bg-slate-50`/`divide-y` de la
fila).

## Verificación

Pendiente confirmación visual del cliente.
