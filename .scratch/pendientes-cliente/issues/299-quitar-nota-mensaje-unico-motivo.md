# 299 — Se quita la nota "El mensaje de abajo es uno solo..." del modal CANCELADO

**Pedido original (cliente):** "remueve esto 'El mensaje de abajo es uno
solo -- {motivo} se reemplaza por el que el STAFF elija al cancelar.'" --
tras [[298]], que agregó esa nota explicativa bajo la lista "Motivos
seleccionables" del modal CANCELADO en `/administracion/notificaciones`.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance acordado

- Se retira el `<p>` de ayuda que explicaba que el mensaje es uno solo y
  que `{motivo}` se resuelve con lo elegido al cancelar -- sin reemplazo,
  la sección "Motivos seleccionables" queda solo con la lista y sus
  acciones (Editar/Borrar/+ Agregar).

## Implementación

- `admin/notificaciones.html`: eliminada la línea del `<p class="text-xs
  text-slate-500 mt-2">`. Ningún test dependía de ese texto.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
