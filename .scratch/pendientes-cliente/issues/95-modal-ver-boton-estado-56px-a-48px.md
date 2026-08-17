# 95 — Modal "Ver": botón de siguiente estado de 56px a 48px

**Pedido original (cliente):**
"can you make it a bit more compact, maybe reducing the size (marging or
padding) of the button that can let you change states (Anunciado -->
Recibido and Recibido --> Entregado, also including to change to cancelado
from any of them)" — aclarado vía pregunta: el modal "Ver" solo tiene un
botón de estado (Recibir/Entregar, 56px); Cancelar no vive dentro de este
modal, solo en la columna Acciones de la tabla. El cliente confirmó que
solo quería achicar el botón existente, sin agregar Cancelar al modal.

**Status:** verificado

## Implementación

- `packages/_resultados.html`, modal "Ver": el botón circular de siguiente
  estado (Recibir en ANUNCIADO, Entregar en RECIBIDO) baja de **56px** a
  **48px** (`h-14 w-14` -> `h-12 w-12`), ícono interno de `h-8 w-8` a
  `h-6 w-6` en la misma proporción. Tercer ajuste de este botón: 36px
  original -> 72px (doblado 2026-08-15) -> 56px (2026-08-16) -> 48px ahora.

## Verificación

- `tests/web/test_packages.py`: 97 tests, todos pasan (ninguno afirmaba las
  clases de tamaño exactas).
- Playwright contra el servidor local real: bounding box del botón
  confirmado en 48x48px, screenshot del modal "Ver" en estado RECIBIDO
  muestra el header más compacto con el botón todavía claramente visible y
  cliqueable.
- Suite completa: ver commit para el conteo final.
- Desplegado a test.papyrus.com.co (2026-08-17), confirmado en el contenedor real (`docker exec paquetex-app-1`).
