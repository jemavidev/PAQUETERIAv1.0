# 02 — Buscar + ver/editar cliente (web)

**Spec:** `.scratch/customers-manage/spec.md` · **Glosario:** Persona

**What to build:** Staff (cualquier rol) busca un cliente por teléfono o nombre desde `/customers/manage`, ve su ficha y **edita** sus datos personales — reutilizando `update_datos_personales` **sin cambios**, operando sobre la Persona de otro (no la propia sesión).

**Blocked by:** None — `current_staff`, `update_datos_personales` ya existen y están probados. (Independiente del ticket 01: no necesita `anonimizar_persona`.)

**Status:** done · 210 tests verdes

- [x] `GET /customers/manage` **gated por `current_staff`** (cualquier rol): formulario de búsqueda (teléfono o nombre) + lista de resultados.
- [x] `GET /customers/manage/{persona_id}`: ficha con formulario prellenado (nombre, email, documento/tipo, segundo contacto, apartamento actual si tiene) — **sin** declarar Apartamento aquí (eso es `/customer/verify`/`/announce-new`, no se duplica).
- [x] `POST /customers/manage/{persona_id}`: guarda vía `update_datos_personales` (parcial; email inválido rechaza todo el request — mismas reglas ya probadas en `customer-verify`).
- [x] Sin sesión → redirige a `/auth/login`. `persona_id` inexistente → 404.
- [x] Tests HTTP: buscar por teléfono y por nombre encuentra al cliente correcto; sesión de OPERADOR puede ver y editar (no requiere admin); guardado parcial no borra lo no enviado; email inválido rechaza sin persistir; sin sesión redirige; id inexistente → 404.
