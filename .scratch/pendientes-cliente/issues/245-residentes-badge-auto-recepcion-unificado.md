# 245 — `/residentes/{id}`: badge "✓ Recepción automática" → "Auto"

**Pedido original (cliente):** "Cambia esto '✓ Recepción automática' a
'Auto', la idea es que se unifique el nombre de la opción para auto
recibir paquetes para ese cliente."

**Status:** implementado

## Alcance

`customers_manage/detail.html` -- badge de cabecera de la ficha (issue
68). La tabla de `/residentes` (`customers_manage/_resultados.html`,
línea 158) YA usa "Auto" para esta misma bandera
(`autoriza_recepcion_automatica`) -- este cambio unifica el texto de la
ficha con el que la lista ya usaba.
