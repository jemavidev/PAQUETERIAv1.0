# 03 — Pago al mensajero en Recibir

**What to build:** el flujo de Recibir muestra el selector "de quién se descuenta" + el monto pagado
al mensajero, solo si el destinatario o algún compañero de su apartamento actual ya tiene historial
de saldo. Confirmar el pago crea el movimiento negativo en la misma transacción que `receive()`.

**Blocked by:** 01 — Núcleo: entidad y funciones de saldo. (En paralelo con 02 y 04.)

**Status:** ready-for-agent

- [ ] El selector de pago aparece solo si el destinatario o un compañero de apartamento actual tiene
      historial de saldo
- [ ] Recibir sin ningún historial se comporta idéntico a hoy, sin ninguna mención de contra entrega
- [ ] Staff puede elegir de cuál residente del apartamento (entre los que tienen historial) se
      descuenta, no solo del destinatario
- [ ] Confirmar el pago crea el movimiento negativo y transiciona el paquete en la misma operación
- [ ] El saldo puede quedar en negativo si el pago excede lo disponible (nunca se bloquea el pago)
