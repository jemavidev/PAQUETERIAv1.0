# 239 — `/mis-paquetes`: la búsqueda también actualiza el conteo de cada tab

**Pedido original (cliente):** "Necesito que en la vista de /mis-paquetes
al momento de utilizar la barra de búsqueda, quiero que las cantidades de
en los Tabs se actualicen también."

**Status:** implementado

## Alcance

`customer/paquetes.html` -- la búsqueda (issue 208) ya filtra las tarjetas
en el cliente (JS puro, sin ida y vuelta al servidor); el conteo `· N` de
cada tab (`Anunciados · 2`, etc.) quedaba fijo con el total server-side
(`conteos`), sin reflejar el término de búsqueda. Ahora `repintar()`
recalcula, por cada tecla, cuántas tarjetas de CADA estado calzan con el
término (independiente de cuál tab esté activo) y reescribe el texto de
los 4 botones -- así se puede ver de un vistazo en qué tab hay resultados
sin tener que entrar a cada uno.
