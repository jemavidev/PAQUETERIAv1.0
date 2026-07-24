# 01 — Persona + árbol Alembic limpio + arnés de CI

**Spec:** `.scratch/data-model/spec.md` · **ADRs:** 0002 (Alembic raíz única), 0003 (Teléfono llave)

**What to build:** El cimiento del modelo nuevo y su arnés de prueba. Cuando alguien anuncia con teléfono + nombre, queda registrado como una **Persona** identificada por su **Teléfono**; volver a usar el mismo teléfono —en cualquier formato— reutiliza la misma Persona, no crea un duplicado. En paralelo, el repo queda con un árbol Alembic de **una sola raíz** y un arnés de CI que construye la base con `alembic upgrade head` sobre un Postgres efímero.

**Blocked by:** None — can start immediately.

**Status:** done — commit `ac78245` · 22 tests verdes

- [x] Se retiran las 38 migraciones viejas y las cicatrices (`fix_migration_conflict.py`, `INSTRUCCIONES_MIGRACION.md`, `INSTRUCCIONES_FIX_MIGRACION.md`); el árbol nuevo tiene **una sola raíz** (`down_revision = None` exactamente una vez). *(ADR-0002)*
- [x] La migración baseline crea `personas`: **Teléfono en forma canónica normalizada**, único y NOT NULL (la llave universal); nombre; campos ampliables nullable (email, documento/tipo, segundo contacto); surrogate key propia; timestamps. *(ADR-0003)*
- [x] El servicio de dominio expone `get_or_create_persona(telefono, nombre)`: **normaliza el teléfono antes de persistir**; si existe una Persona con ese teléfono canónico la reutiliza, si no la crea (registro implícito).
- [x] Arnés de CI: un Postgres efímero se construye corriendo `alembic upgrade head` (**no** `create_all`); los tests de integración del dominio corren contra él.
- [x] **Seam B:** test que verifica un solo `head` y que `upgrade head` → `downgrade base` hace round-trip limpio sobre Postgres vacío.
- [x] **Seam A:** anunciar con teléfono nuevo crea Persona; re-anunciar con el mismo teléfono la reutiliza (sin duplicado); dos formatos del mismo número resuelven a **una** Persona.
