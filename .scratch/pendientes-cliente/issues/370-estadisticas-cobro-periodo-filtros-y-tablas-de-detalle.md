# 370 — `/administracion/estadisticas-cobro`: botones de periodo, íconos de filtro y tablas de detalle — propuesta para ver antes de decidir

**Pedido original (Jesús):** "necesito que los botones [Hoy · Ayer · Esta semana · Este
mes · 3 últimos meses · Semestre] me digas que podemos hacer con ellos,
posiblemente al final una pequeña tabla para filtrar paquetes, algo resumido, que
me puedes sugerir para saber como lo aprovechamos, seria otra forma de ver lo que
existe con las tarjetas pero de otra forma analiza y dime que pienzas. Ademas
existen algunos iconos a la derecha de esto dime tambien que se puede hacer".
Después de ver el análisis: "muestrame lo que cambiaria, pero no modifiques lo que
se tiene actualmente".

**Status:** pendiente (propuesta prototipada en vivo, separada de lo actual; falta
que Jesús decida qué se queda)

## Análisis que se le entregó

Las tarjetas responden *cuánto*; falta *cuáles*. Hallazgos que sostienen la
propuesta:

- `/paquetes` acepta `estado`, `q`, `pagina`, `conectados` y los deep links `ver`,
  `entregar`, `recibir`, `corregir` -- NO acepta rango, Tipo ni cobro. Darle esos
  filtros toca la pantalla más usada del personal, así que la tabla no se plantea
  como un "mini /paquetes" sino como los paquetes detrás de las cifras, con el
  código enlazando a `/paquetes?ver=`.
- La estimación de bodegaje por paquete ya se calcula (en lote) dentro de "Por
  cobrar en bodega"; la tabla "Requieren atención" solo la expone por fila.
- Ya hay precedente de exportación CSV (contactos externos).
- `snapshot_torre` existe en 1.579 de 1.615 paquetes (10 torres) -- Torre es
  viable como filtro, pero suma una dimensión a la matriz de "no aplica".

## Qué se propone (y se muestra en el prototipo)

1. **Periodo:** fechas exactas bajo los botones ("Este mes · 1-21 sep 2026"),
   botón nuevo "Mes anterior" (calendario), comparación contra el periodo anterior
   (▲▼) y gráfico de evolución cuya granularidad la fija el botón (hora / día /
   semana / mes).
2. **Íconos de filtro → chips con texto y conteo** en dos grupos rotulados ("Tipo",
   "Cobro"), "Anulado" → "Cobro anulado" (se confunde con "Cancelado", que es el
   paquete), y **Torre** como filtro nuevo.
3. **Dos tablas cortas:** "Requieren atención" (Ahora: los 10 con más tiempo en
   bodega, con bodegaje por cobrar) y una tabla del Periodo con vistas
   (Mayores cobros · Anulados · Cancelados), sujeta a los mismos filtros, con
   "Descargar CSV".
4. **Móvil:** periodo en una fila deslizable y el resto de filtros tras un botón
   "Filtros (n)".

## Proceso y aislamiento

`prototype` (UI, sub-forma A): la misma ruta, en un worktree aparte con su propio
servidor (`:8011`, misma BD dev) y su propia rama
(`prototipo/estadisticas-cobro-filtros-y-tablas`, sin push, no se mergea). Lo actual
(`:8010`, commit `c9f5149`) no se toca. Lo que se pregunta y sigue abierto:
¿las tablas son para actuar (Ahora), auditar (Periodo) o ambas?, ¿CSV?, ¿"Mes
anterior" y el renombre de "Anulado"?, ¿Torre?

## Prototipo (2026-09-21)

Rama `prototipo/estadisticas-cobro-filtros-y-tablas` (commit `00c4f97`, sin push, NO se
mergea), en un worktree aparte con su propio servidor (`:8011`, misma BD dev). Lo actual
(`:8010`, commit `c9f5149`) no se tocó -- verificado en navegador y con `git diff`.

Incluye TODO lo propuesto, con datos reales:

- **Periodo:** fechas exactas bajo el título y en el encabezado del Periodo, botón "Mes anterior",
  comparación contra el periodo anterior (ingresos, paquetes, entregados, cancelados; con la
  matriz de "no aplica") y gráfico de evolución (barras de ingresos + líneas de entregados y
  cancelados) con granularidad hora / día / semana / mes según el botón.
- **Filtros:** chips con texto y conteo facetado en "Tipo" y "Cobro" ("Anulado" → "Cobro
  anulado"), Torre como selector, "Quitar filtros", y en móvil el periodo en una fila deslizable
  con el resto tras "Filtros (n)".
- **Tablas:** "Requieren atención" (Ahora: en bodega + anuncios sin llegar, lo más viejo
  primero, agrupado para que se vean ambos tipos) y "Detrás de las cifras" (Periodo: mayores
  cobros / cobros anulados / paquetes cancelados, con los mismos filtros), con enlace a
  `/paquetes?ver=` y "Descargar CSV" de todas las filas (el CSV hereda los filtros; UTF-8 con BOM).

**Verificado:** los totales de la comparación y del gráfico coinciden con las tarjetas en 6
periodos; 17 combinaciones de filtros renderizan sin error y los valores inválidos se ignoran;
prueba en navegador de fechas vivas, conteos facetados, Torre, vistas, CSV (cabecera, BOM y
nº de filas = botón), enlace al paquete y colapso móvil; sin errores de consola. **Costo:**
tiempo de respuesta igual al de la pantalla actual (p. ej. semestre 1,00 s vs 1,01 s).

**Decisiones de diseño que quedan abiertas** (además de las 4 preguntas de arriba):
- Torre acota solo Recaudo y Paquetes; Clientes, Operación y SMS se atenúan con "no depende de
  Torre". ¿Se quiere que también los acote (más trabajo)?
- "Hoy"/"Ayer" comparan días completos (hoy va a medio día, así que casi siempre sale ▲ enorme);
  el Panorama sí compara "hasta la misma hora". ¿Se unifica?
- Con el rango explícito `AAAA-MM-DD..AAAA-MM-DD` (solo lo usa la comparación) no se deben
  exponer fechas sueltas: Jesús las quitó a propósito (issue 364). En la versión real, el
  periodo anterior se calcula por dentro, no por la URL.

**Ojo con la BD dev al mirar la propuesta:** el 21-sep entre las 6:55 y las 7:10 alguien entregó
67 paquetes (57 salían de bodega, algunos con 300+ días) → "Hoy" y "Este mes" muestran
$2.675.000 en un solo día y la bodega quedó en 2. El gráfico de "Este mes" queda dominado por
esa barra; "Mes anterior" o "3 últimos meses" muestran una forma representativa. No fue esta
tarea.

Para retirarlo: parar el servidor de `:8011`, `git worktree remove --force
/tmp/claude-1000/-home-stk-Documents-GIT-MATT/proto370` (la rama queda).
