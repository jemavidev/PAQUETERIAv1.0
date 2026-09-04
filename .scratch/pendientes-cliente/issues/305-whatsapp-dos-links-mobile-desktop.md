# 305 — Enlaces de WhatsApp: 2 links (mobile `wa.me` + desktop `web.whatsapp.com`)

**Pedido original (cliente):** confirmó que `wa.me` sí funciona en su celular (issue 304), pero
no en Chrome de escritorio donde tiene WhatsApp instalado como PWA -- "de que forma puedes dejar
que existan 2 links uno para mobiles y otro para el desktop?"

**Status:** verificado

## Contexto -- por qué hacen falta 2 links (no 1)

Investigación oficial completa en `.scratch/whatsapp-deep-link/investigacion-oficial.md` (2
research previas, Android + Chrome desktop). Resumen: son 2 mecanismos completamente distintos,
ninguno sirve para el otro caso:

- **Mobile (Android/iOS, app nativa):** exige `wa.me`/`api.whatsapp.com` -- el mecanismo oficial
  de Meta ("Click to Chat", App Links/Universal Links). `web.whatsapp.com` nunca lo activa ahí.
- **Desktop con PWA de Chrome instalada:** exige `web.whatsapp.com` -- el "Link Capturing" de
  Chrome (Chrome 139+, automático desde esa versión) solo captura links del MISMO origen exacto
  desde el que se instaló la PWA. `wa.me`/`api.whatsapp.com` son orígenes distintos, nunca lo
  activan, sin importar la configuración.

No existe un dominio único documentado que sirva a los dos casos (confirmado con evidencia
directa: Meta no publicó ningún archivo de asociación cross-origin en `api.whatsapp.com`).

## Solución -- CSS decide, sin JavaScript

Mismo patrón `sm:hidden`/`hidden sm:inline` que ya usa toda la app para separar mobile/desktop
(ej. la tabla de `/residentes`) -- se renderizan LOS 2 `<a>` en el HTML, uno oculto según el
breakpoint. El navegador nunca descarga ni ejecuta el que está oculto, solo no lo muestra.

- `persona_service.py`: nueva función `url_whatsapp_desktop(persona)` -- mismo criterio de
  prioridad que `url_whatsapp` (username > teléfono), pero con `web.whatsapp.com/send?phone=`
  para el camino de teléfono. Con username no hay equivalente en `web.whatsapp.com` -- se queda en
  `wa.me/<user>` en los dos casos (mobile y desktop), único mecanismo que existe para eso.
- `packages.py`: `_whatsapp_url_destinatario` gana el parámetro `desktop=False`; nuevo helper
  `_con_texto_whatsapp` que agrega `?text=`/`&text=` según si la URL base ya trae su propio `?`
  (mismo bug que ya pisamos una vez en issue 301 -- ahora centralizado en una función, no un
  cálculo repetido). `_listar` computa `p.whatsapp_url_destinatario_desktop` junto al de siempre.
- Templates (`packages/_acciones.html`, `customers_manage/_resultados.html` x3): cada `<a>` de
  WhatsApp que cubre el caso teléfono se duplica en par mobile/desktop. Los 2 casos gateados a
  SOLO username (`packages/_resultados.html` x2) no se tocaron -- el link ahí es idéntico en
  ambos dispositivos, duplicarlo no sumaría nada.
- `base.html` footer: no hizo falta duplicar nada -- `.footer-nav-mobile`/`.footer-nav-desktop`
  YA eran 2 bloques separados por CSS propio (preexistente, sin relación con Tailwind) -- solo se
  cambió el dominio del `<nav class="footer-nav-desktop">` a `web.whatsapp.com`.
- Cuidado real con Tailwind: `accion_icono_base`/`chip_icono` ya traían un `flex`/`inline-flex`
  sin prefijo horneado -- agregar `hidden` sin prefijo al lado de eso es ambiguo (el orden de
  las reglas ya compiladas por Tailwind decide, no el HTML). Se usa `|replace(...)` para
  sustituir ese `flex`/`inline-flex` por `hidden sm:flex`/`hidden sm:inline-flex` en vez de
  apilar utilidades en conflicto -- mismo criterio que ya explica el comentario de `tam` en
  `chip_icono` (`components/_badge.html`).

**Trade-off aceptado, explícito con el cliente antes de implementar:** un escritorio SIN la PWA
instalada recibe `web.whatsapp.com`, que ya sabemos (issue 304) se comporta peor que `wa.me` como
respaldo. Se acepta porque el público de escritorio es sobre todo staff (grupo chico, puede
instalar la PWA una vez), mientras que residentes -- la mayoría -- usan celular, ya cubierto.

## Verificación

- Suites (`test_persona_service.py`, `test_layout.py`, `test_customers_manage.py`,
  `test_packages.py`): **418 passed**. Tests nuevos para `url_whatsapp_desktop` (username/
  teléfono), el footer desktop, y la variante desktop en los 3 escenarios de `/paquetes` que ya
  cubrían el camino de teléfono.
- Tailwind reconstruido (`npm run build:css`).
- Verificado en vivo (dev local, sesión real de staff): `/residentes` muestra AMBOS links para el
  residente solo-teléfono (`wa.me/573008103849` y `web.whatsapp.com/send?phone=573008103849`);
  los residentes con username siguen solo en `wa.me/<user>`.

Desplegado a `test.papyrus.com.co` 2026-09-03 (CI `jemavidev/PaqueteX` run 33826552096, tests +
deploy success) y confirmado en vivo: el footer público (`/anunciar`) ya sirve los 2 links --
`wa.me/573334004007` y `web.whatsapp.com/send?phone=573334004007`. Pendiente: que el cliente
confirme en su propio escritorio con la PWA instalada que ahora sí abre la ventana de la app.
