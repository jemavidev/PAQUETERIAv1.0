# 181 — Header con ancho inestable según scrollbar (seguimiento a [[179]]/[[180]])

**Pedido original:** seguimiento a [[180]] -- "veo que ya lo cambiaste, pero sigue el problema...
la de /paquetes sigue teniendo el mismo comportamiento de nota a simple vista que no es lo mismo,
analiza ondo y dime cuando lo encuentres" → mid-turn: "al parecer parece el ancho o de una vista o
de la otra" y "pero creo que esta en el header".

**Status:** implementado

## Diagnóstico

Con las 2 pistas combinadas (ancho + header), y ya descartado el `<header>` en sí (byte-idéntico
entre vistas, confirmado con `diff` en [[180]]) y la tipografía (ya quitada en [[180]]), quedaba
un candidato real: **`.site-header` es `position: sticky` y ocupa el 100% del ancho disponible del
`<body>`** -- ese ancho disponible varía según si la página dispara scrollbar vertical o no (la
barra le resta ~15-17px al ancho real en la mayoría de navegadores/SO, excepto macOS con overlay
scrollbar). `base.html` no tenía ningún reset que reservara ese espacio de forma constante --
`/paquetes` (más filas, modales completos por fila) dispara scrollbar más seguido que
`/residentes`, así que el header (centrado a 1280px vía `.site-header-inner`) se corre unos
pixeles según cuál vista tenga scrollbar en ese momento. Explica por qué se sentía "distinto a
simple vista" sin que ninguna clase Tailwind ni el HTML del header cambiara -- es un efecto de
layout del navegador, no del markup.

## Cambio

- `base.html`: `html { overflow-y: scroll; scrollbar-gutter: stable; }` -- reserva el espacio de
  la barra de scroll SIEMPRE, tenga o no la página contenido para scrollear. `overflow-y: scroll`
  (soporte universal) + `scrollbar-gutter: stable` (equivalente moderno) a la vez, por
  compatibilidad. Con esto el ancho disponible del header (y de todo el layout centrado) queda
  exactamente igual en cualquier página del sitio, no solo /paquetes vs /residentes.

## Verificación

- Suite completa de `tests/web/` (cambio global en `base.html`, se corrió más ancho que el par de
  archivos habitual por tocar el layout compartido): **637/637**.
- Verificado en local (`localhost:8010`): la regla aparece en el `<head>` de ambas vistas.
- Pendiente: verificar visualmente en un browser real (sin acceso a uno en este entorno) y en
  test.papyrus.com.co tras deploy -- confirmar que el header ya no se percibe "corrido" al
  alternar entre vistas con distinta cantidad de contenido.
