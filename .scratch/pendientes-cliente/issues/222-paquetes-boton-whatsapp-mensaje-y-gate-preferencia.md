# 222 — `/paquetes`: mensaje pre-cargado del botón WhatsApp + gate por preferencia

**Pedido original (cliente):** "en la vista de /paquetes tengo un botón de
whatsapp de notificación y al presionarlo necesito que diga lo siguiente
'Hola *&lt;NombreResidente&gt;*, tu paquete con código
*&lt;CodigoDeAcceso&gt;* está *&lt;EstadoDelPaquete&gt;*. Consulta más
detalles aquí: https://test.papyrus.com.co/consultar?q=&lt;CodigoDeAcceso&gt;',
pero quiero que este botón de notificaciones esté activo o no dependiendo
de las preferencias de notificaciones de un usuario [...] las que sí están
permitidas dejarían el botón habilitado y las que no dejarían el botón en
gris e inactivo [...] pruebas con 'darrazola' y '+573008103849'."
(motivación original de [[221-mis-datos-notificaciones-activar-whatsapp]]).

**Status:** implementado

## Implementación

- `packages.py`: `_mensaje_whatsapp(paquete)` arma el texto exacto pedido
  (negrilla `*texto*`, nombre/código/estado/link) y se agrega como `?text=`
  al link `wa.me` ya existente (`_whatsapp_url_destinatario`, sin tocar). El
  link usa `public_base_url_relaxed()` (ver abajo).
- `_whatsapp_notificacion_permitida`: gate por la preferencia real de la
  Persona destino (WhatsApp × estado actual del paquete, la misma matriz de
  `/mis-datos`) -- batch (`preferencia_notificacion_service.preferencias_
  activas_por_persona`, una query para TODA la página) para no reintroducir
  el N+1 que ya vigila `test_lista_no_dispara_una_query_de_persona_o_
  usuario_por_paquete` (umbral 14 -> 15, +1 query fija).
- `_acciones.html`: 3 estados del ícono -- activo (link+mensaje), gris
  "notificaciones desactivadas" (hay contacto, preferencia apagada), gris
  "sin teléfono registrado" (sin contacto, como antes).

**Base para SMS/Email/WhatsApp automáticos** (pedido explícito del
cliente, extendido más allá del botón manual):
- `notificacion_service.py`: `PLANTILLAS_DEFAULT` (los 4 eventos, canal
  compartido SMS/Email/WhatsApp) unificado a la misma estructura
  (nombre/código/estado/link), sin la negrilla de WhatsApp (no significa
  nada en SMS/Email). Nuevas variables `{estado}`/`{link}` en
  `_variables`/`variables_ejemplo`, disponibles también para plantillas
  personalizadas vía `/administracion/notificaciones`.
- `base_url` se encadena como parámetro (nunca importado directo, el
  dominio no depende de la capa web -- mismo patrón que
  `plantilla_email_html.envolver_html`) por `construir_mensaje` →
  `preparar_notificacion` → `notificar_evento`/`mensaje_de_prueba`, resuelto
  en cada ruta web (`announce.py`, `announce_new.py`, `packages.py`,
  `admin.py`) vía `public_base_url_relaxed()` -- **nueva** variante de
  `public_base_url()` que nunca lanza (issue real encontrado: la versión
  estricta original rompía `/paquetes/{id}/recibir` con 500 en staging sin
  `PUBLIC_BASE_URL`, violando el criterio "best-effort" que ya regía el
  envío de notificaciones).

**Bug real corregido de paso**: `_variables` usaba `paquete.estado` (el
estado YA persistido) en vez del parámetro `evento` que se está
notificando -- normalmente coinciden, pero `construir_mensaje` puede
llamarse para un evento antes de que el Paquete transicione (tests, o
cualquier caller que arme el texto por adelantado). Corregido a usar
`evento` explícitamente.

**Tests**: ~15 archivos con aserciones sobre el texto default viejo
("portería"/"entregado"/"Anunciaste un paquete"/hrefs `wa.me` exactos)
actualizados al nuevo texto/estructura; `test_llamada_y_whatsapp_no_se_
pueden_activar` (asumía WhatsApp bloqueado, previo a
[[221-mis-datos-notificaciones-activar-whatsapp]]) dividido en
`test_llamada_no_se_puede_activar` + `test_whatsapp_si_se_puede_activar`.
1198+ tests pasan (`tests/web/`, `tests/data_model/`).

