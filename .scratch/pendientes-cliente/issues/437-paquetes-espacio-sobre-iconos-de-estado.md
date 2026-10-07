# 437 — Espacio arriba de la fila de íconos de Estado en `/paquetes`

**Pedido original (Jesús, 2026-10-07):** "en la clase `flex items-center gap-2 w-full justify-between md:w-auto
md:justify-normal` dejar un pequeño espacio en la parte superior ya que está muy pegado a la sección superior".

**Status:** verificado — probado por Jesús en localhost el 2026-10-07 y desplegado en producción (elclub, `e5819a6` del repo de deploy, 2026-10-07)

## Decisiones

- Es el contenedor de los 4 íconos de Estado (`filtro_estado()` en `components/_busqueda_filtros.html`). En celular baja
  a su propia fila debajo del buscador, a solo 8 px (`gap-2`): se le suma `mt-2` solo en celular (`md:mt-0`, en
  escritorio va en la misma fila que el buscador y no hace falta).
