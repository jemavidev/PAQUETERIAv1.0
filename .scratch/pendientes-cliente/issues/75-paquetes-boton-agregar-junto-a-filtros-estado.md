# 75 — `/paquetes`: botón "Agregar" junto a los íconos de Estado

**Pedido original (cliente):** "apenas acabo de iniciar las pruebas y anuncie
un paquete para un cliente, pero no veo una forma de anunciar otro paquete
desde la vista `/paquetes` de que forma podria agregar un similar al que
haces con los botones de filtrado 'ANUNCIADO, RECIBIDO...' la idea es que
este a la mano izquierda del boton de ANUNCIADO, justo al lado, podria ser
algo que referencie el echo de 'agregar'. Este nuevo icono o boton debe
tener el look and feel del resto de botones a su lado."

**Status:** implementado

## Contexto

`/paquetes` (staff) no tenía ningún atajo directo a `/announce` (staff) --
había que salir por el menú de navegación cada vez que se quería anunciar
otro paquete después de revisar la lista.

## Implementación

- `components/_busqueda_filtros.html`, macro `busqueda_filtros`: nuevo param
  `mostrar_agregar=False`. Cuando es `True`, renderiza un `<a href="/announce">`
  inmediatamente a la izquierda del grupo de íconos de Estado (antes de
  `filtro_estado()` en el mismo `flex` row) -- mismo tamaño/forma/sombra/foco
  que sus vecinos (`icono_estado_base`, compartido con `filtro_estado`), ícono
  "+" en el mismo estilo outline (`viewBox 24x24`, `stroke-width 2`) que
  usan ANUNCIADO/RECIBIDO/ENTREGADO/CANCELADO, en azul primario (`bg-blue-800
  hover:bg-blue-700`) para distinguirlo como acción de navegación, no un
  filtro más.
  - Vive FUERA de `filtro_estado()` (que es puramente sobre filtrar) porque
    es un enlace de navegación, no un filtro -- por eso es `<a>`, no
    `<button type="button">` con JS de toggle.
  - `False` por defecto, sin parametrizar el `href` -- hoy solo `/paquetes`
    lo activa y siempre apunta a `/announce`; no hay un segundo caller que
    necesite otro destino todavía (evita generalizar de más sin necesidad
    real).
- `packages/list.html`: pasa `mostrar_agregar=True` en su llamada a
  `busqueda_filtros`.

## Verificación

- `tests/web/test_packages.py` (52) y `tests/web/test_layout.py` pasan sin
  cambios.
- Verificación manual en navegador (Postgres efímero + Playwright): el botón
  aparece a la izquierda de ANUNCIADO, mismo tamaño/forma que sus vecinos,
  clic navega a `/announce`, sin errores de consola.
