# 78 — `/paquetes`: tabla en vez de tarjetas (5 alternativas evaluadas)

**Pedido original (cliente):** "necesito tu ayuda con esta vista /paquetes,
en local host quiero ver unas 5 alternativasd de como se muestra esta
informacion, enfocate en que sea una tabla, ademas necesito que incluya una
columna de botones de accion, ten presente los colores que ya se estan
manejando, ademas necesito que sea enfocada a agilidad, UX y rapidez,
necesito que incluya paginacion cada 10 items, y que los filtros existentes
sigan trabajando con la barra de busqueda tal cual como esta". Tras ver las 5
capturas: "la opcion A me parece buena ... por ahora esta es la que
necesito, implementala".

**Status:** implementado

## Contexto

`/paquetes` mostraba una grilla de tarjetas (`components/_tarjetas.html`).
Se armó un prototipo real (skill `prototype`) con 5 alternativas de tabla
switchables vía `?variant=` sobre datos reales de desarrollo, se compararon
en localhost (capturas de pantalla vía Playwright, el navegador de Claude no
estaba conectado), y el cliente eligió la variante A ("Grid denso").

## Implementación

- `app/web/routes/packages.py`: `_POR_PAGINA` 20 → 10.
- `packages/_resultados.html`: reemplaza la grilla de tarjetas por una tabla
  real (`overflow-x-auto` + `<table>`, patrón ya aprobado en
  `components/_tablas.html`) — columnas Estado/Destinatario/Ubicación/Guía/
  Anunciado/Última acción/Acciones. Los modales por paquete se separaron en
  un loop propio (igual que `admin/staff.html`) en vez de vivir dentro de
  cada fila.
- `packages/_acciones.html` (nuevo): macro `acciones_iconos(p)` — íconos de
  Recibir/Corregir/Cancelar (ANUNCIADO) o Entregar/Cancelar (RECIBIDO),
  coloreados por rol semántico (primary/neutral/danger), mismos
  `data-open="modal-<tipo>-<id>"` reales de siempre.
- Se restauró la columna "Última acción" (`p.actor_ultima_accion`) que la
  variante A del prototipo había omitido — dos tests existentes (Grupo 11,
  Ronda 2) dependen de que ese dato sea visible en la lista.
- `tests/web/test_packages.py`: `test_paginacion_con_mas_de_20_paquetes` →
  renombrado `..._10_paquetes`, ajustada la página esperada (10/página, no
  20) para 25 paquetes de prueba.
- Todo el andamiaje del prototipo (switcher flotante, variantes B–E,
  parámetro `variant`) se descartó del código final — no queda ninguna
  referencia (`grep _prototipo_` sin resultados).

## Verificación

- `tests/web/` completo (463 tests) pasa.
- Verificación manual en navegador (Postgres efímero + Playwright, capturas
  enviadas al cliente): tabla renderiza con datos reales, búsqueda en vivo y
  filtros de Estado siguen funcionando, acciones reales (Recibir/Corregir/
  Entregar/Cancelar) probadas con clicks reales.
- Pendiente: confirmar en test.papyrus.com.co tras el próximo deploy (no
  desplegado todavía — cambios solo en working tree local).
