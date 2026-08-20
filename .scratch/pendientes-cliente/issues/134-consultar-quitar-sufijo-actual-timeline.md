# 134 — `/consultar`: quitar el sufijo " • Actual" del timeline

**Pedido original (cliente):**
"para la vista de ejemplo (/consultar?q=3XQV) en el estado actual
(Entregado • Actual) remuevas la parte que dice ( • Actual), solo
deberia aparecer El estado y esa palabra ' • Actual' no deberia
aparecer en ningun estado"

**Status:** implementado

## Contexto

El mismo sufijo ya se había quitado del modal "Ver" de `/paquetes`
([[106]]). `/consultar` (vista pública) seguía agregándolo al paso
vigente del timeline -- ej. el badge decía "Entregado • Actual" en vez
de solo "Entregado".

## Implementación

- `search/form.html`: los 2 call sites de `paso_timeline(...)` armaban
  el segundo argumento (`badge_texto`) como
  `h.titulo ~ ' • Actual' if h.titulo == titulo_actual else h.titulo`
  -- se simplifica a pasar `h.titulo` directo, sin condicional. La
  variable `titulo_actual` (que solo se usaba para esa comparación)
  queda sin uso -- se elimina su `{% set %}`.
- Alcance explícito: NO se tocó `customer/paquetes.html`
  (`/mis-paquetes`), que tiene el mismo patrón -- el pedido fue puntual
  sobre `/consultar`. Si se quiere ahí también, es el mismo cambio en
  otro archivo.

## Verificación

- `tests/web/test_search.py`: nuevo
  `test_timeline_no_muestra_el_sufijo_actual` -- paquete Entregado,
  confirma que "Actual" no aparece en absoluto en la respuesta.
- Playwright contra el servidor local real, con el mismo ejemplo del
  cliente (`/consultar?q=3XQV`): badge dice "ENTREGADO" solo, sin
  sufijo, en los 3 pasos del timeline.
- Suite completa: pendiente de confirmar.
- Pendiente: deploy a test.papyrus.com.co.
