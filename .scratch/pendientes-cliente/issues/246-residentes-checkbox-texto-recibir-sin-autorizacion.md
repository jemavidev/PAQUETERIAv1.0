# 246 — `/residentes/{id}`: texto del checkbox de recepción automática

**Pedido original (cliente):** "Cambia este texto 'Autoriza que Papyrus
anuncie/reciba paquetes a su nombre sin necesidad de llamarlo primero'
por 'Recibir paquetes sin autorización'."

**Status:** implementado

## Alcance

`customers_manage/detail.html` -- label del checkbox
`autoriza_recepcion_automatica` (tab Datos, lado staff). El texto
equivalente en `/mis-datos` (`customer/verify.html`) es otro distinto
("Autorizo a Papyrus para recibir todos los paquetes a mi nombre." +
enlace a Términos y condiciones, issue 209/210) -- no calza con el texto
citado por el cliente, así que queda fuera de este pedido.
