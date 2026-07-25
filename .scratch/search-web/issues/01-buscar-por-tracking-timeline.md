# 01 — Buscar por número de seguimiento + timeline

**Spec:** `.scratch/search-web/spec.md` · **Glosario:** Estados del Paquete, Contexto de entrega (snapshot) · **ADR:** 0004

**What to build:** Un residente abre **`/search`** (público, sin login), busca su paquete por su **número de seguimiento** y ve su **estado actual** más una **línea de tiempo legible** (Anunciado → Recibido → Entregado, o Cancelado con su motivo), armada desde los timestamps de transición que el Paquete ya tiene.

**Blocked by:** None — `package-lifecycle` (timestamps de transición) y la capa web ya están.

**Status:** ready-for-agent

- [ ] `GET /search` **público** (sin `current_staff`): formulario con un campo ("número de seguimiento o teléfono").
- [ ] Buscar por un `tracking_number` que coincide **exactamente** → muestra ese Paquete: **estado actual**, **destinatario snapshot** (nombre + apartamento snapshot), y el **timeline**.
- [ ] El **timeline** muestra solo los hitos **ocurridos** (timestamps no nulos) en orden, con fecha/hora legible; si `Cancelado`, incluye el **motivo** (`cancel_reason`).
- [ ] El timeline **no** expone al operador (`*_by_usuario`) — solo hitos y fechas, nada de actor interno.
- [ ] Término sin coincidencia (ni tracking ni, en este ticket, teléfono aún) → mensaje claro de "sin resultados", **200**, sin error.
- [ ] La vista **no** requiere sesión (a diferencia de `/packages`).
- [ ] Tests HTTP (`TestClient`, sin autenticar): `GET /search` → 200; sembrar un paquete con `announce` y buscarlo por tracking → aparece con estado `Anunciado`; tras `receive`/`deliver` (dominio), el timeline muestra esos hitos; un paquete cancelado muestra el motivo; término sin coincidencia → "sin resultados" sin error.
