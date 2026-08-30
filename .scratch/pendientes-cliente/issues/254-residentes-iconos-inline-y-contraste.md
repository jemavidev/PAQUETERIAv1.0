# 254 — `/residentes/{id}` tab Residentes: íconos solo-emoji, más contraste, badge junto al nombre

**Pedido original (cliente), en dos mensajes seguidos:**

1. "Convierte esto a ícono o simplemente emojis '✏️ Editar 🔔
   Notificaciones ⭐ Promover', remueve los nombres y solo deja los
   íconos, agrega el de eliminar."
2. "'Confirmado' se vería mucho mejor justo al lado del nombre del
   cliente. Cambia el ícono de eliminar por algo de color rojo alusivo.
   Permite que los íconos tengan más contraste y se vean mejor."

**Status:** implementado

## Implementación

- Chips de acción (Confirmar/Eliminar/Editar/Notificaciones/Promover)
  pasan a ícono/emoji SOLO, sin texto -- nuevo macro `chip_icono(color)`
  en `_badge.html` (botón circular `h-8 w-8`, fondo `bg-*-100` + borde,
  más contraste que `chip_accion`, que usaba `bg-*-50` pensado para
  acompañar texto). `title` se queda como tooltip/accesibilidad aunque no
  haya texto visible.
- El ícono de Eliminar/Rechazar (antes sin ninguno) es ❌ (no 🗑️ -- "algo
  de color rojo alusivo").
- El badge de estado (⭐/Confirmado/Pendiente) pasa de apilado debajo del
  nombre a EN LÍNEA a su derecha -- `badge_ocupante` gana el parámetro
  `mt` (default true) para poder quitar el `mt-1` pensado para el
  apilado viejo cuando se usa inline (`mt=false`).

## Seguimiento

Reposición del ícono de Promover, el resto de la fila pasando a inline, y
el orden de los íconos -- ver issue 255.
