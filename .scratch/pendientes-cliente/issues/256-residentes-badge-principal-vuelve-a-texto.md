# 256 — `/residentes/{id}` tab Residentes: badge Principal vuelve a texto

**Pedido original (cliente):** "Esta estrella de '⭐' conviértela a una
vala [sic, 'píldora'/'badge'] que diga 'Principal'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

Badge de estado (⭐/Confirmado/Pendiente) inline junto al nombre, en el
roster de la tab Residentes (issue 254). El caso Principal vuelve al
texto default del macro (`badge_ocupante('principal', mt=false)`, sin el
override `texto='⭐'` que issue 252 le había puesto) -- misma píldora
azul, mismo tamaño que "Confirmado"/"Pendiente" al lado. El ícono ⭐ de
la acción "Promover" (botón, no badge) no cambia -- son elementos
distintos.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
