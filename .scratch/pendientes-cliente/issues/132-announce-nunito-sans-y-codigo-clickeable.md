# 132 — `/announce`: fuente Nunito Sans + código de acceso clickeable

**Pedido original (cliente):**
De las 3 posibilidades presentadas para `/announce`, eligió "b y c":
- **B.** Extender la fuente Nunito Sans (issue 110/112) a `/announce`.
- **C.** Código de acceso clickeable en el toast de éxito, hacia
  `/consultar`.

**Status:** implementado

## Implementación

- **B**: `announce_new/form.html` gana `{% block head %}` idéntico al
  de `packages/list.html` (Google Fonts preconnect + `<link>`,
  `<style>#vista-announce{font-family:'Nunito Sans',...}`). Todo el
  `{% block content %}` (card del campo único + modal "Recibir" cuando
  aplica) se envuelve en `<div id="vista-announce">`.
- **C**: el toast de éxito ("Anunciado para X — código Y.") pasa el
  código como `<a href="/consultar?q=...">` -- chip inline compacto
  (`font-mono font-bold bg-slate-100 hover:bg-slate-200 rounded`, sin
  ícono, a diferencia de `/mis-paquetes`/columna Cliente de
  `/paquetes`, que sí llevan ícono/fondo por Estado -- acá vive DENTRO
  de una oración corrida, no en un panel ni una columna).

## Bug real encontrado y corregido

Primer intento del toast usaba `('texto ' ~ recipient_name|e ~
'<a>...</a>')|safe` -- Jinja NO respeta el `Markup` de cada pedazo
concatenado con `~` de forma consistente (confirmado con un repro
mínimo: `('a ' ~ x|e ~ '<b>')|safe` sigue escapando el `<b>` literal).
Reescrito con el patrón correcto de `markupsafe`:
`('template con {}'|safe).format(valor)` -- el template literal
(autoría nuestra) queda intacto, y cada `{}` sustituido se auto-escapa,
así que `recipient_name` (nombre tecleado por el staff, no confiable)
nunca puede inyectar HTML.

## Verificación

- `tests/web/test_announce_new.py`: 2 tests nuevos --
  `test_toast_de_confirmacion_incluye_codigo_clickeable_a_consultar`
  (href + texto del link) y
  `test_toast_de_confirmacion_escapa_el_nombre_del_destinatario`
  (nombre con `<b>`/`&` no se cuela como HTML real, aparece escapado
  -- confirmado que además sube a mayúsculas, mismo criterio
  server-side de siempre). 68 passed.
- Tailwind: rebuild + `?v=` de 49 a 50.
- Playwright contra el servidor local real: `font-family` del `<h1>`
  confirmado "Nunito Sans, ...", `href`/texto del link del toast
  confirmados con un anuncio real.
- Suite completa: 1018 passed.
- Pendiente: deploy a test.papyrus.com.co.
