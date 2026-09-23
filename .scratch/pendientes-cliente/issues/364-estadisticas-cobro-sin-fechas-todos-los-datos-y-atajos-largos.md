# 364 — `/administracion/estadisticas-cobro`: sin "Desde/Hasta", carga con todos los datos y se filtra con atajos (+ 3 últimos meses, Semestre, Último año)

**Pedido original (Jesús):** "Remueve los filtros para seleccionar por fechas
'Desde y Hasta', la idea es que siempre se muestren todos los datos
existentes al cargar la vista por primera vez y poder ir buscando o
filtrando por 'Hoy Ayer Esta semana Este mes', a estos filtros agrega '3
últimos meses' y 'semestre' y 'último año'".

**Status:** implementado, pendiente confirmar visualmente

Tests:
- `tests/web/test_admin_estadisticas_cobro.py`: primera carga con todos los
  datos, cada atajo acota con el `hoy` del navegador (fechas fijas),
  clave/`hoy` inválidos y `desde`/`hasta` sueltos ignorados, combinación con
  Tipo, barra de filtros (7 atajos, sin campos de fecha), atajo activo
  resaltado, y el cálculo puro de `_rango_estadisticas_cobro` (fin de mes,
  bisiesto, cruce de año).
- `tests/data_model/test_cobro_service_integration.py`: rango abierto en el
  dominio (todos los cobros, serie diaria del primer cobro a hoy, paginación de
  un historial largo, eje estable al alternar otros filtros, sin cobros, un solo
  extremo).

Verificado además en el navegador local: activar/quitar cada atajo, cambiar de
uno a otro, combinarlo con el filtro de Tipo; sin errores de consola. Ojo: con
los datos demo actuales (90 días, `paquetex_dev_seed_cobros.py`), "3 últimos
meses", "Semestre" y "Último año" muestran los mismos totales -- para ver la
diferencia hay que sembrar más historia (`--reiniciar --dias 400`).

Sigue a [[361]] (quitó "Últimos 7/30 días") y [[363]] (quitó el select de
Usuario). Sustituye la decisión de 361 de conservar el rango inicial de 30
días: ahora la primera carga no tiene rango.

## Decisiones

- **Sin rango = sin límite, "todos los datos".** `FiltrosEstadisticasCobro.desde`
  y `.hasta` pasan a ser opcionales (`None` = sin límite). La primera carga ya
  no aplica los últimos 30 días.
- **Serie diaria sin rango:** va del día del primer cobro hasta hoy (o el del
  último cobro, si fuera posterior). Los extremos se resuelven contra TODOS
  los cobros, no contra los ya filtrados por Tipo/Cobrado-Anulado, para que el
  eje de días no se mueva al alternar esos filtros. Sin ningún cobro, la serie
  queda vacía ("Sin cobros en este rango.").
- **Los atajos son ahora el único control de fechas**, así que ya no pueden ser
  botones sin estado: se resaltan cuando están activos (azul primario, mismo
  lenguaje que el resto de la app) y un segundo clic vuelve a "todos los datos"
  -- igual que las píldoras de Tipo y Cobrado/Anulado. Sin este resalte no
  habría forma de saber qué periodo cubren los números.
- **El rango lo calcula el servidor a partir de una clave**, no de fechas
  sueltas: parámetros `rango` (`hoy`, `ayer`, `semana`, `mes`, `tres_meses`,
  `semestre`, `anio`) y `hoy` (fecha LOCAL del navegador, para que "Hoy" sea el
  día del usuario y no el día UTC -- misma semántica que tenían los atajos
  cuando calculaban las fechas en el navegador). Los parámetros `desde`/`hasta`
  dejan de aceptarse: sin controles que los muestren serían un filtro
  invisible (mismo criterio que [[363]]). Una clave desconocida se ignora
  (= todos los datos).
- **Semántica de los nuevos** (ventanas móviles que terminan hoy, inclusive):
  "3 últimos meses" = 3 meses hacia atrás; "Semestre" = últimos 6 meses;
  "Último año" = últimos 12 meses. Empiezan el día siguiente a la misma fecha
  N meses atrás (ej. hoy 20-sep: 3 meses → 21-jun). Se interpretó "semestre"
  como ventana móvil y no como semestre calendario porque así el orden
  3 meses < semestre < año es coherente (en septiembre, un semestre calendario
  mostraría menos que "3 últimos meses"). Si se quisiera calendario, es una
  línea en `_rango_estadisticas_cobro`. Cada botón lleva un `title` que dice la
  ventana exacta.
- "Hoy / Ayer / Esta semana / Este mes" conservan su significado (esta semana
  = desde el lunes; este mes = desde el día 1).

## Nota (2026-09-20): superado por el rediseño de tablero

La pantalla pasó a `calcular_tablero` (`.scratch/estadisticas-cobro-dashboard`)
y el ticket 17 de esa feature retiró el servicio de listas
(`cobro_service.estadisticas_cobro`, `FiltrosEstadisticasCobro`, serie diaria
paginada) sobre el que corría la mitad de dominio de este issue -- incluidas
sus pruebas en `tests/data_model/test_cobro_service_integration.py`. El
pedido en sí SIGUE cumplido por el tablero: sin Desde/Hasta, primera carga con
todos los datos, 7 atajos (Hoy · Ayer · Esta semana · Este mes · 3 últimos
meses · Semestre · Último año) con el activo resaltado y segundo clic para
quitarlo. Las pruebas vigentes son `test_periodo_sin_rango_activo_son_todos_
los_datos` / `test_periodo_con_atajo_acota_al_rango` (dominio) y
`test_barra_de_filtros_tiene_los_siete_atajos_sin_fechas_sueltas` /
`test_el_atajo_activo_llega_resaltado` (web). Un cambio de fondo: el tablero
usa el reloj del servidor en hora de Colombia, ya no el `hoy` del navegador.
