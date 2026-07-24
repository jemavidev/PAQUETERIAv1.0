# 02 — Entregar

**Spec:** `.scratch/package-lifecycle/spec.md` · **Glosario:** Estados del Paquete, Entregar, Contexto de entrega (snapshot)

**What to build:** El staff **entrega** un paquete `RECIBIDO` al residente: queda `ENTREGADO`, con **quién** entregó y **cuándo**. Al entregar, el **destinatario snapshot** del paquete (nombre/apartamento congelados al anunciar) queda disponible para confirmar a quién se le entrega.

**Blocked by:** 01 — Recibir (+ infraestructura de transiciones). Reutiliza `TransicionInvalida` y usa `receive` para llevar un paquete a `RECIBIDO` en los tests.

**Status:** ready-for-agent

- [ ] `deliver(session, paquete, actor)`: `RECIBIDO → ENTREGADO`; escribe `delivered_at` (now), `delivered_by_usuario_id = actor.id`.
- [ ] **Rechaza** (`TransicionInvalida`, sin efecto) si el paquete no está `RECIBIDO`: todavía `ANUNCIADO`, o ya `ENTREGADO`/`CANCELADO`.
- [ ] `actor` es un `Usuario` **obligatorio**.
- [ ] El **destinatario snapshot** (`recipient_name` + snapshot de apartamento) sigue legible en el paquete entregado (no se toca; ADR-0001) — el test lo verifica para confirmar quién retira.
- [ ] Tests: entregar un paquete llevado a `RECIBIDO` vía `receive`; el actor/`delivered_at` quedan registrados; rechazo desde `ANUNCIADO`/`ENTREGADO`/`CANCELADO` sin efecto.
