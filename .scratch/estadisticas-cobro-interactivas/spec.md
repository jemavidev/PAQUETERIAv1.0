Status: ready-for-agent
Feature: estadisticas-cobro-interactivas
Branch: PaqueteXv.2
Fuente de verdad: sesión de `/grilling` con el cliente (esta conversación) · `.scratch/cobro-bodegaje/spec.md`
(módulo original, historia 14-16 — esta es una extensión de solo lectura sobre la misma pantalla)

---

## Problem Statement

`/administracion/estadisticas-cobro` es la única pantalla de `/administracion` que no se parece al
resto del aplicativo: layout angosto de una sola columna (`max-w-2xl` contra el `max-w-7xl` que ya
usan `/paquetes` y `/residentes`), un `<form method="get">` de recarga completa de página en vez de
la actualización en vivo (fetch, sin recargar) que el resto del staff ya da por hecho, y solo dos
filtros posibles (Desde/Hasta). Los agregados que muestra hoy son mínimos: cantidad total, monto
total, tiempo promedio de bodegaje, y un desglose por apartamento — sin poder ver cuánto vino de
paquetes Normales contra Extra-dimensionados, cuánto se cobró de verdad contra cuánto se anuló, qué
miembro del staff registró cada cobro, ni cómo se distribuyó día a día dentro del rango elegido. El
admin que quiere responder algo tan simple como "¿cuánto se anuló esta semana y quién cobró más?"
hoy no puede — tiene que confiar en memoria o revisar paquete por paquete.

## Solution

La pantalla se rediseña con el mismo lenguaje visual e interactivo que `/paquetes`: layout ancho
(`max-w-7xl`), una barra de filtros que actualiza todo en vivo por `fetch` (sin recargar la página,
mismo convenio `X-Requested-With: fetch` que ya usa `/paquetes`), y una granularidad mucho mayor
sobre los mismos datos que el sistema ya guarda (`Cobro` + `Paquete`).

La barra de filtros gana:
- **Atajos de fecha** (Hoy · Ayer · Esta semana · Este mes · Últimos 7 días · Últimos 30 días),
  además de los selectores Desde/Hasta manuales de siempre.
- **Tipo de paquete** (Normal / Extra-dimensionado) como pills cliqueables de selección única con
  toggle (mismo mecanismo que los íconos de Estado en `/paquetes` — clic sobre el ya activo vuelve
  a "todos").
- **Cobrado / Anulado** como un segundo grupo de pills, mismo mecanismo — separa los cobros que
  realmente se cobraron de los que el staff anuló a "$0".
- **Usuario que registró el cobro**, como un `<select>` que acota el resto de la vista a un solo
  miembro del staff.

Todos estos filtros combinan entre sí (AND) y con el rango de fechas. Cada cambio de cualquiera de
ellos dispara un `fetch` inmediato (sin debounce — no hay campo de texto libre en esta vista) que
reemplaza el bloque de resultados completo, igual que hace `_busqueda_filtros.html` en `/paquetes`.

Los resultados ganan tres secciones nuevas, además de lo que ya existía (cantidad, monto total,
tiempo promedio de bodegaje, desglose por apartamento — los cuatro ahora también respetan los
filtros nuevos):

- **Por usuario**: tabla comparativa de todo el staff que registró al menos un cobro en el rango y
  filtros activos (cantidad y monto de cada uno, lado a lado) — a diferencia del resto de la vista,
  esta tabla ignora el propio `<select>` de Usuario (si lo hiciera, dejaría de servir para comparar)
  pero sí respeta fecha/tipo/cobrado-anulado.
- **Serie diaria**: una fila por cada día del rango (incluidos los días sin ningún cobro, en $0),
  con su cantidad y monto — para ver tendencia en vez de un solo total acumulado. Sin gráficos ni
  barras: una tabla numérica, consistente con que ninguna otra vista del aplicativo usa
  visualización de datos todavía.

