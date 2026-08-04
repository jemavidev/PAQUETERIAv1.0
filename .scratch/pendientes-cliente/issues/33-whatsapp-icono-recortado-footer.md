# 33 — Ícono de WhatsApp recortado en el footer (mobile Y desktop)

**Pedido original (cliente):** "el icono de whatsapp en este momento se ve
de lo mejor en versiones que me has presentado, pero no necesariamente
está bien... el icono de whatsapp tiene una pequeña punta en la parte
izquierda inferior, en este proyecto esa punta NO SALE, no se ve, por eso
digo que algo está mal pero no sé qué es, posiblemente estés redondeando
el icono y recortando alrededor de este y por eso no se vea." También
preguntó si el problema podía ser la altura de la barra de footer en
desktop "comiéndose" los íconos.

**Status:** verificado

## Diagnóstico

NO es la altura de la barra (por eso el cliente ya notaba que pasaba
igual en mobile, con barra mucho más alta, y en desktop) — el culpable es
CSS a nivel de cada ícono individual, independiente del contenedor:

`.site-footer-mobile nav a svg` tiene `border-radius:50%` (para pintar el
círculo de fondo del ícono ACTIVO). Los elementos `<svg>` traen
`overflow:hidden` por defecto del user-agent — al combinarse con
`border-radius:50%` en el MISMO elemento, el navegador recorta el
contenido pintado del SVG a un CÍRCULO inscrito en su caja de 24x24, no
solo a un cuadrado. El logo de WhatsApp (path oficial, ya en viewBox
24x24 correcto desde el ticket de "más redondo") tiene su "colita"
distintiva apuntando justo hacia la esquina inferior izquierda de su
propio bounding box — exactamente la zona que el círculo inscrito recorta.
Los demás íconos del footer no lo evidencian porque sus siluetas no
llegan tan cerca de las esquinas, pero TODOS estaban sufriendo el mismo
recorte circular silencioso (el `border-radius` se aplica siempre, esté o
no activo el ícono — solo el `background` cambia con `aria-current`).

## Qué se hizo

`base.html`, macro `enlace_nav_footer`: el `<svg>` ahora vive envuelto en
un `<span class="footer-nav-icon">` propio. El `border-radius`/
`padding`/`background` (el círculo de resaltado del ítem activo) se
movieron a ese `<span>` (un elemento normal, sin `overflow:hidden`
implícito, así que el radio ya no recorta nada). El `<svg>` se queda solo
con `width:24px; height:24px` — igual que el patrón ya usado en
`.site-nav svg` del header, que nunca tuvo este bug porque nunca tuvo
`border-radius`.

Selectores actualizados: `.site-footer-mobile nav a svg` (split en
`.footer-nav-icon` + `svg` puro), `.site-footer-mobile nav
a[aria-current="page"] svg` → ahora apunta a `.footer-nav-icon`. El
override de color más claro para "Anunciar" activo se queda intacto
sobre `svg` (es `color`/`fill`, no clipping).

Aplica a los 3 contextos que comparten esta regla (mobile, desktop, y
cualquier audiencia) porque todos pasan por el mismo macro/CSS
compartido — no hace falta tocar nada por audiencia.

## Verificación

- [x] Confirmado visualmente (screenshot Playwright de test.papyrus.com.co
      tras el deploy) que la punta de WhatsApp se ve completa en mobile Y
      desktop.
- [x] El círculo de resaltado del ítem activo ("Consultar") se ve igual
      que antes del cambio.
