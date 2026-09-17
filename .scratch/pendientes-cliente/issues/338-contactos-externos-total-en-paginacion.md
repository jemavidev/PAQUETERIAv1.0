# 338 — Contactos externos: mostrar cantidad total en la paginación

**Pedido original (cliente):**
"muy bien, necesito que en la paginacion sea posible vicualizar la cantidad
de cobtactos existentes"

**Status:** implementado, verificado en vivo en localhost:8010

## Contexto

`/administracion/contactos-externos` muestra "Página X de Y" en la barra de
paginación (`components/_paginacion.html`, compartida con `/paquetes` y
`/residentes`), pero no la cantidad total de contactos que hay.

`buscar_contactos_externos` (`contacto_externo_service.py`) ya calcula el
total (`total = query.count()`) para derivar `total_paginas`, pero lo
descarta -- solo devuelve `(contactos, total_paginas)`.

## Implementación

- `buscar_contactos_externos` (`contacto_externo_service.py`) pasa a devolver
  `(contactos, total_paginas, total)` en vez de `(contactos, total_paginas)`
  -- el `total` ya se calculaba internamente, solo se descartaba.
- Los 2 call sites en `admin.py` (`_contexto_contactos_externos`, y el
  branch de fetch en vivo dentro de `admin_contactos_externos`) desempacan
  el nuevo valor y lo pasan al contexto como `total_contactos`.
- `_contactos_externos_resultados.html` muestra "`N` contacto(s)" arriba de
  la barra de paginación, FUERA del `{% if total_paginas > 1 %}` interno del
  macro `paginacion()` -- así sigue viéndose aunque haya 20 contactos o
  menos (una sola página, donde el macro no renderiza nada).

## Verificación

- `tests/web/test_admin_contactos_externos.py` (21 tests, 2 nuevos):
  muestra el total con varios contactos, y sigue mostrándolo con 1 solo
  contacto (caso de una sola página).
- Verificado en vivo contra `localhost:8010`: la vista real muestra
  "1041 contactos".
