# 02 — Apartamento + membresía actual

**Spec:** `.scratch/data-model/spec.md` · **Glosario:** Apartamento, Apartamento actual

**What to build:** Una **Persona** puede tener un **Apartamento actual**. El staff crea Apartamentos sobre la marcha (Conjunto → Torre → Apartamento); escribir uno que ya existe **reutiliza el existente** en lugar de duplicar. El Apartamento es **opcional**: una Persona puede no tener ninguno.

**Blocked by:** 01 — Persona + árbol Alembic limpio + arnés de CI.

**Status:** done — commit 695e74f · 44 tests verdes

- [x] Migración (descendiente de la raíz de 01) añade `apartamentos` (`conjunto`, `torre`, `apartamento`) con **restricción única sobre la terna normalizada**, y la FK nullable `apartamento_actual_id` en `personas`.
- [x] `get_or_create_apartamento(conjunto, torre, apartamento)`: normaliza casing/espacios y **reutiliza el existente por la terna**; lo crea si no existe (entidad ligera, creable sobre la marcha).
- [x] `set_apartamento_actual(telefono, apartamento)` asigna el Apartamento actual de una Persona.
- [x] Una Persona **sin** Apartamento es válida (`apartamento_actual_id` nulo).
- [x] Tests: dedup por terna (misma terna → un solo Apartamento); asignar apartamento actual; Persona sin apartamento.
