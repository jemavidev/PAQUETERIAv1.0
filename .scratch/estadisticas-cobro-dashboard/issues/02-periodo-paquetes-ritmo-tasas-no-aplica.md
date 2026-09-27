# 02 — Periodo seleccionado: Paquetes, Ritmo y tasas + matriz de «no aplica»

**What to build:** el resto de la categoría "Paquetes" y la categoría "Ritmo y tasas" de la zona Periodo
seleccionado, y con ellas el mecanismo de atenuado que van a reutilizar todos los tickets de Periodo que
siguen (03, 04, 05, 14): la matriz de qué filtro (Tipo, Cobrado/Anulado) acota cada tarjeta, y cómo se ve
una tarjeta a la que un filtro activo no le aplica.

**Blocked by:** 01

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: 1a4d74b)

- [ ] "Paquetes" muestra: Total de paquetes (con cualquier movimiento en el periodo), Anunciados,
      Recibidos, Entregados y Cancelados, cada uno por la fecha de su propio evento dentro del periodo.
- [ ] "Ritmo y tasas" muestra: ritmo de Anunciados, Recibidos y Entregados por día/semana/mes dentro del
      periodo (total del periodo ÷ días locales × 1, × 7, × 30; con "todos los datos" los días van desde
      el primer movimiento hasta hoy), Tasa de entrega (entregados ÷ cerrados) y Tasa de cancelación
      (cancelados ÷ cerrados) — ambas por fecha de cierre y sumando 100 %.
- [ ] Sin ningún paquete cerrado en el periodo, las dos tasas muestran "—", no un error ni "0%".
- [ ] Activar el filtro Tipo (Normal / Extra-dimensionado) acota: Recibidos, Entregados, ritmo de
      Recibidos y ritmo de Entregados. NO acota: Total de paquetes, Anunciados, Cancelados, ritmo de
      Anunciados, ni las dos tasas — estas quedan atenuadas (opacidad reducida, escala de grises) con la
      nota "no depende de Tipo" mientras el filtro está activo, y siguen mostrando su valor SIN filtrar.
- [ ] El filtro Cobrado/Anulado no acota ninguna tarjeta de esta categoría — todas se atenúan con "no
      depende de Cobrado/Anulado" mientras esté activo.
- [ ] Con ambos filtros activos a la vez, una tarjeta atenuada por los dos junta ambos motivos en su nota
      (ej. "no depende de Tipo ni de Cobrado/Anulado").
- [ ] Prueba de dominio (Postgres real, reloj fijo) que cubre la matriz completa de esta categoría —
      qué tarjeta cambia con cada filtro y cuál no.
