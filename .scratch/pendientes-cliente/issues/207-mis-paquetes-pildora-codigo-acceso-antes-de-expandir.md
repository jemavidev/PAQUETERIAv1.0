# 207 — `/mis-paquetes`: píldora de "Código de acceso" visible antes de expandir

**Pedido original (cliente):** "Sería bueno poder visualizar en cada
paquete en /mis-paquetes el 'Código de acceso' en cada uno de los estados
de cada paquete, esto sería bueno que se vea de forma tipo 'píldora' (como
ya se ha venido trabajando), este podría estar ubicado al lado de la
píldora del estado, recuerda que sería en cada paquete antes de
expandirlo, ya que cuando está expandido sí se muestra sin problemas."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

`customer/paquetes.html`: píldora `access_code` (mismo estilo que la del
detalle expandido, compactada) agregada junto al `badge(p.estado)` en el
header de cada tarjeta, antes de expandir.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