Tanto "Por apartamento" (ya existente) como las dos tablas nuevas ("Por usuario" y "Serie diaria")
pueden crecer más allá de lo razonable para una sola pantalla con el rango por defecto de 30 días o
uno más largo — las tres se paginan de forma independiente con un control simple y propio
(Anterior/Siguiente + "Página X de Y"), nuevo macro compartido en `components/` porque el
`_paginacion.html` existente está construido para una sola lista por página (IDs y hook JS
globales, más la píldora flotante mobile) y no soporta tres instancias simultáneas.

Sin filtros, la carga inicial pasa de "solo hoy" a los **últimos 30 días** — suficiente cuerpo para
que la serie diaria y los desgloses nuevos tengan sentido de entrada.

## User Stories

1. Como admin, al entrar a `/administracion/estadisticas-cobro` sin ningún filtro, quiero ver el
   layout ancho (`max-w-7xl`) con la barra de filtros y las tarjetas/tablas distribuidas en varias
   columnas, para que la pantalla se sienta parte del mismo aplicativo que `/paquetes` y
   `/residentes`, no una pantalla aparte.
2. Como admin, al cargar la pantalla sin ningún filtro, quiero que el rango por defecto sean los
   últimos 30 días (no solo el día de hoy como hasta ahora), para que la serie diaria y los
   desgloses nuevos muestren algo con cuerpo sin tener que tocar nada primero.
3. Como admin, al cambiar Desde, Hasta, un atajo de fecha, un pill de Tipo, un pill de Cobrado/
   Anulado, o el `<select>` de Usuario, quiero que los resultados se actualicen solos por `fetch`
   sin recargar la página completa, para no perder la posición de scroll ni esperar un round-trip
   de página completa por cada ajuste.
4. Como admin, quiero atajos de fecha (Hoy, Ayer, Esta semana, Este mes, Últimos 7 días, Últimos 30
   días) que ajusten Desde/Hasta con un solo clic y disparen la actualización en vivo, para no
   tener que calcular ni escribir fechas a mano para los rangos que más uso.
5. Como admin, quiero poder seguir escribiendo un rango personalizado en Desde/Hasta en cualquier
   momento, para los casos que ningún atajo cubre.
6. Como admin, quiero filtrar por Tipo de paquete (Normal / Extra-dimensionado) con un clic sobre
   un pill, mismo mecanismo que los íconos de Estado de `/paquetes` (clic sobre el ya activo lo
   desactiva, vuelve a "todos"), para ver cuánto se cobró de cada tipo sin tener que hacer la resta
   a mano.
7. Como admin, quiero filtrar por Cobrado / Anulado con el mismo mecanismo de pill, para separar lo
   que realmente se cobró de lo que el staff anuló a "$0", algo que hoy queda mezclado en un solo
   número de "cantidad".
8. Como admin, quiero que Tipo de paquete y Cobrado/Anulado se puedan combinar entre sí y con el
   rango de fechas (ej. "solo Extra-dimensionados anulados de esta semana"), para acotar tanto como
   necesite sin tener que consultar varias veces por separado.
9. Como admin, quiero un `<select>` de Usuario que acote TODA la vista (tarjetas, por apartamento,
   serie diaria) a un solo miembro del staff, para revisar el trabajo de una persona puntual.
10. Como admin, quiero ver una tabla "Por usuario" con TODO el staff que registró al menos un cobro
    en el rango/filtros activos, comparados lado a lado (cantidad y monto de cada uno), sin tener
    que elegir a cada uno por turno en el `<select>` para armar la comparación yo mismo.
11. Como admin, quiero que esa tabla "Por usuario" respete el rango de fechas, Tipo y Cobrado/
    Anulado, pero NO el propio `<select>` de Usuario, para que siga sirviendo de comparación aunque
    ya haya acotado el resto de la vista a una persona.
12. Como admin, quiero una tabla "Serie diaria" con una fila por cada día del rango elegido
    (cantidad y monto de ese día), incluidos los días sin ningún cobro (en $0), para ver la
    tendencia real día a día en vez de un solo acumulado.
