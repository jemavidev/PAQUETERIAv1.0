# 231 — `/mis-datos` y `/residentes`: alineación del modal de Notificaciones + textos de placeholders/badge

**Pedido original (cliente, 3 mensajes seguidos):**
1. "Para la notificación en desktop veo que no está alineada cada columna,
   solucionalo"
2. "Cambia 'Agregar WhatsApp' por 'Usuario WhatsApp', también remueve la
   palabra 'Agregar ' en los placeholders"
3. "Remplaza 'Pendiente de confirmar' por 'Pendiente' solamente"

**Status:** implementado

## Implementación

- Alineación: el modal de Notificaciones (issue 230) usaba el breakpoint
  `sm:` para pasar de la fila apilada (mobile) a la grilla de 5 columnas
  (desktop) -- innecesario y probable causa del desalineamiento: los
  breakpoints de Tailwind miden el VIEWPORT, no el ancho del modal, así que
  no hacía falta bajarlo de `lg:` (el que ya usa, probado, el tab
  "Notificaciones" principal). Revertido a `lg:`, byte a byte igual al
  patrón ya probado.
- Placeholders: "Agregar teléfono"/"Agregar Teléfono" → "Teléfono",
  "Agregar WhatsApp" → "Usuario WhatsApp", "Agregar Teléfono o WhatsApp" →
  "Teléfono o WhatsApp" -- en las dos vistas (`/mis-datos` y `/residentes`,
  mismos textos duplicados en ambas).
- Badge: "Pendiente de confirmar" → "Pendiente" -- en las dos vistas.
