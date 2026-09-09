# 02 — Entrega atómica con cobro

**What to build:** el endpoint único de Entregar (compartido por `/paquetes` y `/consultar`) calcula
y registra el `Cobro` (o "$0" + motivo) en la misma transacción que marca el paquete como
`Entregado` — un solo formulario, un solo submit, sin posibilidad de entregar sin dejar el cobro
resuelto. Una vez registrado, el `Cobro` es inmutable para siempre.

**Blocked by:** 01 — Núcleo: entidades de cobro + cálculo puro.

**Status:** ready-for-agent

- [ ] Entregar crea el `Cobro` con el monto calculado (recalculado server-side, nunca confiado del
      cliente) en la misma transacción que `delivered_at`
- [ ] Marcar "$0" exige elegir un `motivo_anulacion_id`; sin motivo, se rechaza sin transicionar el
      paquete ni crear el `Cobro`
- [ ] El mismo flujo de cobro funciona igual desde `/paquetes` y desde `/consultar`
- [ ] Si un paquete llega a `Cancelado` en vez de `Entregado`, no se genera ningún `Cobro`
- [ ] No existe ninguna ruta (ni de admin) que edite o borre un `Cobro` ya creado