13. Como admin, NO quiero que la serie diaria se muestre como gráfico o barras — una tabla numérica
    simple, para que la pantalla se mantenga consistente con el resto del aplicativo (ninguna otra
    vista usa visualización de datos hoy).
14. Como admin, si elijo un rango largo (ej. un año completo), quiero que "Por apartamento", "Por
    usuario" y "Serie diaria" se paginen de forma independiente (Anterior/Siguiente + "Página X de
    Y" cada una), para que ninguna tabla se vuelva inmanejable ni tire abajo el resto de la
    pantalla.
15. Como admin, quiero que cambiar de página en cualquiera de esas tres tablas también sea en vivo
    (fetch, sin recargar), consistente con el resto de la interacción de la pantalla.
16. Como admin, quiero que las tarjetas existentes (cantidad, monto total, tiempo promedio de
    bodegaje) y el desglose "Por apartamento" ya existente respeten TODOS los filtros nuevos (Tipo,
    Cobrado/Anulado, Usuario), no solo el rango de fechas como hoy.
17. Como admin, si el rango/filtros activos no arrojan ningún cobro, quiero ver un estado vacío
    claro en cada sección (mismo criterio que "Sin cobros en este rango." que ya existe hoy), no
    tablas rotas ni un error.
18. Como admin, quiero que la pantalla siga funcionando correctamente en mobile (una sola columna,
    controles apilados), con el mismo criterio responsivo (`flex-wrap`, breakpoints `md:`) que ya
    usa el resto del aplicativo.
19. Como operador (no admin), quiero seguir sin poder acceder a esta pantalla en absoluto (403),
    sin cambios respecto al comportamiento actual.
20. Como sistema, quiero que ninguno de los filtros nuevos pueda alterar ni crear ningún `Cobro` —
    esta pantalla sigue siendo estrictamente de solo lectura.

## Implementation Decisions

- **Filtros como objeto único**: nuevo dataclass `FiltrosEstadisticasCobro` (`cobro_service.py`) —
  agrupa `desde`, `hasta`, `tipo: TipoPaquete | None`, `anulado: bool | None` (`None` = ambos,
  `False` = solo cobrados, `True` = solo anulados), `usuario_id: UUID | None`,
  `pagina_apartamento`, `pagina_usuario`, `pagina_diario` (cada una default `1`) — evita que
  `estadisticas_cobro()` termine con ocho parámetros posicionales sueltos.
- **`estadisticas_cobro(session, filtros: FiltrosEstadisticasCobro) -> EstadisticasCobro`**: mismo
  nombre y ubicación (`cobro_service.py`), firma nueva. La query base gana `.filter()` condicionales
  por `Paquete.package_type`, `Cobro.motivo_anulacion IS (NOT) NULL`, y
  `Cobro.cobrado_por_usuario_id` cuando cada filtro está activo — todas las secciones (cantidad,
  monto total, tiempo promedio de bodegaje, por apartamento, serie diaria) parten de la MISMA query
  base filtrada. La tabla "Por usuario" corre su propia query que aplica fecha/tipo/anulado pero
  deliberadamente **no** aplica `usuario_id` (ver historia 11).
- **`EstadisticasCobro` (dataclass existente) gana campos nuevos**: `por_usuario: list[
  FilaEstadisticaUsuario]`, `total_paginas_usuario: int`, `serie_diaria: list[FilaEstadisticaDiaria]`,
  `total_paginas_diario: int`, `total_paginas_apartamento: int` (pagina esa lista, que hoy vuelve
  completa). Constante `_FILAS_POR_PAGINA = 20` para las tres tablas paginadas.
- **Nuevos dataclasses** (mismo molde que `FilaEstadisticaApartamento` ya existente):
  `FilaEstadisticaUsuario` (`usuario_id`, `nombre`, `cantidad`, `monto_total`) y
  `FilaEstadisticaDiaria` (`fecha: date`, `cantidad`, `monto_total`).
