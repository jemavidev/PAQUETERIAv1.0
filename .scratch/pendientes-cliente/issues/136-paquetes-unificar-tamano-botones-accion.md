# 136 — `/paquetes`: unificar tamaño de los íconos de Acciones con los de Filtro

**Pedido original (cliente):**
"Necesito unificar tamanos, los botones de accion deberian ser del
mismo tamano que los botones de filtro, la idea es unificar los
tamanos en el sistema, analiza y corrije, el tamano deseado deberia
ser igual al de los botones de filtro."

**Status:** implementado

## Implementación

- `packages/_acciones.html`: nueva `accion_icono_base` (nivel de
  archivo, mismo patrón que `icono_estado_base` en
  `_busqueda_filtros.html`) -- `h-9 w-9 shrink-0 rounded-lg flex
  items-center justify-center` -- MISMA caja que los íconos de Estado
  de la barra de filtros (36×36px). Aplica a los 7 íconos de la
  columna Acciones (WhatsApp/Teléfono/Email/Modificar/Acción/Cancelar/
  Eliminar), activos e inactivos por igual (para que la fila no salte
  de ancho según haya o no acción disponible).
- El glifo interno (`h-5 w-5`, 20px) no cambia -- solo crece la caja
  clickeable que lo envuelve.
- Diseño: "solo ícono, sin caja" se mantiene EN REPOSO (sin fondo fijo
  de color, a diferencia de los íconos de Filtro que sí llevan color
  de fondo siempre porque comunican cuál filtro está activo) -- fondo
  `hover:bg-slate-100` solo al pasar el mouse, para reforzar visualmente
  el área clickeable más grande sin cambiar el lenguaje "sin caja" ya
  establecido para esta columna. Los inactivos (`<span>`, gris) NO
  llevan `hover:bg-slate-100` -- no son clickeables.
- `gap-2` → `gap-1` en el contenedor -- compensa el ancho extra de 7
  cajas de 36px en vez de glifos sueltos de 20px.

## Verificación

- `tests/web/test_packages.py`: 1 test actualizado (aserción de clase
  exacta del ícono de Teléfono con fallback al Anunciante) a la nueva
  combinación de clases. 163 passed.
- Playwright contra el servidor local real: medí el `bounding_box()`
  real de un ícono de Filtro y del primer ícono de Acciones de una
  fila -- ambos exactamente `36×36px`. Captura visual confirma look
  consistente, sin salto de tamaño entre estados activos/inactivos.
- Tailwind: rebuild + `?v=` de 50 a 51.
- Suite completa: pendiente de confirmar.
- Pendiente: deploy a test.papyrus.com.co.
