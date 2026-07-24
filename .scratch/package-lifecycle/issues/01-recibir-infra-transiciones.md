# 01 — Recibir (+ infraestructura de transiciones)

**Spec:** `.scratch/package-lifecycle/spec.md` · **Glosario:** Estados del Paquete, Recibir, Guía, Usuario

**What to build:** El staff puede **recibir** un paquete que estaba `ANUNCIADO`: queda `RECIBIDO`, con **quién** lo recibió (el Usuario de la sesión) y **cuándo**, y opcionalmente su **Guía**. Se establece la infraestructura de transiciones (el error `TransicionInvalida` + el patrón de guardia) que las demás transiciones reutilizan.

**Blocked by:** None — la rebanada data-model (Persona/Apartamento/Paquete/Usuario) ya está.

**Status:** ready-for-agent

- [ ] Módulo de transiciones del Paquete en `app/domain/` con `receive(session, paquete, actor, guide_number=None)`: `ANUNCIADO → RECIBIDO`; escribe `received_at` (now), `received_by_usuario_id = actor.id`, y `guide_number` si se pasa (opcional).
- [ ] Error de dominio `TransicionInvalida` (estado actual + transición intentada) para orígenes no permitidos — reutilizable por las tres transiciones.
- [ ] `receive` **rechaza** si el paquete no está `ANUNCIADO` (ya recibido / entregado / cancelado) con `TransicionInvalida`, y el paquete queda **INTACTO** (ni estado ni timestamps cambian: valida antes de mutar).
- [ ] `actor` es un `Usuario` **obligatorio**; no hay default ni id hardcodeado (invariante del brief §14).
- [ ] Tests (Seam A, arnés existente `tests/data_model` / mismo Postgres efímero): recibir un `ANUNCIADO` con y sin `guide_number`; el actor y `received_at` quedan registrados; rechazo desde un no-`ANUNCIADO` sin efecto. Un `Usuario` de prueba se crea en el test.
