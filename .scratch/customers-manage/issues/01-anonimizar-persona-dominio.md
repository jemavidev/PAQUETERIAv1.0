# 01 — Anonimizar Persona (dominio)

**Spec:** `.scratch/customers-manage/spec.md` · **ADR:** 0005 (eliminar Persona = anonimización), 0002 (Alembic raíz única)

**What to build:** El sistema puede **anonimizar** una Persona: limpia sus datos personales y reemplaza su Teléfono por un valor sintético no reutilizable, **sin borrar la fila** (la FK real desde `paquetes.announced_by_persona_id` nunca se rompe). Todo en dominio, sin HTTP.

**Blocked by:** None — `Persona`, `move_resident` (data-model) ya están y están probados.

**Status:** done · 210 tests verdes

- [x] Migración `0007` **descendiente de `0006`** (raíz única, ADR-0002): añade `eliminado_en` (timestamp, nullable) a `personas`. Guard de paridad esquema↔ORM la cubre; `alembic heads` = 1.
- [x] `anonimizar_persona(session, persona) -> Persona` en `persona_service.py`: desvincula del Apartamento reutilizando `move_resident(session, persona.telefono, None)` **antes** de tocar el teléfono; limpia `nombre` → `"Cliente eliminado"`, `email`/`documento`/`tipo_documento`/`segundo_contacto` → `NULL`; **reemplaza `telefono`** por un valor sintético único no enrutable; marca `eliminado_en = ahora`.
- [x] **Idempotente**: si `persona.eliminado_en` ya está seteado, es un no-op (no falla, no vuelve a mutar).
- [x] El **snapshot** de un Paquete ya anunciado por esa Persona (`recipient_name`/`recipient_phone`/`announced_by_phone`, columnas de texto) **no cambia** tras anonimizar (ADR-0001).
- [x] Anunciar de nuevo con el **teléfono real original** (tras la anonimización) crea una **Persona nueva** — el teléfono viejo ya no resuelve a la identidad anonimizada.
- [x] Tests (Seam A): anonimizar limpia los campos correctos; teléfono queda sintético y único; `apartamento_actual_id` queda `NULL`; llamar dos veces es no-op; snapshot de paquete previo intacto; re-anunciar con el teléfono real original crea Persona distinta.
