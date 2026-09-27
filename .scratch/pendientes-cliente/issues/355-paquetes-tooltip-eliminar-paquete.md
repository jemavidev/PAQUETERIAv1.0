# 355 — `/paquetes`: tooltip del chip Eliminar dice "Eliminar (solo Admin)" en vez de "Eliminar paquete"

**Pedido original (Jesús):** "Cambia el mensaje de 'Eliminar (solo admin)' a
'Eliminar paquete'".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

Test: `test_tooltip_del_chip_eliminar_dice_eliminar_paquete` en
`tests/web/test_packages.py`.

## Contexto

`CODE/src/app/web/templates/packages/_acciones.html` -- el chip rojo de
Eliminar de la columna Acciones (visible solo para `staff.rol == ADMIN` y
paquetes `ANUNCIADO`) traía `title="Eliminar (solo Admin)"`. Es el único
lugar de la app con ese texto (`grep` en `src/app/web` y `tests`).

## Decisiones

- Solo cambia el `title` (el tooltip que ve el usuario). El `aria-label`
  ("Eliminar") y el gate por rol/estado no se tocan.
- El nuevo texto coincide con el título y el botón del modal de confirmación
  que abre este chip ("Eliminar paquete", `packages/_resultados.html`).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
