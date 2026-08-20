# 137 — Colores más intensos en íconos de Acciones y de Estado (filtros)

**Pedido original (cliente):**
"ayudame con los colores de los iconos y emojis, necesito que sean los
mismos colores, pero un poco mas solidos o intensos"

Alcance aclarado vía pregunta directa (multi-select): el cliente marcó
"Íconos de Acciones en /paquetes", "Íconos de Estado en la barra de
filtros" y "Todo el sistema de íconos de la app en general". Este issue
cubre los dos primeros grupos, concretos y nombrados explícitamente — el
tercero ("todo el sistema") queda deliberadamente pendiente de un barrido
aparte antes de tocar colores que codifican significado en otras partes
de la app (ver Pendiente abajo).

**Status:** implementado

## Implementación

Mismo criterio en ambos archivos: un tono más oscuro dentro de la MISMA
familia de color (sin cambiar de hue), no un color distinto.

- `packages/_acciones.html`: WhatsApp/Entregar `emerald-700→800`;
  Teléfono (ambos fallbacks)/Recibir `blue-800→900`; Email
  `indigo-700→800`; Modificar `slate-700→900`; Cancelar `red-700`
  (con hover `800`); Eliminar `red-800→900` (un paso más oscuro que
  Cancelar, para mantener la distinción visual entre ambas acciones
  destructivas).
- `components/_busqueda_filtros.html`, macro `filtro_estado`, dict
  `estados`: las 4 variantes (suave/activo/opacado) de los 4 estados
  (Anunciado/Recibido/Entregado/Cancelado) subidas un tono — ej. Recibido
  activo `blue-700→800`, Entregado activo `emerald-700→800`, etc.
- Tailwind: rebuild + `?v=` 51→52.

## Verificación

- `tests/web/test_packages.py`: 1 test con aserción de clase exacta
  actualizado a los nuevos tonos (mismo test ya tocado por [[136]]).
  163 passed en ese archivo.
- Sin tests que hardcodeen los tonos viejos de `_busqueda_filtros.html`
  (confirmado por grep) — sin roturas ahí.
- Suite completa: pendiente de confirmar (corriendo junto con [[138]]).
- Pendiente: deploy a test.papyrus.com.co.

## Pendiente

- "Todo el sistema de íconos de la app en general" (tercer grupo
  marcado por el cliente) — queda para un barrido aparte: hay colores en
  otras vistas que codifican significado específico acumulado a lo largo
  de muchos issues anteriores, así que conviene presentar un inventario
  antes de aplicar el mismo "+1 tono" a ciegas.
