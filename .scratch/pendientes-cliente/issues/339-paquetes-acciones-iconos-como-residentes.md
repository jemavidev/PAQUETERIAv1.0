# 339 — `/paquetes`: íconos de la columna Acciones iguales a `/residentes`

**Pedido original (cliente):**
"antes de iniciar con la version mobil, necesito que los iconos de la
columna "Acciones" sea similares en todo aspecto a los que manejas en la
vista de /residentes"

**Status:** implementado, pendiente confirmar visualmente el tamaño ya corregido

## Ronda 2 (mismo issue, pedido de seguimiento del cliente)

**Pedido:** "VEO QUE LOS TAMAÑOS DE LOS ICONOS SON DIFERENTES ENTRE LAS 2
VISTAS" -- la primera pasada igualó forma/color (`chip_icono`) pero dejó el
tamaño fijo en `h-9 w-9` (36px, issue 79/2026-08-19: "mismo tamaño que los
botones de filtro"), mientras /residentes usa
`clamp(1.625rem,7.8vw,2.15rem)` -- responsive, tope real ~34.4px en
cualquier viewport de escritorio (el 7.8vw ya excede el techo por encima de
~441px) y baja hasta 26px en mobile. Diferencia real (36px fijo vs ~34.4px
en desktop), no un error de percepción.

**Fix:** `packages/_acciones.html::_tam_accion` pasa a usar el mismo
`clamp(1.625rem,7.8vw,2.15rem)` que `customers_manage/_resultados.html::
tam_icono` -- mismo token exacto. De paso se igualó también el tamaño del
glifo SVG interno (`h-4 w-4`, antes `h-5 w-5`) para que la proporción
ícono/chip sea la misma que en /residentes.

**Verificación:** verificado en vivo en localhost:8010 (screenshot +zoom
comparando ambas columnas) antes del pedido de "no analizar en el navegador
por ahora" -- pendiente confirmación visual final del cliente.

## Ronda 3 (mismo issue, pedido de seguimiento del cliente)

**Pedido:** "Veo que el boton de cancelar, aunque no se pueda cancelar un
paquete este sigue apareciendo, la idea es que tenga el mismo comportamiento
de los demas que no estan activos (un color tipo gris y desactivado)".

**Contexto:** "Cancelar" (y el ícono "Acción" cuando el paquete está en
CANCELADO) se quedaban en ROJO en estados terminales -- un caso especial
preservado desde issue 79 (2026-08-14: "todos los iconos siempre tengan
colores"), documentado explícitamente en `packages/_acciones.html` como
excepción deliberada. Ese criterio contradice lo que este mismo issue 339
vino a unificar: en /residentes, apagado/no aplicable es SIEMPRE el chip
gris plano, sin excepciones de color por estado.

**Fix:** ambos casos (Acción en CANCELADO, Cancelar en estados terminales)
pasan de `chip_icono('red', tam=_tam_accion)` a `_accion_off` (mismo gris
plano que ya usa ENTREGADO). Comentario de cabecera del archivo actualizado
para reflejar que la excepción de issue 79 quedó revertida.

**Verificación:** pendiente -- el cliente pidió no analizar en el navegador
por ahora.

## Contexto

`/paquetes` (`packages/_acciones.html::acciones_iconos`) usa un estilo
"solo ícono, sin caja" (issue 79): `rounded-lg`, sin fondo/borde en reposo,
solo `hover:bg-slate-100`, tamaño fijo `h-9 w-9` (calibrado en 2026-08-19
para igualar los botones de Estado de la barra de filtros).

`/residentes` (`customers_manage/_resultados.html`) usa el macro
`chip_icono` (`components/_badge.html`): círculo (`rounded-full`) con fondo
de color siempre visible (`bg-{color}-100` + borde a juego), que oscurece
al pasar el mouse (`hover:bg-{color}-200`). El estado apagado/no aplicable
es un chip plano gris (`bg-slate-50 border-slate-100 text-slate-300`), no
solo el ícono en gris.

Pedido explícito: que `/paquetes` adopte el mismo lenguaje visual de
`chip_icono`, no el propio de `_acciones.html`.

## Implementación

- `packages/_acciones.html` importa `chip_icono` de `components/_badge.html`
  y reemplaza `accion_icono_base`/`_mobile`/`_desktop` (rounded-lg, sin
  fondo) por `chip_icono(color, tam='h-9 w-9')` en cada ícono activo --
  mismo tamaño `h-9 w-9` que ya tenía (no forma parte de este pedido,
  queda para la tarea de mobile que sigue), pero ahora círculo relleno.
- Mapeo de color por ícono, siguiendo el mismo criterio que ya usa
  `/residentes` para WhatsApp/Teléfono (`green`/`blue`): WhatsApp=green,
  Teléfono=blue, Email=indigo, Modificar=slate, Acción=blue (Recibir) o
  green (Entregar), Cancelar=red, Eliminar=red.
- Estado apagado/no aplicable (WhatsApp sin permiso, Teléfono sin dato,
  Email sin dato, Modificar fuera de ANUNCIADO/RECIBIDO, Acción en
  ENTREGADO): chip gris plano `bg-slate-50 border-slate-100 text-slate-300`,
  mismas clases que usa `/residentes` para su propio estado apagado (antes
  era solo el ícono en gris, sin fondo).
- Caso especial preservado (issue 79, sin tocar la lógica): Acción en
  CANCELADO y Cancelar en estados terminales siguen en rojo (no gris) pero
  ya no clicables -- ahora como chip rojo (`chip_icono('red', ...)`) en un
  `<span>` en vez de solo el ícono rojo plano.

## Verificación

- Pendiente: correr la suite de `/paquetes` y confirmar visualmente contra
  `localhost:8010` que los íconos de Acciones (activos y apagados) se ven
  igual que los de `/residentes` en el mismo viewport.
