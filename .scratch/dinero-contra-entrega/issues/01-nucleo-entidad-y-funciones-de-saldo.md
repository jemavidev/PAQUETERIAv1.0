# 01 — Núcleo: entidad y funciones de saldo

**What to build:** la entidad `MovimientoSaldoContraEntrega` (append-only), y las funciones
`registrar_movimiento_saldo`, `saldo_de_persona` (suma, sin campo desnormalizado) y
`personas_con_historial_en_apartamento` (por apartamento ACTUAL, no snapshot). Sin ninguna ruta ni
UI todavía.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `registrar_movimiento_saldo` crea un movimiento con signo (positivo suma, negativo resta)
- [ ] `saldo_de_persona` suma correctamente varios movimientos, incluyendo el caso de terminar en
      negativo
- [ ] `personas_con_historial_en_apartamento` devuelve solo Ocupantes con Persona propia del
      apartamento dado que tienen al menos un movimiento — usa el apartamento ACTUAL de cada
      Persona, no un snapshot viejo
- [ ] No existe ninguna función ni ruta que edite o borre un movimiento ya creado
