# 03 — Periodo seleccionado: Recaudo completo

**What to build:** el resto de la categoría "Recaudo" de la zona Periodo seleccionado (ya tiene el Total
de ingresos del ticket 01): promedio por paquete, desglose bodegaje/servicio, lo exonerado por
anulaciones, las exenciones por primera entrega y el cobro más alto.

**Blocked by:** 02

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `domain/estadisticas_tablero_service.py`)

- [ ] "Promedio recaudado por paquete" = Total de ingresos ÷ cantidad de cobros del periodo.
- [ ] "Recaudado por bodegaje" y "Recaudado por servicio" muestran su suma y su % sobre el Total de
      ingresos (ambos porcentajes suman 100 %).
- [ ] "Exonerado por anulaciones" muestra el monto ESTIMADO con las tarifas de servicio vigentes según el
      Tipo de cada paquete anulado, junto con cuántas anulaciones hubo y su tasa sobre el total de
      cobros del periodo; la tarjeta deja claro que es una estimación (los cobros no guardan lo
      perdonado).
- [ ] "Exenciones por primera entrega" muestra cuántas hubo (cobros con servicio en 0 y sin motivo de
      anulación) y el monto estimado que se dejó de cobrar por ellas, con la misma aclaración de
      estimación.
- [ ] "Cobro más alto" muestra el mayor total de un cobro del periodo y sus días en bodega.
- [ ] Matriz de "no aplica" de esta categoría: Tipo y Cobrado/Anulado acotan Total de ingresos, Promedio,
      Bodegaje, Servicio y Cobro más alto; Tipo acota Exenciones por primera entrega pero Cobrado/Anulado
      NO (queda atenuada con esa nota — tiene sentido, exención y anulación son mutuamente excluyentes).
- [ ] Prueba de dominio que compara la estimación contra un escenario armado a mano (tarifas conocidas,
      unos cuantos cobros anulados y exentos) para verificar la aritmética exacta.
