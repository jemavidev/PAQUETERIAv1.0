# 99 — "+ Nuevo residente": Nombre oculto hasta teclear el contacto

**Pedido original (cliente):**
"se ve bien, pero necesito el nombre este escondido o oculto, al digitar
el telefono o whatsapp si este existe deberia aparecer, en caso contrario
deberia poder escribir el nombre de la persona correcta."

**Status:** implementado

## Implementación

- `packages/_resultados.html`, sub-form "+ Nuevo residente": orden de
  campos invertido (Contacto primero, Nombre después) -- el campo Nombre
  ahora vive envuelto en `<div id="nuevo-ocupante-nombre-wrap-<id>"
  hidden>`, oculto por defecto.
- JS: al teclear en Contacto,
  - vacío → Nombre se oculta de nuevo (`nombreWrap.hidden = true`).
  - no vacío → Nombre se revela; si el lookup en vivo (issue 97/98)
    encuentra a alguien, aparece relleno y de solo lectura (como ya
    hacía); si no encuentra a nadie, aparece vacío y editable, listo
    para escribir el nombre correcto.
- El wrapper (`<div>` liso, sin `flex`) sí puede usar el atributo nativo
  `hidden` sin el problema de cascada de issue 98 (`.flex` vs `hidden`) --
  ese bug solo afectaba a los otros dos elementos (`preview`,
  `mover-label`), que ya quedaron corregidos ahí.

## Verificación

- `tests/web/test_packages.py`: nuevo test confirma que el wrapper del
  Nombre se sirve con `hidden` y que el campo Contacto aparece ANTES que
  el Nombre en el HTML -- 109 tests, todos pasan.
- Playwright contra el servidor local real, con `is_visible()` (no solo
  el atributo DOM, lección de issue 98): confirmado el ciclo completo --
  oculto al abrir "+ Nuevo residente", aparece vacío/editable al teclear
  un contacto sin match, aparece relleno/readonly al teclear uno con
  match, y vuelve a ocultarse al borrar el contacto por completo.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
