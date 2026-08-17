# 94 — Modal "Ver": teléfono debajo del título, se retira la sección "Destinatario"

**Pedido original (cliente):**
"ahora en la vista de /paquetes, el modal de clientes, quiero que en la
parte superior, justo debajo del id 'modal-ver-<id>-titulo'... coloques el
numero de telefono de la persona que anuncio, este numero ya se encuentra
en la seccion con clase 'rounded-xl bg-blue-50 border border-blue-100 p-3
mb-3' llamada 'Destinatario'. al finalizar si todo sale bien, quiero que
remuevas de este modal esta seccion... todo esto enfocado a optimizar el
tamano y espacio para mostrar informacion en este modal."

**Status:** implementado

## Implementación

- `packages/_resultados.html`, modal "Ver": nueva línea justo debajo del
  título (`<h2 id="modal-ver-<id>-titulo">`), con el mismo teléfono y la
  misma cadena de fallback que antes vivía en el campo "Anuncio" de
  "Destinatario" -- teléfono propio del destinatario si lo tiene, si no el
  del Anunciante, si no su WhatsApp (`announce()` garantiza que uno de los
  dos exista, así que la línea nunca queda vacía).
- Implementado en dos pasos, verificando en vivo entre uno y otro (pedido
  explícito): primero se agregó la línea nueva CON la sección
  "Destinatario" todavía presente (para confirmar visualmente que el dato y
  el fallback quedaban correctos), luego se retiró la sección completa
  (`rounded-xl bg-blue-50 border border-blue-100 p-3 mb-3` -- "Nombre" +
  "Anuncio"). El campo "Nombre" no se perdió: el nombre ya vive en el
  título del modal (issue 91).

## Verificación

- `tests/web/test_packages.py`: 3 tests reescritos (antes afirmaban el chip
  "Anuncio" dentro de "Destinatario"; ahora afirman que el teléfono aparece
  DESPUÉS del `id` del título en el HTML, y que "Destinatario" ya no
  aparece en el modal) -- 97 tests, todos pasan.
- Playwright contra el servidor local real, screenshot antes y después de
  retirar la sección: el teléfono queda visible justo bajo el título, la
  tarjeta azul de "Destinatario" desaparece, el modal queda notablemente
  más compacto.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
