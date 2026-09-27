# 08 — Panorama: tendencia (▲▼ contra el periodo anterior + minigráfico de 7 días)

**What to build:** las tarjetas Ingresos, Entregados y Cancelados de Panorama ganan su indicador de
tendencia: la variación porcentual contra el MISMO TRAMO del periodo anterior, coloreada según convenga,
y un minigráfico de los últimos 7 días.

**Blocked by:** 06 (Ingresos ya existe desde el 01; Entregados/Cancelados los trae el 06)

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `domain/estadisticas_tablero_service.py`)

- [ ] Cada una de las tres columnas (Hoy, Semana, Mes) de Ingresos, Entregados y Cancelados muestra su
      variación ▲▼ contra el mismo tramo del periodo anterior: Hoy vs. ayer hasta esta misma hora;
      Semana vs. la semana anterior hasta el mismo día de la semana y hora; Mes vs. el mes anterior hasta
      el mismo día del mes y hora (si el mes anterior es más corto, se recorta a su último día).
- [ ] Variación = (actual − anterior) ÷ anterior. Cuando el periodo anterior vale 0, no se muestra
      ningún porcentaje (ni infinito, ni un guion que confunda con "0%") — se prueba explícitamente este
      caso.
- [ ] El color de la flecha depende de la métrica: en Ingresos y Entregados, subir es verde y bajar es
      rojo; en Cancelados, bajar es verde y subir es rojo.
- [ ] Cada una de las tres tarjetas muestra un minigráfico de los últimos 7 días (incluido el día actual,
      en hora de Colombia).
- [ ] Prueba de dominio con un reloj fijo a media mañana de un día conocido, que arma cobros/entregas de
      "hoy hasta ahora" y "ayer hasta la misma hora" y verifica que la comparación NO se ve falseada por
      la hora del día (el caso que motivó este ticket: comparar el día completo de ayer contra medio día
      de hoy daría una caída falsa).
