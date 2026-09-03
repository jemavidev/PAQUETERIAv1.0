# 301 — Enlaces de WhatsApp: `web.whatsapp.com/send` en vez de `wa.me`, sin `target="_blank"`

**Pedido original (cliente):** documento de especificación técnica completo
("Integración de Enlaces Directos a la App de WhatsApp (Chrome PWA)") pidiendo
que todo enlace de WhatsApp use `https://web.whatsapp.com/send?phone=...&text=...`
(nunca `wa.me`/`api.whatsapp.com`) y nunca `target="_blank"` -- para que la PWA
de WhatsApp instalada en Chrome capture la navegación en vez de abrir una
pestaña del navegador con la web intermedia.

**Status:** verificado

## Conflicto real encontrado (antes de implementar)

`Persona.whatsapp_usuario` NO es un teléfono -- es el username real de
WhatsApp (Meta, rollout 2026, `persona_service.WHATSAPP_USUARIO_RE`: 3-35
caracteres, letras/números/punto/guion bajo, ej. `jesus.villalobos`).
`web.whatsapp.com/send?phone=` exige un número E.164 real; no tiene forma de
abrir un chat por username. Aplicar el cambio a ciegas habría roto el
contacto de cualquier Persona que solo tiene `whatsapp_usuario` (sin
teléfono propio -- caso real ya cubierto por [[104]]/[[113]], "solo-WhatsApp").

**Resolución:** el dominio se elige según qué dato se usa, no incondicional:

- Username de WhatsApp (`persona.whatsapp_usuario`) → sigue en `wa.me/<user>`
  (único mecanismo que Meta ofrece para username, ver docstring de
  `url_whatsapp`).
- Teléfono (`persona.telefono`, `recipient_phone`, `numero_whatsapp` del
  footer) → pasa a `web.whatsapp.com/send?phone=<dígitos>`.

## Cambios

- `persona_service.py::url_whatsapp` -- domain-aware según arriba; el
  camino de teléfono limpia con `re.sub(r"\D", "", ...)` (más robusto que el
  `.lstrip('+')` anterior).
- `packages.py::_whatsapp_url_destinatario` -- mismo criterio en el fallback
  de teléfono crudo (`recipient_phone` sin Persona resuelta).
- `packages.py` línea del mensaje pre-cargado (`?text=` tras `_base_whatsapp`)
  -- corregido para usar `&text=` cuando la URL base ya trae `?phone=` (antes
  asumía siempre `wa.me/<x>` sin `?` propio; con el nuevo dominio de teléfono
  eso rompería el link, `?phone=X?text=Y` no es válido).
- `base.html` footer (`numero_whatsapp`, 3 ocurrencias) -- mismo cambio de
  dominio (siempre es un teléfono real, el de soporte).
- `target="_blank" rel="noopener noreferrer"` retirado de los 6 `<a>` de
  WhatsApp del código (`packages/_acciones.html`, `packages/_resultados.html`
  x2, `customers_manage/_resultados.html` x3) -- `rel` se retira junto con
  `target` porque no tiene efecto sin él.

**Fuera de alcance (a propósito):** el documento asume mensaje pre-cargado en
TODOS los enlaces, pero hoy solo el botón de Acciones de `/paquetes` arma uno
(`_mensaje_whatsapp`) -- `/residentes` y el footer abren el chat vacío, sin
`?text=`. Generalizar el mensaje a esos enlaces es una decisión de contenido
aparte (qué texto tendría sentido sin contexto de paquete), no incluida acá.

## Verificación

- Suites relevantes (`test_persona_service.py`, `test_layout.py`,
  `test_customers_manage.py`, `test_packages.py`): **415 passed**. 3 fallos
  reales en el camino, no bugs -- las aserciones nuevas esperaban `&text=`
  literal, pero Jinja autoescapa `&` a `&amp;` dentro de un atributo `href`
  (HTML válido, el navegador lo interpreta igual) -- corregidas las 3
  aserciones, no el código.
- Verificado en vivo contra dev local (curl con sesión real de staff):
  - `/residentes`: usuarios con `whatsapp_usuario` siguen en
    `wa.me/<user>` (ej. `wa.me/jesusmariavillalobos`); el único residente
    solo-teléfono ya resuelve a `web.whatsapp.com/send?phone=573008103849`.
  - `/paquetes`: mensaje pre-cargado (`?text=Hola *NOMBRE*...`) sigue
    intacto en el link de username.
  - Cero ocurrencias de `target="_blank"` en enlaces de WhatsApp de
    `/paquetes` y `/residentes`.

Desplegado a `test.papyrus.com.co` 2026-09-03 (CI `jemavidev/PaqueteX` run
33810514014, tests + deploy success) y confirmado en vivo: el enlace público
del footer (`/anunciar`) ya resuelve a `web.whatsapp.com/send?phone=...`.

**Nota (seguimiento [[304]]):** el cliente reportó en vivo, ya desplegado,
que `web.whatsapp.com` no abría la app en ningún dispositivo probado (ni
Android nativo, ni Chrome de escritorio sin la configuración manual de 3
pasos) -- la premisa del documento original resultó ser la inversa de la
realidad. El dominio del camino de teléfono se revirtió a `wa.me` en [[304]];
el resto de este issue (`target="_blank"` retirado, dominio de username sin
tocar) sigue vigente sin cambios.