- **Serie diaria — todos los días, no solo los que tuvieron cobros**: se genera la lista completa de
  fechas entre `desde` y `hasta` (inclusive) en Python y se hace `LEFT JOIN`/mapeo contra los
  agregados reales por día — un día sin cobros aparece igual, con `cantidad=0, monto_total=0`.
  Orden cronológico ascendente (el más antiguo primero); la página 1 es el inicio del rango.
- **`Usuario` para el `<select>`**: lista completa de staff (`ADMIN` + `OPERADOR`), ordenada por
  `nombre` — se resuelve UNA vez en la carga completa de página (no en cada fetch en vivo), mismo
  criterio que `conteos_estado`/`conteos_conectados` en `/paquetes` (`packages.py`): el `<select>`
  vive en la barra de filtros, fuera del contenedor que el fetch reemplaza.
- **Ruta `GET /administracion/estadisticas-cobro`** (`admin.py`, misma ruta): gana query params
  `tipo`, `anulado`, `usuario_id`, `pagina_apartamento`, `pagina_usuario`, `pagina_diario`, además de
  los `desde`/`hasta` ya existentes. Mismo convenio que `packages.py`: si el header
  `X-Requested-With` es `fetch`, devuelve SOLO el fragmento de resultados
  (`admin/_estadisticas_cobro_resultados.html`); si no, la página completa
  (`admin/estadisticas_cobro.html`, que incluye ese mismo fragmento en la carga inicial). Rango por
  defecto sin `desde`/`hasta`: últimos 30 días (antes: solo hoy). Sin cambios en `require_admin`.
- **Barra de filtros propia, NO una reutilización de `busqueda_filtros()`**: ese macro compartido
  tiene su JS acoplado a los campos `q`/`estado`/`vista`/`conectados` únicamente — generalizarlo
  para nuestros filtros nuevos (`tipo`, `anulado`, `usuario_id`, atajos de fecha) arriesgaría romper
  `/paquetes` y `/residentes`, sus dos callers actuales. Esta vista arma su propio `<form>` + script,
  pero **reutiliza el lenguaje visual** ya fijado: la clase compartida `icono_estado_base` y el
  patrón de 3 estados por pill (`suave`/`activo`/`opacado`, con `data-*` + repintado JS) que ya usan
  `filtro_estado()` y `filtro_vista_residentes()` en `_busqueda_filtros.html`. Paletas de color
  propias para Tipo y Cobrado/Anulado, distintas entre sí y de los 4 colores ya fijados de Estado de
  Paquete (mismo criterio ya usado para elegir la paleta de `filtro_vista_residentes`).
  Actualización sin debounce (no hay texto libre en esta vista) con `AbortController`, mismo
  criterio de cancelar la petición anterior que ya usa `_busqueda_filtros.html`.
  Los atajos de fecha son botones que solo ESCRIBEN Desde/Hasta (client-side, sin ida al servidor
  aparte) y disparan la misma función `actualizar()`.
- **Nuevo macro compartido `components/_paginacion_simple.html`**: `paginacion_simple(id,
  pagina_actual, total_paginas, on_click_js)` (o equivalente) — Anterior/Siguiente + "Página X de
  Y", sin píldora flotante ni sticky (esta pantalla no es una lista larga de scroll continuo como
  `/paquetes`), parametrizado por `id` para poder instanciarse 3 veces sin colisión de IDs/handlers.
  Oculto (o deshabilitado) cuando `total_paginas <= 1`.
- **Nuevo fragmento `admin/_estadisticas_cobro_resultados.html`**: tarjetas (cantidad, monto total,
  tiempo promedio de bodegaje), tabla "Por apartamento" + su paginación, tabla "Por usuario" + su
  paginación, tabla "Serie diaria" + su paginación — todo lo que el fetch en vivo reemplaza,
  análogo a `packages/_resultados.html`.
- **Sin cambios** en `Cobro`, `Paquete`, `TarifaCobro`, `MotivoAnulacionCobro`, ni en el endpoint de
  `Entregar` — esta pantalla sigue leyendo, nunca escribe.

