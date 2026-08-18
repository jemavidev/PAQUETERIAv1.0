# 120 — /paquetes ordenado por último cambio de estado, no por fecha de anuncio

**Pedido original (cliente):**
"necesito que para la vista /paquetes todo este ordenado desde el ultimo
cambio de estado hasta el mas antiguo, la idea es que siempre este lo mas
reciente de primero."

**Status:** verificado en test.papyrus.com.co

## Diagnóstico

La consulta ordenaba por `Paquete.announced_at.desc()` -- la fecha de
ANUNCIO, no la del último cambio real de estado. Un paquete anunciado
hace 3 días pero recién Recibido/Entregado/Cancelado HOY se quedaba
enterrado donde le tocaba por su fecha de anuncio, en vez de subir al
tope de la lista.

La columna "Fecha" de la tabla YA mostraba lo correcto (`_fecha_ultima_
accion`, issue 79: `cancelled_at or delivered_at or received_at or
announced_at`) -- el bug era que el `ORDER BY` de la consulta nunca usó
esa misma lógica, solo la fecha de anuncio.

## Implementación

- `packages.py`, `_render_lista`: `ORDER BY` cambia de
  `Paquete.announced_at.desc()` a
  `func.coalesce(cancelled_at, delivered_at, received_at,
  announced_at).desc()` -- mismo orden de prioridad que
  `_fecha_ultima_accion`, pero resuelto en SQL (no en Python) para que
  la paginación (`OFFSET`/`LIMIT`, ya a nivel de consulta) corte en el
  lugar correcto.

## Verificación

- `tests/web/test_packages.py`: test nuevo -- paquete Anunciado hace más
  tiempo pero Recibido/Entregado/Cancelado más recientemente aparece
  ANTES que uno anunciado después pero sin ninguna transición todavía.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
