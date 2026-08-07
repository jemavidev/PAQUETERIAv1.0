# 57 — Fix: tabs/notificaciones "dañados" en desktop (cache de CSS) + distribuir Notificaciones a ancho completo en mobile

**Pedido original (cliente):** "Te pedi encarecidamente que dividieras lo
que es la vista del mobil con la vista del desktop, no se porque no
tomaste esta instruccion con relacion a los TABS, ahora las vistas del
desktop se dañaron [...] Veo que no solo eso de los TABS se afecto, tambien
dalaste las 'notificaciones' en el desktop. ANLIZA A FONDO LO QUE HICISTE Y
COMO LO HICISTE PARA QUE PROPONGAS CORREGIRLO. Por ultimo en tu
modificacion al tab de 'notificaciones' [...] seria posible que para la
vista de mobiles distribuyas el contenido en el ancho total del
dispositivo, esto ya que se encuentra todo el contenido ajustado y
apiñado a la izquierda."

**Status:** implementado

## Análisis — causa raíz real

**No fue un error de lógica CSS.** Se re-derivó a mano, regla por regla, el
comportamiento esperado de cada clase `lg:*` agregada en [[54]]/[[55]]/[[56]]
contra el HTML real, y la cascada mobile-first (`grid` → `lg:flex`,
`bg-slate-50 border` → `lg:bg-transparent lg:border-0`, `flex flex-wrap` →
`lg:grid lg:grid-cols-[...]`, etc.) es correcta — confirmado además
recompilando Tailwind localmente y verificando que CADA una de esas reglas
(incluida la columna con valor arbitrario `grid-cols-[1fr_repeat(4,minmax(0,1fr))]`)
se genera bien.

**La causa real: `base.html` sirve el CSS compilado como
`/static/css/tailwind.css?v=29` — un cache-buster manual.** El comentario
en el propio archivo ya lo advertía: *"Al agregar clases nuevas en una
plantilla hay que RECOMPILAR este archivo y subir el ?v= — no es un CDN en
runtime."* El `?v=29` llevaba fijo desde el 2026-08-05 (issue 48, la última
vez que alguien sí lo subió). En los 3 despliegues de este pedido (54, 55,
56) se agregaron clases Tailwind genuinamente nuevas (el grid 2x2 de tabs,
`bg-slate-50`/`lg:bg-transparent`/`lg:border-0`, el layout de tarjetas de
Notificaciones con la columna arbitraria) SIN subir el `?v=`. El servidor
sí recompiló el CSS correctamente en cada deploy (`Dockerfile` corre `npm
run build:css` en cada build) -- el problema es que cualquier navegador
que ya tuviera cacheado `tailwind.css?v=29` de ANTES de estos 3 cambios
nunca volvió a pedirlo, porque la URL nunca cambió. Ese navegador sigue
sirviendo, de memoria, un CSS que no define las reglas `lg:` necesarias
para esas clases nuevas -- así que en desktop, esos elementos quedan sin
ninguna regla que revierta el estilo mobile, mostrando algo roto/mezclado
en vez de la vista de escritorio de siempre. Los deploys previos de esta
misma vuelta (52/53, el visor de fotos) escaparon del problema solo por
suerte: la única clase Tailwind nueva que agregaron (`overflow-hidden`) ya
existía de sobra en el resto de la app, así que ya estaba en cualquier CSS
cacheado medianamente reciente.

Esto explica también por qué mobile SÍ se veía bien en cada ronda (54, 55,
56) mientras el cliente lo probaba desde el celular: el navegador del
celular sí traía el CSS fresco (o no tenía nada cacheado todavía); el
navegador de escritorio, probado por primera vez recién en este pedido,
llevaba semanas con una copia vieja cacheada bajo la misma URL.

## Corrección

- `base.html`: `?v=29` → `?v=30` -- fuerza a todo navegador a pedir el CSS
  fresco, que ya tenía las reglas correctas desde el deploy de 56.
- Regla a seguir de ahora en más (ya documentada en el propio archivo,
  simplemente no se siguió): **toda vez que se agregue/quite una clase de
  Tailwind en cualquier plantilla, subir el `?v=` en el mismo commit.**

## Adicional — Notificaciones en mobile, distribuir a ancho completo

El layout de tarjetas de [[54]] usaba `flex flex-wrap` sin `justify-content`
para los 4 canales de cada evento -- por defecto quedaban pegados a la
izquierda (`justify-start`), con el resto del ancho vacío a la derecha.
Se agregó `justify-between` (solo mobile, `lg:justify-normal` lo neutraliza
en desktop) -- como el `<p>` del evento fuerza su propia línea completa
(`w-full`), `justify-between` solo afecta a la línea de los 4 canales, que
ahora quedan repartidos borde a borde en vez de amontonados.

## Verificación

- Recompilación local de Tailwind: confirmado que las 6+ reglas `lg:*` en
  cuestión (`lg:bg-transparent`, `lg:border-0`, `lg:flex`, `lg:grid`,
  `lg:justify-normal`, `justify-between`) se generan correctamente.
- Suite completa (`tests/data_model tests/web`): 633/633, sin regresiones.
- Pendiente: confirmar en `test.papyrus.com.co` que desktop volvió
  exactamente a como estaba antes de [[54]], que mobile sigue viéndose
  como en [[56]], y que los canales de Notificaciones ahora se reparten en
  todo el ancho en mobile. El cliente debería hacer un refresh forzado
  (Ctrl+Shift+R / Cmd+Shift+R) la primera vez, ya que su navegador de
  escritorio puede seguir teniendo cacheado el CSS viejo hasta que la URL
  con `?v=30` se lo fuerce.
