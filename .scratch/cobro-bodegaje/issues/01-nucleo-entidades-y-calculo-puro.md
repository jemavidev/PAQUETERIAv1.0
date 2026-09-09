# 01 — Núcleo: entidades de cobro + cálculo puro

**What to build:** las entidades `Cobro`, `TarifaCobro` (sembrada con los valores iniciales: $1.500
base Normal, $2.000 base Extra-dimensionado, $1.000 bodegaje/24h Normal, $1.500 bodegaje/24h
Extra-dimensionado) y `MotivoAnulacionCobro`, más la función pura `calcular_cobro(paquete, tarifas,
ahora)` que resuelve el desglose completo (cargo base + bodegaje, con la exención de primera
entrega aplicada solo al cargo base). Sin ninguna ruta ni UI todavía — es la base que el resto de
los tickets de este módulo usa.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `calcular_cobro` devuelve $1.500 para un paquete Normal sin primera entrega ni bodegaje
- [ ] `calcular_cobro` devuelve $2.000 para Extra-dimensionado en las mismas condiciones
- [ ] `calcular_cobro` exime el cargo base (a $0) cuando el paquete es primera entrega a ese teléfono
- [ ] `calcular_cobro` cobra bodegaje igual aunque sea primera entrega (nunca se exime)
- [ ] Fórmula de bodegaje: 0 bloques a las 48h exactas, 1 bloque a las 48h01, 1 bloque a las 71h59, 2
      bloques a las 72h01
- [ ] Las tarifas de bodegaje distintas por tipo de paquete se respetan en el cálculo
- [ ] Ningún `Cobro` se crea para un paquete `Cancelado` (esta función no se invoca en ese camino)
