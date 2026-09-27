# 310 — Botón "Mostrar conexiones" deshabilitado cuando no hay conexiones reales

**Pedido original (cliente):** el botón de "conectados" (issue 308) solo se debe habilitar
cuando existan conexiones reales para la búsqueda actual -- si presionarlo no cambiaría nada
en pantalla, no debería ser presionable.

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo
disponible en esta sesión).

## Regla

`hay_conexiones` es `False` (botón `disabled` real, no solo opacado) cuando:
- `q` está vacío -- sin búsqueda no hay nada que "conectar".
- Torre/Apto está activo (issue 309) -- `conectados` se ignora por completo en modo estricto.
- El SET de condiciones "conectado" (mismo criterio de issue 308) no trae NINGÚN resultado
  para el `q` actual (`_hay_conexiones` en packages.py, vía `.exists()`).

## Implementación

`_condiciones_busqueda(q, conectados)` (packages.py) -- factoreada fuera de `_listar` para que
`_hay_conexiones` pueda preguntar "¿existiría algún resultado en modo conectado?" sin duplicar
la regla de qué cuenta como "conectado".

La barra de búsqueda vive FUERA de `#resultados-paquetes` y no se vuelve a renderizar en cada
fetch de búsqueda en vivo -- por eso `hay_conexiones` viaja también como header de respuesta
(`X-Hay-Conexiones`), que el JS de `_busqueda_filtros.html` lee tras cada fetch para
habilitar/deshabilitar el botón sin recargar la página completa.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente verificar visualmente en vivo". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
