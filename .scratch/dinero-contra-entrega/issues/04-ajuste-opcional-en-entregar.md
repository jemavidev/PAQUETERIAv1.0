# 04 — Ajuste opcional en Entregar

**What to build:** si el destinatario tiene saldo negativo al momento de Entregar, el modal muestra
el monto pendiente y un campo opcional "¿pagó ahora?" — sin bloquear nunca la entrega.

**Blocked by:** 01 — Núcleo: entidad y funciones de saldo. (En paralelo con 02 y 03. Nota: este
ticket y el ticket "Entrega atómica con cobro" del módulo `cobro-bodegaje` tocan el mismo endpoint
de Entregar — no se bloquean entre sí, pero quien implemente el segundo de los dos debe revisar el
formulario ya extendido por el primero.)

**Status:** ready-for-agent

- [ ] Un saldo negativo asociado al destinatario muestra el campo de ajuste al Entregar
- [ ] Completar el campo crea el movimiento positivo correspondiente
- [ ] Dejarlo vacío entrega el paquete igual, sin crear ningún movimiento ni bloquear nada
