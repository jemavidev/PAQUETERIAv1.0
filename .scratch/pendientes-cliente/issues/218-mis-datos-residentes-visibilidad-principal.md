# 218 — `/mis-datos` tab Residentes: mejor visibilidad de quién es el principal

**Pedido original (cliente):** "de qué forma se puede observar mejor que
existe un residente principal y quien es, te pido esto ya que veo que
puedes promocionar a un residente para que sea principal, corrije esto."
(el principal es intercambiable vía "⭐ Principal", así que quién lo es
puede cambiar -- debe quedar inequívoco en la lista).

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

`verify.html`: la tarjeta del Ocupante Principal ahora lleva borde y fondo
azul (`border-blue-300 bg-blue-50/60`, el resto se queda `border-gray-200`)
y su badge pasa de "Residente principal" a "⭐ Residente principal" en
negrilla completa (antes semibold) -- mismo ⭐ que ya usa el botón para
promover, para que la asociación visual sea inmediata.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
