# 258 — `/residentes/{id}` tab Residentes: espacio entre nombre+badge y teléfono

**Pedido original (cliente):** 'Dale un poco de espacio a las 2 líneas
"MARIANA Confirmado / +573008855220".'

**Status:** implementado

## Alcance

`customers_manage/detail.html`, roster de la tab Residentes -- `mt-1` en
el `<p>` del teléfono, que quedaba pegado sin espacio al renglón de
nombre+badge de arriba (issue 254 los puso en la misma columna).
