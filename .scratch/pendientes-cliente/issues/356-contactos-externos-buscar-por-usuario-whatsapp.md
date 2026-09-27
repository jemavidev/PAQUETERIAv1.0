# 356 — `/administracion/contactos-externos`: la búsqueda también debe cubrir el usuario de WhatsApp

**Pedido original (Jesús):** "Necesito que permitas que en la vista
/administracion/contactos-externos se puedan realizar busquedas por los
siguientes criterios 'Nombre, Teléfono y usuario de WhatsApp', hasta el
momento creo que solo es posible buscar por 'Nombre y Teléfono'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Contexto

`buscar_contactos_externos` (`contacto_externo_service.py`) hoy es
excluyente: si el término normaliza como teléfono busca SOLO por teléfono
(exacto); si no, SOLO por nombre (`ilike '%x%'`). El usuario de WhatsApp
(`ContactoExternoWhatsapp.whatsapp_usuario`, forma canónica de
`normalizar_whatsapp_usuario`: sin `@`, en minúscula) no participa.

## Decisiones

- Nombre, teléfono y WhatsApp pasan a ser condiciones en OR -- el término
  matchea si coincide con CUALQUIERA de las tres.
- WhatsApp: coincidencia PARCIAL sobre la forma canónica (mismo criterio que
  el nombre; se puede escribir `@ana`, `Ana` o `ana.gom`). Los comodines
  `_`/`%` del término se escapan (un usuario de WhatsApp puede tener `_`).
- Sin migración de índice trigrama por ahora: `contactos_externos_whatsapps`
  tiene del orden de 1.000 filas -- ofrecer el índice (como 0053) si la
  tabla crece.
- El placeholder del buscador ("Nombre o teléfono") pasa a mencionar
  WhatsApp.

## Implementación

- `contacto_externo_service.buscar_contactos_externos`: `or_(nombre ilike,
  id en teléfonos [si el término normaliza], id en whatsapps [contains
  autoescape sobre la forma canónica])`. Subconsultas en vez de materializar
  ids en Python.
- Placeholder del buscador: "Nombre, teléfono o WhatsApp".

## Verificación

- `tests/web/test_admin_contactos_externos.py`: por usuario completo; parcial
  + `@` + mayúsculas + espacios; `_` no es comodín; nombre sigue igual.
- En vivo contra `localhost:8010` (1.041 contactos reales): `adrianacuelloq01`
  y `@ADRIANACUELLOQ01` -> 1 contacto; `adri` -> 3.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
