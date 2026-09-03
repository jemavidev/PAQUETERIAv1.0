# 295 — Quitar "Notificaciones"/"Proveedores" duplicados de `.site-nav` (staff admin)

**Pedido original:**
"ya 'Notificaciones y Proveedores' existen en la clase 'site-actions', lo
que necesito es que los remuevas de 'site-brand-group'"

**Status:** implementado

## Contexto — revierte parte de [[190]]

`base.html` mostraba "Notificaciones" y "Proveedores" en dos lugares para
ADMIN: como tab visible en `.site-nav` (dentro de `.site-brand-group`) y
como ítem del menú de cuenta (`.site-actions`, `bloque_staff`).

- "Notificaciones" se promovió a tab visible por pedido explícito del
  cliente en [[190]] ("sin quitarlo del menú de cuenta" -- la duplicación
  fue intencional en ese momento).
- "Proveedores" se agregó siguiendo el mismo patrón al construir
  `/administracion/proveedores` (commit `1941f38`, ticket 03), sin un
  pedido de tab dedicado.

Este issue revierte la duplicación: ambos enlaces quedan únicamente en el
menú de cuenta (`.site-actions`), no en el nav de escritorio.

## Implementación

`base.html` -- se retira el bloque `{% if es_admin %}` que agregaba
`enlace_nav('/administracion/notificaciones', ...)` y
`enlace_nav('/administracion/proveedores', ...)` dentro del `<nav
class="site-nav">` de staff. `es_admin` se sigue calculando y usando para
el menú de cuenta (`bloque_staff`), sin cambios ahí.

## Verificación

- `tests/web/test_layout.py`: los 2 tests que afirmaban la presencia de
  "Notificaciones" como tab visible (issue 190) se reemplazan por
  `test_staff_admin_no_duplica_notificaciones_ni_proveedores_en_el_tab_del_header`
  -- confirma que ADMIN ya NO ve ninguno de los dos en `.site-nav`, pero sí
  los sigue viendo en algún lugar de la página (el menú de cuenta).
- Suite `tests/web/test_layout.py`: 27 tests, todos pasan.
- Pendiente: deploy a test.papyrus.com.co.
