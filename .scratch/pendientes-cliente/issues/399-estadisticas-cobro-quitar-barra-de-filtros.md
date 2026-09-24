# 399 — `/administracion/estadisticas-cobro`: quitar la barra de filtros

**Pedido original (Jesús):** "puedes en test y localhost eliminar esta seccion "/administracion/estadisticas-cobro"
la misma que "filtros-estadisticas-cobro" en algun momento me dijiste que no er necesaria".

**Status:** implementado — verificado en localhost:8010; desplegando a test

## Qué se quita

La barra `#filtros-estadisticas-cobro`, arriba del tablero: los atajos de fecha (Hoy, Ayer, Esta semana, Este mes,
3 últimos meses, Semestre, Último año), las pills de Tipo (Normal / Extra-dimensionado) y las de Cobrado / Anulado,
junto con el JS que recargaba los resultados al tocarlas.

## Consecuencias y ajustes

- "Periodo seleccionado" (antes "Responde a los filtros de arriba") pasa a mostrar siempre TODOS los datos. Se
  renombra a **"Todo el historial"**, con el subtítulo "Todos los datos registrados", y se quitan los chips de
  "Filtros activos".
- "Panorama" y "Ahora" pierden el "· no cambia con los filtros" de su subtítulo, porque ya no hay filtros.
- El título "Estadísticas de cobro" en escritorio vivía dentro de la barra: se mantiene fuera de ella.
- El servidor sigue aceptando `?rango=`/`?tipo=`/`?estado_cobro=` en la URL (no se toca el servicio), pero la
  pantalla ya no los ofrece.
- Deja sin efecto la parte de filtros de la propuesta del issue 370 (prototipo en `:8011`), que no está en el
  código real.
