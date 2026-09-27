# 206 — `/mis-paquetes`: timeline acordeón exclusivo

**Pedido original (cliente):** "Expandir timeline de cada paquete: Se ve
bien, pero sería bueno solo tener abierto uno a la vez, de forma que si voy
haciendo click se vaya mostrando el que acabo de hacerle click, esto
permitirá visualizar de mejor manera."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

`customer/paquetes.html`: el JS de expandir/colapsar ahora cierra todos los
demás paneles `[id^="detalle-"]` antes de abrir el que se acaba de tocar
(y sincroniza `aria-expanded` de los demás botones a `false`).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
