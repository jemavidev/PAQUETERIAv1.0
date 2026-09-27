# 324 — `/announce`: quitar el enlace "¿Solo registrar residentes?"

**Pedido original (cliente):** "Tomemos la vista de /announce como referencia base, ya que existen
varias formas de interactuar con este flujo, comencemos por eliminar este enlace '¿Solo registrar
residentes?'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

Primer ajuste de una serie sobre `/announce` (vista de staff, `announce_new.py`). Se retira el
enlace `¿Solo registrar residentes? → /residentes` del encabezado de `announce_new/form.html` --
sin reemplazo, sin cambiar nada más del layout salvo simplificar el contenedor que solo existía
para ubicarlo junto al título.

## Implementación

- `app/web/templates/announce_new/form.html`: quitado el `<a href="/residentes">`; el `<h1>` ya no
  necesita el wrapper flex que lo alineaba con el link.
- `tests/web/test_announce_new.py`: `test_operador_ve_el_campo_unico_y_el_enlace_a_residentes`
  renombrado a `test_operador_ve_el_campo_unico` (se quita la aserción del `href="/residentes"`).

## Verificación

- `tests/web/test_announce_new.py` en verde.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente desplegar y confirmar". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
