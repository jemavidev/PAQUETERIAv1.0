# 10 — Ahora: Dinero (por cobrar en bodega + deuda contra entrega)

**What to build:** las dos tarjetas de dinero de la zona Ahora, con su punto azul propio.

**Blocked by:** 09

**Status:** ready-for-agent

- [ ] "Por cobrar en bodega" = suma, sobre los paquetes RECIBIDO actuales, del cobro que se calcularía SI
      se entregaran ahora mismo — misma aritmética y misma exención de primera entrega que ya usa el
      modal Entregar de `/paquetes` (reutilizada, no reimplementada aparte).
- [ ] "Deuda contra entrega" = suma de los saldos NEGATIVOS de las Personas (los saldos positivos no
      compensan), junto con cuántas Personas tienen saldo negativo.
- [ ] Ambas tarjetas llevan el punto azul de "dinero" y no cambian con los filtros de la barra.
- [ ] Prueba de dominio que compara "Por cobrar en bodega" contra entregar de verdad esos mismos paquetes
      en ese instante y sumar sus cobros reales — deben coincidir.
