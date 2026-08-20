# 138 — Reemplazar el literal "None" por "N/D" cuando un campo no tiene dato (solo front)

**Pedido original (cliente):**
"Vamos a actualizar el comentario de 'None' para cuando no ten[ga]
especifico en cualquiera de los campos de la base de datos, la idea es
que todo se vea mejor, remplaza donde aparezca 'None' --> 'N/D'"

Aclaración inmediata del cliente, restricción dura: "logico, solo para
el front no para la logica del sistema" — el fix es solo de
presentación (plantillas), nunca toca cómo el dominio/backend maneja
`None`/`NULL`.

**Status:** implementado

## Investigación

En vez de auditar a ojo cada `{{ }}` de Jinja (impreciso: depende de qué
campos están realmente vacíos y qué plantillas se ejercitan en la
práctica), se sembraron datos reales con campos nulos deliberados
(paquete sin guía/sin teléfono, Persona solo-WhatsApp sin Teléfono) y se
corrió un crawl automatizado con Playwright sobre las vistas de staff y
cliente, buscando el literal "None" completo (regex de palabra completa,
evita falsos positivos de CSS/JS) en el HTML renderizado.

Encontrado: **`/residentes` (customers_manage/search.html)** — única
fuente real de la fuga, dos manifestaciones del mismo caso (Persona sin
Teléfono, solo con `whatsapp_usuario` — estado válido desde ADR-0007,
no un dato faltante por error):

1. Línea 66 — columna Teléfono: `{{ p.telefono }}` sin guard, imprimía
   el literal `None` como texto.
2. Líneas 76-78 — ícono "Llamar": `url_llamada(p)` (helper de dominio,
   `persona_service.py`) arma `f"tel:{persona.telefono}"` sin validar
   `None` → enlace roto `href="tel:None"`.

`url_llamada`/`url_whatsapp` viven en `persona_service.py` (capa de
dominio) pero son helpers puramente de formato de link para las
plantillas — no participan de ninguna decisión de negocio. Se
confirmó que `url_whatsapp` nunca puede fallar así: el modelo `Persona`
tiene un `CheckConstraint` a nivel de base de datos
(`ck_personas_telefono_o_whatsapp`) que garantiza que Teléfono o
WhatsApp SIEMPRE está presente — pero no cuál de los dos, así que
`url_llamada` sí puede recibir un `telefono` nulo legítimamente.

Barrido más amplio tras el primer fix, sin encontrar más fugas en ese
momento: `/paquetes` (lista + 3 modales "Ver" con guía/teléfono/torre
nulos), `/residentes/{id}` (ficha), `/consultar` (3 códigos),
`/administracion/personal`, `/administracion/notificaciones`,
`/administracion/conjunto`, `/paquetes/promover-candidatos` — todos
limpios.

**Segunda fuga, reportada en vivo por el cliente** ("sigue apareciendo
NONE" en `/consultar?q=6S4B"): los 3 códigos usados en el primer barrido
tenían `recipient_phone` con dato — ninguno ejercitaba el caso borde de
`/consultar` con AMBOS teléfonos vacíos. `6S4B` sí lo tiene
(`recipient_phone=None`, `announced_by_phone=None`), y reveló un
segundo punto sin guard:

3. `search/form.html:50` — fila Teléfono del resultado de `/consultar`:
   `{{ fila_dato('Teléfono', paquete.recipient_phone or
   paquete.announced_by_phone) }}` sin fallback — si ambos son `None`
   (anunciante solo-WhatsApp, sin Teléfono propio ni del destinatario,
   caso legítimo por ADR-0007), el macro `fila_dato` (`_confirmacion.
   html`) imprime `{{ valor }}` tal cual, sin guard propio.

Fix: `... or paquete.announced_by_phone or 'N/D'`.

## Implementación (solo `customers_manage/search.html`, sin tocar dominio)

- Línea 66: `{{ p.telefono }}` → `{{ p.telefono or 'N/D' }}`.
- Ícono "Llamar" (líneas 76-78): envuelto en `{% if p.telefono %}` —
  con teléfono arma el link de siempre; sin teléfono cae a un `<span>`
  inactivo (`text-slate-300`, `title="Sin teléfono registrado"`), mismo
  patrón ya establecido en `packages/_acciones.html` (issue 136) para
  íconos sin dato disponible. El ícono de WhatsApp no necesitó guard:
  por el `CheckConstraint` de arriba, si no hay Teléfono siempre hay
  `whatsapp_usuario`, así que `url_whatsapp(p)` nunca queda sin destino.
- **`persona_service.py` NO se tocó** — la restricción del cliente fue
  explícita.
- `search/form.html:50`: `paquete.recipient_phone or
  paquete.announced_by_phone or 'N/D'` — mismo criterio (front-only,
  sin tocar `paquete_service.py` ni el resto del dominio).

## Verificación

- Nuevo test `tests/web/test_customers_manage.py::
  test_tabla_de_residentes_sin_telefono_no_filtra_none` — Persona
  creada vía `get_or_create_persona_por_whatsapp` (sin Teléfono real,
  mismo estado que produjo el bug) — confirma ausencia de `tel:None` y
  de `>None<`, presencia de `N/D` y de "Sin teléfono registrado".
  `tests/web/test_customers_manage.py`: 92 passed.
- Nuevo test `tests/web/test_search.py::
  test_sin_telefono_alguno_muestra_nd_no_none` — anuncio con
  `anunciante_whatsapp` (sin Teléfono) para sí mismo, ambos campos de
  teléfono quedan `None` -- confirma ausencia de "None" y presencia de
  "N/D" en `/consultar`. `tests/web/test_search.py`: 24 passed.
- Verificado en vivo contra `localhost:8010` con el código real
  `6S4B` (el mismo que el cliente reportó) -- confirmado limpio tras
  el fix, con curl directo y con el crawl Playwright.
- Re-corrida del crawl completo (Playwright) contra el servidor local
  tras ambos fixes: las 8 vistas antes revisadas siguen limpias.
- Suite completa: pendiente de confirmar tras el segundo fix (corriendo).
- Pendiente: deploy a test.papyrus.com.co.
