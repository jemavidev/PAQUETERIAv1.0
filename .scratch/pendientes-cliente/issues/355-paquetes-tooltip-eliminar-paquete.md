# 355 — `/paquetes`: tooltip del chip Eliminar dice "Eliminar (solo Admin)" en vez de "Eliminar paquete"

**Pedido original (Jesús):** "Cambia el mensaje de 'Eliminar (solo admin)' a
'Eliminar paquete'".

**Status:** implementado, pendiente confirmar visualmente

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
