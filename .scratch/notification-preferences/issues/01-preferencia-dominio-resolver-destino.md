# 01 — Preferencia de notificaciones + regla unificada de fallback (dominio)

**Spec:** `.scratch/notification-preferences/spec.md` · **ADR:** 0001, 0003, 0005

**What to build:** Toda Persona tiene un interruptor `notificaciones_activas` (activo por defecto). `notificar_evento` deja de enviar ciegamente al `recipient_phone`/`announced_by_phone` congelados: ahora resuelve **quién de verdad puede recibirlo** (una Persona viva, no anonimizada) y respeta su preferencia — con **una sola regla** para "nombre sin teléfono" y "destinatario anonimizado después", no dos.

**Blocked by:** None — `Persona`, `Paquete`, `anonimizar_persona` (ADR-0005) ya están.

**Status:** done · 223 tests verdes

- [x] Migración `0008` **descendiente de `0007`** (raíz única, ADR-0002): `personas.notificaciones_activas` (`Boolean NOT NULL DEFAULT True`). Guard de paridad esquema↔ORM la cubre; `alembic heads` = 1.
- [x] `set_notificaciones_activas(session, persona, activas: bool) -> Persona` en `persona_service.py`.
- [x] `resolver_destino_notificable(session, paquete) -> Persona | None`: si `recipient_phone` existe, busca una Persona **viva** con ese teléfono exacto (una Persona anonimizada ya no tiene ese teléfono, no hace falta filtrar `eliminado_en` aparte); si la encuentra, es el destino. **Si no** (nombre sin teléfono, o Destinatario ya no alcanzable) → cae al **Anunciante** (FK real `announced_by_persona_id`) — pero solo si el Anunciante mismo sigue vivo; si también fue anonimizado, devuelve `None`.
- [x] `notificar_evento` **cambia de firma** a `notificar_evento(session, paquete, evento, sender)`. Usa `resolver_destino_notificable`; si es `None` o `persona.notificaciones_activas` es `False` → no envía nada, sin error. Si hay destino activo → `sender.enviar(persona.telefono, mensaje)` (best-effort, sin cambios en ese comportamiento).
- [x] **Actualizar los 3 call sites existentes** en `packages.py` (`receive_action`, `deliver_action`, `cancel_action`) para pasar `db` a `notificar_evento`. **Actualizar** los tests de Seam A existentes (`test_notificacion_service.py`) a la firma nueva.
- [x] `resolver_destino` (la función pura vieja) **se conserva sin cambios** — sigue siendo válida para "qué dice el snapshot", solo deja de ser la que decide el envío.
- [x] Tests (Seam A): Destinatario vivo con teléfono → ese es el destino; nombre sin teléfono → cae al Anunciante; Destinatario anonimizado después de anunciarle un paquete → cae al Anunciante (**mismo resultado, misma función** que el caso anterior); Anunciante también anonimizado → `None`; `notificaciones_activas=False` → cero llamadas al sender; `True` → envía normal.
