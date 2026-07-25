# 01 — `/announce-new` (declarar unidad en lote)

**Spec:** `.scratch/announce-new/spec.md` · **Glosario:** Apartamento, Herencia de apartamento · **ADR:** 0003 (Teléfono llave universal)

**What to build:** Un **staff** (cualquier rol) con sesión abre `/announce-new`, crea o selecciona un **Apartamento** (Conjunto/Torre/Apartamento) y declara **una lista de residentes** (nombre + teléfono, ilimitados) que quedan unidos a esa unidad de una sola vez — reutilizando `get_or_create_apartamento`/`declare_unit` **sin cambios de dominio**.

**Blocked by:** None — `declare_unit`/`get_or_create_apartamento` (data-model) y `current_staff` (staff-auth) ya están y están probados.

**Status:** done · 189 tests verdes

- [x] `GET /announce-new` **gated por `current_staff`** (cualquier rol — no `require_admin`): sin sesión → redirige a `/auth/login`; con sesión (ADMIN u OPERADOR) → 200 con formulario de Apartamento + lista dinámica de filas nombre+teléfono.
- [x] `POST /announce-new`: valida **antes** de llamar a dominio — los 3 campos del Apartamento completos, **al menos un miembro**, y cada fila con **nombre y teléfono ambos presentes** (una fila con uno solo de los dos se rechaza). Cualquier fallo → error claro, **nada se persiste** (todo o nada, mismo patrón que `/customer/verify`).
- [x] Éxito → `get_or_create_apartamento(...)` + `declare_unit(apartamento, miembros)`; **confirmación** listando los residentes unidos a la unidad (PRG).
- [x] Apartamento **ya existente** → se **reutiliza** (no duplica). Teléfono **ya conocido** → esa Persona se **reutiliza** (no duplica), y hereda el Apartamento junto con los demás.
- [x] Tests HTTP (`TestClient`, sesión de staff vía `/auth/login`, patrón `test_packages.py`): sin sesión → redirige; sesión de **OPERADOR** → 200 (a diferencia de `/admin/staff`, que exige ADMIN); `POST` con 3 miembros nuevos → los 3 comparten `apartamento_actual`; Apartamento existente no se duplica; teléfono existente no duplica Persona; fila con nombre sin teléfono (o viceversa) → error sin persistir nada; Apartamento incompleto → error; cero miembros → error. **No** se re-testean los invariantes de `declare_unit` en sí (ya cubiertos en `test_declarar_unidad.py`).
