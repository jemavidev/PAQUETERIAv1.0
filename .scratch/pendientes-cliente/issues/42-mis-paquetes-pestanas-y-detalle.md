# 42 — `/mis-paquetes`: pestañas por estado + detalle expandible + código de acceso

**Pedido original (cliente):** "vamos a otro enfoque el de la vista de
/mis-paquetes... analiza que hace esta vista, que muestra, pero sobre todo
que podria mostrar, dame alternativas... en general una vista simple
inicialmente y despues que al hacer click se pueda extenteder mas
informacion acerca de un paquete especifico (incluyendo el codigo de acceso
que no lo veo), resalta los tipos de paquetes, ANUNCIADOS, RECIBIDOS,
ENTREGADOS y CANCELADOS, en tabs como hisiste con la vista de /mis-datos".

**Status:** verificado

## Decisiones del cliente

- Tarjeta simple: nombre + badge + ubicación (Torre/Apto) + verbo del estado
  con la fecha del hito MÁS RECIENTE (no siempre la fecha de anuncio).
- Pestañas con conteo (ej. "Recibidos · 3").

## Implementación

**Prefactor:** la lógica de timeline/actor/fotos/`dias_desde_recibido` que
ya existía (privada) en `search.py` (`/consultar`) se extrajo a
`app/domain/paquete_timeline_service.py` -- compartida ahora por
`/consultar` y `/mis-paquetes`, para que ambas vistas cuenten la misma
historia del mismo paquete con el mismo código (sin duplicar lógica).

- `customer_paquetes.py`: agrupa por estado (conteos), y por cada paquete
  calcula ubicación, fecha relevante según su estado actual, timeline
  completo y fotos -- todo antes de renderizar (sin fetch adicional al
  expandir, mismo criterio que las pestañas de `/mis-datos`).
- `customer/paquetes.html`: pestañas (Todos/Anunciados/Recibidos/
  Entregados/Cancelados, con conteo) filtran las tarjetas ya renderizadas
  vía JS. Cada tarjeta es un `<button>` que expande/colapsa un panel con:
  código de acceso (+ botón copiar al portapapeles), pill de "N días" si
  aplica, y el timeline completo reutilizando `_timeline.html`/
  `_visor_fotos.html` -- los MISMOS componentes que ya usa `/consultar`,
  sin reinventar el diseño.
- Ya no enlaza a `/consultar` -- todo el detalle vive en la misma vista.

Tests nuevos: conteo por pestaña, código de acceso visible, timeline en el
detalle. Suite completa: 544 passed.
