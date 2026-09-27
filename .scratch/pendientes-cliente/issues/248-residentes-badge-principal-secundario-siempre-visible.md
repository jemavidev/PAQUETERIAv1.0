# 248 — `/residentes/{id}`: badge Principal/Secundario siempre visible junto a "Auto"

**Pedido original (cliente):** "Al lado de auto coloca si este residente
es 'Principal' o no, igual como las píldoras anteriores de color azul."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

`customers_manage/detail.html` -- badges de cabecera (issue 68). Antes
(issue 69) el badge azul "Residente principal" solo se mostraba cuando el
Ocupante ERA principal; el default (Secundario) no llevaba badge, a
propósito ("solo se muestra el estado notable"). El cliente ahora pide
verlo en los dos casos, junto a "Auto" -- texto acortado a
"Principal"/"Secundario" (antes "Residente principal") para que las dos
píldoras vayan cortas una junto a la otra. Mismo estilo azul de siempre.
Sin badge solo si `mi_ocupante` no existe (sin Ocupante activo en
ninguna unidad).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
