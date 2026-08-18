# 126 — `/paquetes`: badges de conteo en los íconos Anunciado/Recibido

**Pedido original (cliente):**
"necesito que me digas si puedes crear 2 badges solo mostrando numero,
que numeros la cantidad de paquetes anunciados y la cantidad de
paquetes recibidos, necesito que estos badges los coloque en la parte
superior de los iconos al lado de la barra de filtro, podriamos
llamarlos los iconos de filtro"

**Confirmación (cliente):** "global, dale con esa" -- conteo GLOBAL
confirmado (no filtrado por búsqueda/estado activo).

**Status:** implementado

## Propuesta

- Conteo GLOBAL (todos los paquetes en ANUNCIADO / en RECIBIDO en todo
  el sistema), no filtrado por la búsqueda/estado activo -- funciona
  como indicador operativo, no como recuento de lo que se ve en
  pantalla.
- Badge circular superpuesto en la esquina superior derecha de los
  íconos Anunciado y Recibido de `filtro_estado()`
  (`components/_busqueda_filtros.html`) -- Entregado/Cancelado sin
  badge. Oculto si el conteo es 0.
- Calculado en `_render_lista` (`packages.py`) con una sola consulta
  agrupada por estado, SOLO en la carga completa de página (no en cada
  fetch de búsqueda en vivo, que no re-renderiza la barra de filtros).

## Implementación

- `packages.py`: nueva `_conteos_pendientes(db)` -- 1 sola consulta
  agrupada (`GROUP BY estado`) filtrada a ANUNCIADO/RECIBIDO, retorna
  `{'ANUNCIADO': N, 'RECIBIDO': N}`. `_render_lista` la calcula SOLO
  cuando NO es una petición de búsqueda en vivo (`_peticion_en_vivo`) --
  la barra de filtros vive fuera de `_resultados.html`, así que no hace
  falta recalcular en cada tecleo. Nuevo campo de contexto
  `conteos_estado`.
- `packages/list.html`: pasa `conteos=conteos_estado` a
  `busqueda_filtros(...)`.
- `components/_busqueda_filtros.html`: `busqueda_filtros` y
  `filtro_estado` ganan el parámetro `conteos=none`. Cada ícono de
  Estado se envuelve en un `<div class="relative">`; si
  `conteos.get(clave) > 0`, agrega un `<span>` circular (`absolute
  -top-1.5 -right-1.5`, fondo blanco, texto oscuro, borde sutil) con el
  número, superpuesto en la esquina superior derecha. Como `conteos`
  solo trae claves ANUNCIADO/RECIBIDO, Entregado/Cancelado nunca
  reciben badge sin lógica extra (su `.get(clave, 0)` da 0). No
  participa del repintado en vivo de selección de Estado
  (`pintarIconos()`) -- vive en un `<span>` hermano del botón.

## Verificación

- `tests/web/test_packages.py`: 4 tests nuevos -- badges muestran el
  conteo correcto junto a cada ícono; el conteo de Anunciado NO cambia
  al filtrar por Recibido (confirma que es global); sin paquetes
  pendientes no se renderiza ningún badge; el fragmento de búsqueda en
  vivo no incluye la barra de filtros en absoluto.
- `test_lista_no_dispara_una_query_de_persona_o_usuario_por_paquete`
  (guarda de rendimiento, issue 77): el umbral de queries sube de 11 a
  12 -- la nueva consulta agrupada es 1 query FIJA (no por paquete), no
  reintroduce el N+1 que ese test vigila.
- Playwright contra el servidor local real: badges circulares visibles
  con el conteo correcto sobre Anunciado/Recibido, sin badge en
  Entregado/Cancelado.
- Suite completa: 1014 passed.

**Ampliación (cliente):** "Posibilidades que se ubiquen en la esqueina
superior derecha de cada icono y ademas que sean de color rojo?" --
bug propio encontrado al leerlo: la posición YA estaba pensada así en
el CSS (`absolute -top-1.5 -right-1.5`), pero nunca se reconstruyó
`tailwind.css` tras agregar esas clases nuevas (paso obligatorio de
este repo, ver memoria "PaqueteX Tailwind build") -- sin compilar, esas
utilidades no existían en el CSS servido, así que el badge se veía sin
posicionar (fluía DEBAJO del ícono en vez de superpuesto en la
esquina). Corregido: `npm run build:css` (ambos targets, legacy +
rebuild) + `tailwind.css?v=` de 46 a 47 en `base.html`. Color cambiado
de blanco/slate a `bg-red-600 text-white border-2 border-white` (el
borde blanco lo separa visualmente del ícono de color de fondo).
`tests/web/test_packages.py`: las 4 aserciones que buscaban las clases
viejas (`bg-white text-slate-900`) actualizadas a las nuevas
(`bg-red-600 text-white`).

- Playwright contra el servidor local real (zoom sobre la barra de
  filtros): badges rojos, bien superpuestos en la esquina superior
  derecha de Anunciado/Recibido, separados con borde blanco del color
  de fondo del ícono.
- Suite completa (tras el fix): pendiente de confirmar, corriendo en
  background.
- Pendiente: deploy a test.papyrus.com.co.