## Testing Decisions

Buen test acá = observar comportamiento externo (qué devuelve `estadisticas_cobro()`, qué HTML/
fragmento devuelve la ruta) — nunca aserciones sobre el código interno.

- **Seam 1 — `estadisticas_cobro()` con `Postgres` real** (`tests/data_model/
  test_cobro_service_integration.py`, prior art directo — ya cubre rango, desglose por apartamento,
  cobros anulados en el total): agregar casos para `filtros.tipo` (crear cobros de ambos
  `TipoPaquete` en el rango, confirmar que cada filtro devuelve solo el suyo); `filtros.anulado`
  (`True`/`False`/`None` devuelven los subconjuntos correctos); `filtros.usuario_id` (acota
  cantidad/monto/por-apartamento/serie-diaria a un solo `cobrado_por_usuario_id`, pero NO la tabla
  `por_usuario`); combinación de varios filtros a la vez (AND); serie diaria incluye días sin
  ningún cobro en $0 y respeta el rango completo; paginación de las 3 tablas (total de páginas
  correcto, página fuera de rango se comporta con sensatez, cada página trae exactamente las filas
  que le tocan).
- **Seam 2 — `GET /administracion/estadisticas-cobro`** (`tests/web/test_admin_estadisticas_cobro.py`,
  prior art directo — ya cubre 403 para operador, redirect sin sesión, default de hoy): actualizar
  el test de default a "últimos 30 días"; nuevos query params (`tipo`, `anulado`, `usuario_id`,
  `pagina_*`) se reflejan en el HTML devuelto; con el header `X-Requested-With: fetch` la respuesta
  es solo el fragmento (sin `<html>`/layout alrededor), igual que ya se prueba para `/paquetes` en
  `tests/web/test_packages.py`; sin ese header, la página completa incluye el mismo fragmento.
- Sin seam nuevo para el macro `_paginacion_simple.html` en sí (es HTML/JS puro, sin lógica de
  servidor) — se cubre indirectamente vía el HTML devuelto por Seam 2 (número de página actual,
  controles deshabilitados cuando corresponde).

## Out of Scope

- Exportar cualquiera de estas estadísticas a CSV/Excel.
- Gráficos, barras o cualquier visualización de datos — todo queda en tarjetas y tablas numéricas,
  consistente con el resto del aplicativo.
- Desglose de "Anulados" por motivo de anulación (`MotivoAnulacionCobro`) — el pill "Anulado" separa
  el conteo/monto, pero no abre un sub-desglose por motivo dentro de esta iteración.
- Bucketing automático de la serie diaria por semana/mes en rangos largos — siempre es por día,
  paginada (decisión explícita del cliente, ver `grilling`).
- Cualquier filtro sobre `snapshot_torre`/`snapshot_apartamento`/`recipient_phone` más allá de lo
  que "Por apartamento" ya muestra hoy (esa tabla no gana un filtro de texto libre propio).
- Cambios a `busqueda_filtros()` (`components/_busqueda_filtros.html`) o a sus callers existentes
  (`/paquetes`, `/residentes`) — esta pantalla arma su propia barra, sin tocar ese macro compartido.
- Cambios al componente `_paginacion.html` existente — se deja intacto para sus callers actuales;
  `_paginacion_simple.html` es un componente nuevo y separado.

## Further Notes

- Un desglose por motivo de anulación dentro del pill "Anulado" (ver Out of Scope) es un follow-up
  natural si el cliente lo pide después de usar esta versión — no se construyó ahora porque la
  sesión de `/grilling` lo dejó fuera del alcance confirmado explícitamente.
- El `<select>` de Usuario lista TODO el staff (`ADMIN` + `OPERADOR`) sin importar si tiene o no
  cobros en el rango activo — si en la práctica resulta confuso ver usuarios sin actividad en la
  lista, acotar esa lista a quienes sí tienen cobros en el rango es un ajuste chico y aislado a
  futuro, no estructural.
