# 258 — `/residentes/{id}` tab Residentes: espacio entre nombre+badge y teléfono

**Pedido original (cliente):** 'Dale un poco de espacio a las 2 líneas
"MARIANA Confirmado / +573008855220".'

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

`customers_manage/detail.html`, roster de la tab Residentes -- `mt-1` en
el `<p>` del teléfono, que quedaba pegado sin espacio al renglón de
nombre+badge de arriba (issue 254 los puso en la misma columna).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
