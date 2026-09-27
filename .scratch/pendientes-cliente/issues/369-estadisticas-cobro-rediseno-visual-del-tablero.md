# 369 — `/administracion/estadisticas-cobro`: el tablero "no se ve nada agradable" — rediseño visual

**Pedido original (Jesús):** "no sé, pero creo que aplicaste sobre ingeniería y
/administracion/estadisticas-cobro no se ve nada agradable".

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Qué se ve hoy (capturas del tablero real, escritorio 1440 y móvil 390)

Diagnóstico propio, para que la conversación no dependa de memoria:

1. **~40 tarjetas del mismo peso.** No hay jerarquía: el ingreso del día
   pesa igual que "Hora pico". Nada dice "este es el número que importa".
2. **Etiqueta de categoría repetida en cada tarjeta** (RECAUDO, FOTO,
   DINERO, CLIENTES, RITMO, TASAS...) -- eso es un título de sección, no
   una etiqueta por tarjeta.
3. **Las 3 zonas (Panorama / Ahora / Periodo) no tienen título visible**: solo
   un riel de color a la izquierda; el texto que explica que Panorama y Ahora
   NO responden a los filtros es solo para lectores de pantalla.
4. **Texto cortado con "…"** en la propia pantalla: `$110,…` / `$345,…` en
   Ingresos, `Anuncio…` / `Perman…` / `Bodegaj…` en Tiempos promedio,
   "Paquete más antiguo".
5. **Cuadrícula irregular:** la tarjeta de SMS queda sola en una segunda fila
   con un hueco enorme; en Periodo hay filas con huecos y alturas dispares.
6. **Móvil:** ~7.500 px de tarjetas apiladas, una por métrica.
7. Los 4 íconos de filtro (cian / morado / verde / rojo) no dicen qué filtran.

## Alcance

Solo la presentación de los resultados (las 3 zonas): el cálculo del tablero
(`estadisticas_tablero_service`) y las reglas de "no aplica" no cambian. La
barra de filtros se evalúa aparte (punto 7) una vez elegida la estructura.

## Proceso

`prototype` (UI): 3 variantes estructuralmente distintas sobre la misma ruta,
conmutables con `?variant=`, en un worktree aparte (rama `prototipo/...`, no
toca el árbol de trabajo compartido ni main). La ganadora se pliega al código
real y las demás quedan solo en la rama del prototipo.

## Prototipo (2026-09-20)

Rama `prototipo/estadisticas-cobro-tablero-visual` (commit `ef8a7ec`, sin push,
NO se mergea a main), montada en un worktree aparte con su propio servidor
(`:8011`, misma BD dev) para no tocar el árbol compartido. Misma ruta, 4 vistas
con `?variant=actual|a|b|c` y un conmutador flotante (← →):

- **A · Ejecutivo** -- jerarquía: héroe de Ingresos + paneles con filas y
  barras de proporción (composición de la bodega, origen del recaudo, embudo de
  paquetes). Móvil ~4.800 px.
- **B · Reporte** -- una hoja tipográfica: Panorama como tabla real, el resto
  como listas "etiqueta ... valor", casi sin color. Móvil ~4.100 px (el
  Panorama se apila; una 1ra versión desbordaba la tabla y se corrigió).
- **C · Pestañas** -- una zona a la vez (Panorama / Ahora / Periodo); los
  filtros solo se ven en Periodo, que es lo único que los usa. Mosaicos
  uniformes, mosaico oscuro en "Total de ingresos". Móvil 1.200-3.000 px por
  pestaña.

Las 3 respetan la matriz de "no aplica" y el refresco en vivo conserva la
variante (probado en navegador). Hallazgo aparte: "Deuda contra entrega"
imprimía `$-280,000`; las variantes lo muestran `-$280,000` (`formato()` en
`_estadisticas_tarjetas.html` tiene el mismo detalle en el diseño actual).

**Pendiente:** que Jesús elija (o mezcle) y decida qué hacer con la barra de
filtros (los 4 íconos de color sin etiqueta), común a las tres.

## Resultado (2026-09-20)

Jesús eligió la **A · Ejecutivo** ("se ve mucho mejor"). Plegada al código real
(`_estadisticas_cobro_resultados.html` + `_estadisticas_tarjetas.html`),
reescrita, no copiada; B y C quedan solo en la rama del prototipo.

- Se borraron las 11 macros de "tarjeta" que ya nadie usaba; quedan formato,
  variación ▲▼, `spark`, `no_aplica` y `etiqueta_rango`.
- `formato(..., 'cop')` pone el signo antes del peso (`-$280,000`).
- **Corrección respecto al prototipo:** la primera versión de A atenuaba varios
  datos con un filtro activo sin decir "no depende de …" (Exenciones, barras de
  Paquetes, ritmo) y había perdido el pie del SMS con menos de 7 días de
  registro. Nuevo macro `metrica`/`dato` empareja atenuar + explicar y le pone a
  cada dato un `data-metrica`; las pruebas de la pantalla apuntan a ese
  identificador y hay una que verifica el emparejamiento para todos los datos
  y todas las combinaciones de filtros.
- Verificado en navegador contra la pantalla real: sin conmutador, 3 títulos de
  zona, ningún texto truncado, sin scroll horizontal, filtros en vivo (activar y
  quitar), atenuado + nota con Tipo activo, Panorama idéntico con filtros.
- 170 pruebas del módulo de cobro y la pantalla en verde.

**Observación aparte (no es del diseño):** "todos los datos" (sin atajo) tarda
~1,3 s en calcularse con los datos demo de la BD dev (1.600 paquetes), contra
0,3 s de "Esta semana"; "Último año" y cualquier combinación con Tipo también
rondan 1,2 s. Es el cálculo de `calcular_tablero`, no la plantilla.

**Sigue abierto:** la barra de filtros (los 4 íconos de color -- cian, morado,
verde, rojo -- no dicen qué filtran), que no cambió.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado, pendiente confirmar visualmente". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
