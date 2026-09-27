# 246 — `/residentes/{id}`: texto del checkbox de recepción automática

**Pedido original (cliente):** "Cambia este texto 'Autoriza que Papyrus
anuncie/reciba paquetes a su nombre sin necesidad de llamarlo primero'
por 'Recibir paquetes sin autorización'."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

`customers_manage/detail.html` -- label del checkbox
`autoriza_recepcion_automatica` (tab Datos, lado staff). El texto
equivalente en `/mis-datos` (`customer/verify.html`) es otro distinto
("Autorizo a Papyrus para recibir todos los paquetes a mi nombre." +
enlace a Términos y condiciones, issue 209/210) -- no calza con el texto
citado por el cliente, así que queda fuera de este pedido.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
