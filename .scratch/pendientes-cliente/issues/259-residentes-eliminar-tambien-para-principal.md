# 259 — `/residentes/{id}` tab Residentes: ❌ Eliminar también para el principal

**Pedido original (cliente):** "permite que la opción de eliminar también
la tenga el residente principal."

**Status:** implementado

## Alcance

`customers_manage/detail.html`, roster de la tab Residentes -- el botón
❌ (Eliminar/Rechazar) y su modal de confirmación vivían dentro de
`{% if not o.es_principal %}`, así que la fila del principal nunca lo
mostraba.

El backend (`dar_de_baja_ocupante`, `ocupante_service.py`) ya soporta dar
de baja al principal sin cambios: si quedan otros Ocupantes activos en el
Apartamento, levanta `ValueError` ("El principal no puede darse de baja
mientras existan otros Ocupantes activos...") que la ruta
`/residentes/.../baja` ya captura y renderiza como banner de error (mismo
patrón que el resto de esta vista). Si el principal es el único Ocupante
activo, la baja procede igual que para cualquier otro.

Cambio: quitar el guard `{% if not o.es_principal %}` alrededor del botón
❌ y del `modal_confirmacion('baja-...')`, moviendo el `{% set
accion_baja %}` fuera de ese guard para que quede disponible también
para la fila del principal.

## Implementación

`customers_manage/detail.html` -- sin cambios en el backend, ya soportaba
esto sin tocar código. Se verificó en vivo contra el dev local:

- El botón ❌ y su modal ahora se renderizan también en la fila del
  principal (probado con LAIS HERNANDEZ, TORRE 10 apto 302).
- POST real a `.../baja` sobre el principal, con otro Ocupante (RAFAEL
  TORRES) todavía activo en el mismo apartamento -> 400, banner "El
  principal no puede darse de baja mientras existan otros Ocupantes
  activos...", y se confirmó en la BD que `desvinculado_en` siguió en
  `None` (no hubo mutación).
- Suite completa `tests/web/test_customers_manage.py`: 139 passed.
