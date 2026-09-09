# 04 — CRUD de tarifas (admin)

**What to build:** un admin edita las 4 tarifas fijas (`TarifaCobro`) desde una pantalla de
configuración simple bajo `/administracion` — sin poder agregar un quinto tipo de cobro ni eliminar
ninguno de los 4.

**Blocked by:** 01 — Núcleo: entidades de cobro + cálculo puro. (En paralelo con 02 y 03.)

**Status:** ready-for-agent

- [ ] Admin edita las 4 tarifas desde `/administracion/tarifas-cobro`
- [ ] Un operador (no admin) recibe 403
- [ ] Cambiar una tarifa NO altera `monto_base`/`monto_bodegaje` de un `Cobro` ya registrado
      (snapshot, no referencia viva)
