# 436 — `/paquetes` por defecto muestra solo Anunciados y Recibidos

**Pedido original (Jesús, 2026-10-07):** "que en la vista principal de /paquetes al cargar por defecto no se visualicen
los paquetes con estado entregado o cancelados, que solo por defecto se vean los anunciados y los recibidos [...] en caso
que requiera visualizar un paquete con un estado diferente, sería necesario usar los filtros o la barra de búsqueda o
ambos".

**Status:** verificado — probado por Jesús en localhost el 2026-10-07 y desplegado en producción (elclub, `e5819a6` del repo de deploy, 2026-10-07)

## Decisiones

- Sin filtro de Estado y sin búsqueda → solo ANUNCIADO + RECIBIDO.
- Con un Estado seleccionado → solo ese estado (ENTREGADO/CANCELADO incluidos), como hoy.
- Con texto en la búsqueda → todos los estados, como hoy (así se encuentra un entregado o cancelado).
- La búsqueda por código exacto (paquete + sus relacionados) no cambia.
