# 103 — Ícono de WhatsApp en Acciones prioriza el username sobre el teléfono

**Pedido original (cliente):**
"Necesito que actualices algo, el icono de whatsapp en la vista
'/paquetes' deberia estar enfocado al nombre de usuario de whatsapp antes
que el numero de telefono, en caso que no tenga usuario de whatsapp,
entonces se deberia usar el numero de telefono, dime si puedes corregir
esto, aqui y en cualquier otro lugar donde se utilice el enlace de
whatsapp."

**Status:** implementado

## Implementación

Revisados todos los lugares donde se arma un link de WhatsApp
(`grep wa.me\|url_whatsapp` en `templates/`): la mayoría YA usaba
`persona_service.url_whatsapp` (que ya prioriza `whatsapp_usuario` sobre
`telefono` desde issue 67) -- modal "Ver" (línea de teléfono bajo el
título, "Residentes de la unidad") y `/residentes` ya estaban bien. El
footer (`base.html`) usa un número de WhatsApp de soporte de Papyrus, sin
relación con ninguna Persona -- fuera de alcance.

El único lugar roto: la columna **Acciones de `/paquetes`**
(`_acciones.html`) armaba el link directo desde `p.recipient_phone` (el
teléfono crudo del snapshot del Paquete), sin pasar por `url_whatsapp` ni
mirar si el destinatario tenía un username registrado.

- `packages.py`: nueva `_personas_por_telefono` (batch, mismo criterio que
  `_personas_por_id`) resuelve la Persona real detrás de
  `recipient_phone` -- sin tocar el snapshot congelado (ADR-0001), es
  una lectura extra solo para enriquecer la vista. Nueva
  `_whatsapp_url_destinatario(paquete, persona)`: si hay Persona
  resuelta, reusa `url_whatsapp` (prioriza username); si no, cae al
  teléfono crudo del snapshot -- mismo criterio de prioridad en los dos
  casos.
- `_acciones.html`: el ícono de WhatsApp usa `p.whatsapp_url_destinatario`
  (precomputado) en vez de armar el link a mano.

## Verificación

- `tests/web/test_packages.py`: 3 tests nuevos (prioriza username cuando
  existe, cae a teléfono sin username, cae a teléfono sin ninguna Persona
  resuelta) + ajustado el umbral del test de N+1 (10 → 11 queries, la
  nueva resolución batch agrega UNA consulta fija por página, no por
  paquete) -- 122 tests, todos pasan.
- Playwright contra el servidor local real: ícono de WhatsApp de un
  destinatario con username registrado confirmado apuntando a
  `https://wa.me/<username>`, no al teléfono.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
