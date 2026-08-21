# 153 — `/paquetes` modal "Ver": nombre y código del título, cada uno con su propio link

**Pedido original:** "Para la vista /paquetes en el modal de 'Cliente' por ejemplo aparece este
'JESUS VILLALOBOS - QK5P' quiero que para el nombre y el codigo se generen 2 links (JESUS
VILLALOBOS --> /residentes<residente seleccionado> y QK5P --> /consultar?q=QK5P)".

**Status:** verificado

## Decisiones

- El nombre enlaza a `/residentes/<id>` **solo si se resuelve una Persona real** detrás del
  destinatario -- reusa `persona_destino`, ya resuelto en `packages.py` para el ícono de
  WhatsApp del mismo modal (mismo criterio teléfono→nombre, `_personas_por_telefono`/
  `_personas_por_nombre`; cero consultas nuevas). Sin match (ej. `Destinatario.solo_nombre` sin
  ninguna Persona con ese teléfono/nombre), el nombre se queda como texto plano -- no hay a
  dónde enlazarlo, y forzar un link roto sería peor que no tener link.
- El código de acceso enlaza SIEMPRE a `/consultar?q=`, mismo criterio ya usado en la columna
  Cliente de la lista y en el toast de éxito de `/announce`.
- `Markup.format()` para construir el título con HTML seguro (no `~` + `|safe`): mismo patrón ya
  usado en `announce_new/form.html` -- el literal queda tal cual, cada `{}` sustituido
  (`recipient_name`, `access_code`, ambos texto no confiable) se escapa automáticamente.

## Verificación

- `tests/web/test_packages.py::test_modal_ver_titulo_enlaza_nombre_a_residentes_y_codigo_a_consultar`
  (nuevo): Persona resuelta -- nombre enlaza a `/residentes/<id>`, código a `/consultar?q=`.
- `tests/web/test_packages.py::test_modal_ver_titulo_sin_persona_resuelta_nombre_queda_como_texto`
  (nuevo): `Destinatario.solo_nombre` sin match -- nombre queda como texto plano, código sigue
  enlazando.
- Suite `/paquetes`: 171/171.
- Render real contra `localhost:8010`: título del modal "Ver" con los 2 `<a href>` exactos.
