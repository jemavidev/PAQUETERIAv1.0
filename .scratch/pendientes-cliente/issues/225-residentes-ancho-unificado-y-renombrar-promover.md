# 225 — `/residentes`: ancho de tabs unificado con `/mis-datos` + renombrar "⭐ Principal" a "⭐ Promover"

**Pedido original (cliente):** "Necesito que el ancho de estos tabs entre
staff y residentes (vistas /mis-datos y /residentes) sean mas unificadas,
mismo ancho que ya maneja /mis-datos para todas sus tabs, ya que esto solo
esta aplicando para las notificaciones. Algo adicional es que necesito que
cambien el nombre de '⭐ Principal' a '⭐ Promover' en todas las vistas y
tabs."

**Status:** implementado

## Implementación

- `customers_manage/detail.html`: contenedor de página pasa de
  `max-w-[460px] lg:max-w-[760px]` (propio, sin relación con ningún otro
  valor del sistema) a `max-w-lg lg:max-w-2xl` -- mismo que usa `/mis-datos`.
  Las tabs "Datos" (dejó de usar el macro `formulario_flujo`, que fuerza
  `max-w-md`), "Dirección" y "Residentes" pierden su `max-w-md mx-auto`
  interno -- las 4 tabs (incluida Notificaciones, que ya no tenía esa
  restricción desde el issue 68 original) comparten ahora el mismo ancho de
  página completo.
- Botón "⭐ Principal" → "⭐ Promover" en `customer/verify.html` y
  `customers_manage/detail.html` (el único lugar con ese texto en las dos
  vistas) -- el badge de estado "⭐ Residente principal" se dejó igual, es
  un estado, no la acción de promover.
