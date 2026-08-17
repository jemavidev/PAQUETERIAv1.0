# 110 — Fuente Roboto en la vista /paquetes

**Pedido original (cliente):**
"puedes cambiar la fuente de esta vista a Roboto?"

**Status:** implementado

## Contexto

Toda la app (base.html + tailwind.css) usa la pila `font-sans` por
defecto de Tailwind (`ui-sans-serif, system-ui, -apple-system, "Segoe
UI", Roboto, ...` -- Roboto ya aparecía ahí como fallback, pero solo se
pintaba de verdad en sistemas sin las fuentes anteriores instaladas, casi
nunca en la práctica). El pedido es por Roboto real, garantizado, no un
fallback de suerte.

Alcance: SOLO `/paquetes` ("esta vista", pedido explícito) -- no toda la
app. `base.html` es compartido por todas las pantallas (públicas y de
cliente incluidas); cambiar la fuente ahí afectaría vistas que nadie pidió
tocar. El header/footer compartidos (`site-header`/`site-footer-mobile`,
viven en `base.html`, fuera del `{% block content %}`) se quedan con su
fuente actual -- son chrome global de la app, no parte de esta vista
puntual.

## Implementación

- `packages/list.html`: nuevo `{% block head %}` (el slot que `base.html`
  ya expone antes de `</head>`, sin tocar `base.html`) con `<link>` a
  Google Fonts (Roboto, pesos 400/500/700/900 -- los reales que ofrece la
  familia; Tailwind usa también 600/semibold y 800/extrabold en esta
  vista, el navegador los aproxima al peso cargado más cercano, límite
  normal de Roboto, no un bug).
- Todo el contenido de `{% block content %}` (grid de paquetes + modal
  "Recibir") se envuelve en un solo `<div id="vista-paquetes">`, con
  `font-family: 'Roboto', ...` en el mismo `head` block -- hereda a toda
  la vista (tabla, modales "Ver"/"Corregir"/"Recibir"/"Promover", chips,
  botones) sin tocar el header/footer, que quedan fuera del div. Los
  elementos con `font-mono` (código de acceso) no se ven afectados --
  declaración directa en el propio elemento le gana a la heredada del
  contenedor.

## Verificación

- Playwright contra el servidor local real: `getComputedStyle` sobre el
  título "Paquetes" y sobre una fila de la tabla confirma
  `font-family` empieza con "Roboto"; el header (`.site-header`) se
  queda con `system-ui` (sin cambios, confirmado que NO se contagió).
- Suite completa: ver commit para el conteo final (cambio puramente de
  presentación, sin lógica nueva -- no se esperan tests nuevos).
- Pendiente: deploy a test.papyrus.com.co.
