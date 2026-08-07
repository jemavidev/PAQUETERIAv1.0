# 58 — `/mis-datos` y `/mis-paquetes`: tabs desktop más grandes y resaltados (misma posición)

**Pedido original (cliente):** "me parece perfecto el como se ve la version
mobil. Pero creo que te fuiste muy lejos con relacion a la version
desktop, puedes para la version de desktop cambiard la forma en como se
ven los TABS (solo en el look and feel), para que se vean un poco mas
grande en el desktop, y se pueda resaltar cuales son y cual esta
seleccionado, pero que se vean en la misma posicion qu esta actualemnte."

**Status:** implementado

## Contexto

Después de corregir el bug real de [[57]] (CSS nunca recompilado en el
deploy), desktop volvió exactamente a como estaba ANTES de [[54]] — pero
el cliente, viendo ambas versiones, pidió que desktop TAMBIÉN reciba el
mismo tratamiento visual de mobile (tamaño + ficha resaltada), sin mover
nada de posición (sigue en una sola fila, mismo lugar).

## Implementación

En ambos archivos (`customer/verify.html`, `customer/paquetes.html`) se
quitan los overrides `lg:bg-transparent lg:border-0 lg:py-2 lg:text-sm`
que restauraban el tamaño/look ORIGINAL de desktop — al no tener `lg:` que
los anule, `bg-slate-50 border border-slate-200 px-3 py-3 text-base`
(las mismas clases que ya se usaban en mobile) ahora aplican en las DOS
resoluciones por igual. Se conserva `lg:whitespace-nowrap` (única
diferencia real entre mobile/desktop ahora: en mobile el texto puede
saltar de línea si no cabe, en desktop no).

La POSICIÓN no cambia: el contenedor sigue siendo `lg:flex` (una sola
fila) en el mismo lugar de siempre — solo se tocó el look and feel de los
botones, no el layout del contenedor.

El tab ACTIVO sigue igual que antes (`bg-blue-50 text-blue-800`, sin
fondo/borde de "ficha" — el JS ya se lo quita), así que la distinción
activo/inactivo queda igual de clara en desktop que en mobile.

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- Tailwind recompilado localmente y comiteado (lección de [[57]]: el
  deploy no lo hace solo) — `?v=31` → `?v=32`.
- Suite completa (`tests/data_model tests/web`): 633/633, sin regresiones.
- Pendiente: confirmar en `test.papyrus.com.co` que desktop se ve más
  grande/resaltado en la misma posición, y que mobile sigue exactamente
  como en [[57]] (no se tocó ninguna clase sin `lg:`).
