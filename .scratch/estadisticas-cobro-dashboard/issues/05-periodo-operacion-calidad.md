# 05 — Periodo seleccionado: Operación y calidad

**What to build:** la categoría "Operación y calidad" de Periodo seleccionado — quién entrega más, cuándo
hay más movimiento, y tres indicadores de calidad del proceso.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] "Operador con más entregas" muestra el nombre del Usuario (staff) con más entregas en el periodo y
      cuántas.
- [ ] "Día más activo" muestra el día de la semana (lunes a domingo, en hora de Colombia) con más
      entregas del periodo y qué % de las entregas concentra.
- [ ] "Hora pico" muestra la franja de una hora (hora de Colombia) con más entregas del periodo, con
      formato legible (ej. "6 – 7 p. m.").
- [ ] "% entregados dentro de las 48 h", "% extra-dimensionados" y "% recibidos abiertos o en mal estado"
      (condición ABIERTO o REGULAR) se calculan sobre los paquetes recibidos/entregados del periodo según
      corresponda.
- [ ] Un empate en "día más activo" u "hora pico" se resuelve siempre igual (día: el primero en orden
      lunes→domingo; hora: la primera franja del día) — determinista entre cargas.
- [ ] Matriz de "no aplica": Tipo acota Operador top, Día pico, Hora pico, % dentro de 48h y % en mal
      estado; Tipo NO acota % extra-dimensionados (se atenúa: ese indicador ES sobre el tipo, filtrar por
      tipo no tendría sentido). Cobrado/Anulado no acota ninguna tarjeta de esta categoría.
- [ ] Prueba de dominio que arma entregas concentradas en un día/hora conocidos y verifica que "día más
      activo"/"hora pico" los detecta correctamente, incluyendo un caso de empate.
