# 208 — `/mis-paquetes`: búsqueda por código de acceso o nombre del residente

**Pedido original (cliente):** "Sería bueno tener la posibilidad de tener
una opción de búsqueda por código de acceso o el nombre del residente,
recuerda que debería estar similar a las barras de búsqueda que ya has
venido trabajando."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

`customer/paquetes.html`: campo de texto (mismo estilo visual que la barra
de `components/_busqueda_filtros.html`) que filtra EN EL CLIENTE las
tarjetas ya renderizadas por `data-codigo`/`data-nombre` (normalizado sin
acentos), combinado con el filtro de tab de Estado ya existente -- no usa
el macro de búsqueda en vivo del staff (fetch al servidor) porque esta
lista es chica y ya está completa en el DOM.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
