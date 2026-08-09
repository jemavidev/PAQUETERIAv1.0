# 73 — `/paquetes`: tarjeta de filtros/acciones con look de producción (`/customers/manage`)

**Pedido original (cliente):** que la tarjeta de búsqueda/filtros de
`/paquetes` (`components/_busqueda_filtros.html`) se vea similar a la
sección de filtros y acciones de la vista de producción
`https://paquetex.papyrus.com.co/customers/manage`
(clase `bg-white rounded-xl shadow-lg border border-gray-100 p-3 sm:p-4
lg:p-6 mb-4 sm:mb-6`) — colores más vivos y más espacio usado por la
información. Explícitamente **no** pide letras más grandes (el tamaño de
texto sigue como está).

**Status:** implementado

## Contexto

La tarjeta actual (`components/_busqueda_filtros.html`, único caller
`packages/list.html`) usaba `max-w-lg mx-auto bg-white border
border-gray-200 rounded-2xl shadow p-5` — ancho fijo angosto (32rem),
padding fijo (no responsivo por breakpoint) y 4 íconos de Estado como
círculos vacíos en tono pastel muy claro.

El cliente compartió el HTML real de la tarjeta de producción
(`https://paquetex.papyrus.com.co/packages`, clase `bg-white rounded-xl
shadow-lg border border-gray-100 p-3 sm:p-4 lg:p-6 mb-4 sm:mb-6`) como
referencia de look. Se tomó el padding responsivo, `rounded-xl`,
`shadow-lg`, `border-gray-100` y el ancho completo (sin `max-w-lg`) de esa
referencia; NO se copiaron los botones extra que trae esa vista (⭐
anunciar nuevo / + anunciar clásico → `/announce-new`, `/announce-papyrus`,
rutas que no existen en este proyecto) porque el pedido era solo sobre
color/espacio, no sobre agregar acciones nuevas.

## Implementación

- `components/_busqueda_filtros.html`:
  - Tarjeta: `max-w-lg mx-auto ... rounded-2xl shadow p-5` →
    `bg-white rounded-xl shadow-lg border border-gray-100 p-3 sm:p-4
    lg:p-6 mb-4 sm:mb-6` (ancho completo del contenedor de la página,
    hasta 1100px en desktop vía `packages/list.html`).
  - Fila interna: `gap-2` → `gap-2 sm:gap-3 lg:gap-4` (más espacio entre
    el campo de texto y los íconos en pantallas grandes).
  - Los 4 íconos de Estado pasan de círculo vacío pastel (`bg-amber-100`
    etc., sin ícono) a círculo sólido de color -400 (inactivo) / -600–700
    + anillo (activo), `h-7 w-7` → `h-9 w-9`, con un glifo blanco dentro
    (reloj/check/caja/x, mismos trazos que produce usa en sus botones
    cuadrados). El botón de reseteo mantiene su estilo neutro (blanco/gris)
    a propósito, para no competir visualmente con los de Estado.
  - No se tocó el modelo de interacción (toggle single-select + resultados
    en vivo, ticket 03) — solo color/tamaño/espaciado.
- `base.html`: `tailwind.css?v=38` → `?v=39`.
- Tailwind recompilado (`npm run build:css`) y ambos `tailwind.css`
  comiteados junto con el bump de versión (ver memoria
  `paquetex-tailwind-build`).

## Verificación

- Sintaxis Jinja verificada con `Environment.parse()`.
- Preview renderizado con headless Chrome (desktop 1200px y mobile
  390px) de la tarjeta sin filtro y con "Recibido" + texto activos:
  ancho completo, colores vivos, estado activo claramente distinguible
  del resto (tono más oscuro + anillo).
- `tests/web/test_packages.py` (52) y `tests/web/test_layout.py` (26)
  pasan sin cambios.
- Pendiente: confirmar en vivo en `test.papyrus.com.co` tras el deploy.
