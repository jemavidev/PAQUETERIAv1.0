# 206 — `/mis-paquetes`: timeline acordeón exclusivo

**Pedido original (cliente):** "Expandir timeline de cada paquete: Se ve
bien, pero sería bueno solo tener abierto uno a la vez, de forma que si voy
haciendo click se vaya mostrando el que acabo de hacerle click, esto
permitirá visualizar de mejor manera."

**Status:** implementado

## Implementación

`customer/paquetes.html`: el JS de expandir/colapsar ahora cierra todos los
demás paneles `[id^="detalle-"]` antes de abrir el que se acaba de tocar
(y sincroniza `aria-expanded` de los demás botones a `false`).

