# 255 — `/residentes/{id}` tab Residentes: Promover al mismo renglón, fila inline, Eliminar al final

**Pedido original (cliente), en tres mensajes seguidos:**

1. "Coloca la estrella (promover) también justo al lado de cada
   residente."
2. "Necesito que todos estos íconos se vean inline, para los residentes
   [confirmados] serían 4 íconos y una píldora de 'Confirmado', todo
   alineados."
3. "Lleva el ícono de eliminar al final derecho de la lista."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

- "⭐ Promover" se une al resto de íconos (antes vivía solo, en su
  propio renglón `mt-2` más abajo) -- sigue exclusivo de no-Principal
  (no aplica promoverse a sí mismo); el modal de confirmación se queda
  donde estaba.
- La fila completa (nombre + badge + íconos) vuelve a ser una sola línea
  -- `flex flex-wrap items-center justify-between` en vez del `flex-col
  lg:flex-row` de issue 253 (ese apilado era necesario cuando las
  acciones eran chips con texto; ahora que son solo ícono, hasta 4
  íconos + una píldora caben de sobra). `flex-wrap` se deja como red de
  seguridad -- si algún caso extremo no cupiera, envuelve en vez de
  desbordar, en vez de depender de un breakpoint fijo.
- Orden fijo de íconos: Confirmar (si aplica) -> Promover -> Editar ->
  Notificaciones -> Eliminar -- Eliminar al final, separado del resto de
  acciones "seguras".

Verificado en vivo por curl (`ANGELICA ARRAZOLA` -- Confirmado, no
Principal): nombre + píldora "Confirmado" en una sola línea, íconos en
el orden ⭐ -> ✏️ -> 🔔 -> ❌.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
