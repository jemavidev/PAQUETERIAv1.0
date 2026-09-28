# 426 — `/paquetes`: los badges Anunciado/Recibido siguen la búsqueda activa

**Pedido original (Jesús):** "cuando se filtra por cualquier item, digamos en la barra de búsqueda se busca una palabra,
los badges siguen mostrando el mismo número de paquetes anunciados y recibidos, la idea es que si se filtra algo se
actualicen los badges".

**Status:** verificado en escritorio (`a3bda27`, Jesús 2026-09-28) · falta confirmar en celular

## Contexto

El issue 126 definió los badges como conteo GLOBAL a propósito ("global, dale con esa"): indicador operativo, no
recuento de lo que se ve. Este pedido reemplaza esa decisión. Además, la búsqueda en vivo solo reemplaza
`_resultados.html`; la barra de filtros (con los badges) no se vuelve a pintar.

## Decisiones

- Los badges cuentan los ANUNCIADO/RECIBIDO que calzan con la búsqueda `q` y el modo "Mostrar conexiones" -- el mismo
  criterio que la lista. Sin búsqueda, el total de siempre.
- NO se filtran por el estado elegido: el estado es justo lo que el badge ayuda a escoger (si se filtrara, al elegir
  Anunciado el badge de Recibido caería a 0).
- Código de acceso exacto (expansión a sus RECIBIDO relacionados): cuentan los paquetes de ese conjunto.
- En búsqueda en vivo los conteos viajan como headers de la respuesta (igual que `X-Conteo-Conectados`) y el JS de
  la barra actualiza los badges; conteo 0 oculta el badge, como hoy.

## Verificación

- `tests/web/test_packages.py`: `test_badges_conteo_siguen_la_busqueda_activa`, `test_busqueda_en_vivo_manda_los_conteos_de_los_badges_en_headers`, `test_la_barra_de_filtros_actualiza_los_badges_con_los_headers` (fallaban antes); la del 126 "es global" renombrada a `test_badges_conteo_no_se_filtran_por_el_estado_elegido` (esa parte sigue igual). Archivo completo: 241 en verde.
- Sin clases de Tailwind nuevas (el badge creado por JS usa las mismas clases que el del servidor).
