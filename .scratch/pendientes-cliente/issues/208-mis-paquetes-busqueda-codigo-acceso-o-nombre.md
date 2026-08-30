# 208 — `/mis-paquetes`: búsqueda por código de acceso o nombre del residente

**Pedido original (cliente):** "Sería bueno tener la posibilidad de tener
una opción de búsqueda por código de acceso o el nombre del residente,
recuerda que debería estar similar a las barras de búsqueda que ya has
venido trabajando."

**Status:** implementado

## Implementación

`customer/paquetes.html`: campo de texto (mismo estilo visual que la barra
de `components/_busqueda_filtros.html`) que filtra EN EL CLIENTE las
tarjetas ya renderizadas por `data-codigo`/`data-nombre` (normalizado sin
acentos), combinado con el filtro de tab de Estado ya existente -- no usa
el macro de búsqueda en vivo del staff (fetch al servidor) porque esta
lista es chica y ya está completa en el DOM.

