# 03 — CRUD de motivos de anulación (admin)

**What to build:** un admin puede crear y eliminar los motivos del catálogo cerrado que usa el "$0"
de la entrega — mismo patrón exacto que `MotivoCancelacion` (sin campo "activo", borrado directo).

**Blocked by:** 01 — Núcleo: entidades de cobro + cálculo puro. (En paralelo con 02 y 04 — el flujo
de Entregar puede probarse con un motivo sembrado directo en tests, sin depender de este CRUD.)

**Status:** ready-for-agent

- [ ] Admin puede crear un `MotivoAnulacionCobro` nuevo
- [ ] Admin puede eliminar un `MotivoAnulacionCobro` existente
- [ ] Un operador (no admin) recibe 403 al intentar crear o eliminar
