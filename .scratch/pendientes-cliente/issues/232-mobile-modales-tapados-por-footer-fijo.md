# 232 — Mobile: modales tapados por el `site-footer-mobile` fijo

**Pedido original (cliente):** "En la opción mobile necesito que la última
información que se muestre en una vista no sea obstruida por ningún
'site-footer-mobile' o 'footer-nav-mobile'."

**Status:** implementado

## Investigación

`body { padding-bottom: 64px }` (`base.html`) ya reserva el espacio
correcto para el contenido NORMAL de página (confirmado: ninguna de las
vistas revisadas tiene su propio contenedor `overflow-y-auto`/`h-screen`
que se salte ese padding).

El problema real es específico de los MODALES (`components/_modales.html`):
usaban `z-50`, EXACTO el mismo z-index que `.site-footer-mobile` (nav fijo
inferior). Con un empate de z-index, gana el elemento que aparece DESPUÉS
en el HTML -- el footer se renderiza después de `{% block content %}`
(donde vive cualquier modal), así que en mobile tapaba la parte baja de
cualquier modal abierto, botón "Guardar" incluido (justo lo último que se
ve en cada modal de Editar/Notificaciones/Promover/Eliminar).

## Implementación

`components/_modales.html`: `z-50` → `z-[60]` en los dos macros (`modal`,
`modal_confirmacion`) -- arriba de cualquier `z-50` del resto del sistema,
sin acoplarse al valor exacto del footer. Arregla TODOS los modales del
sistema (no solo los nuevos de esta sesión), incluidos los que ya existían
en `/residentes`/`/paquetes` antes.
