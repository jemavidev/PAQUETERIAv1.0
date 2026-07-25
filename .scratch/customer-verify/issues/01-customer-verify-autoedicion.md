# 01 — `/customer/verify` (autoedición del cliente)

**Spec:** `.scratch/customer-verify/spec.md` · **Glosario:** Persona, Apartamento, Herencia de apartamento · **ADR:** 0001 (snapshot inmutable), 0004 (capa web clean-room)

**What to build:** Un residente **con sesión verificada** (`current_customer`) abre `/customer/verify`, ve sus datos actuales (nombre, email, documento/tipo, segundo contacto, Apartamento) y los **edita**. Puede **declarar su Apartamento** (Conjunto/Torre/Apartamento, creable sobre la marcha) — el acto que lo une deliberadamente al grupo "misma unidad" de ese apartamento.

**Blocked by:** None — `current_customer` (customer-otp-auth) y `declare_unit`/`get_or_create_apartamento` (data-model) ya están.

**Status:** ready-for-agent

- [ ] `update_datos_personales(session, persona, *, nombre=None, email=None, documento=None, tipo_documento=None, segundo_contacto=None) -> Persona` en dominio: **actualización parcial** — los campos `None` (no enviados) **no** tocan el valor existente; validación básica de forma (p.ej. email con `@`, si se manda).
- [ ] `GET /customer/verify` **gated por `current_customer`** (sin sesión → redirige a `/auth/customer/login`, handler ya existente): muestra el formulario **prellenado** con los datos actuales, incluido el Apartamento actual si tiene.
- [ ] `POST /customer/verify`: guarda los datos personales vía `update_datos_personales`; si vienen Conjunto/Torre/Apartamento (**opcionales**), llama `get_or_create_apartamento(...)` + `declare_unit(apartamento, [(persona.telefono, persona.nombre)])` — **un solo miembro** (el propio cliente); **PRG** de vuelta a `/customer/verify` con confirmación.
- [ ] Declarar un Apartamento **existente** lo **reutiliza** (no duplica) y **no afecta** a ninguna otra Persona ya asignada a ese Apartamento (el test lo prueba explícitamente, no lo asume).
- [ ] Guardar datos / cambiar de Apartamento **no reescribe** el snapshot de paquetes ya anunciados por esa Persona (ADR-0001).
- [ ] Email con forma inválida → error claro, **sin persistir** el cambio inválido (el resto de campos válidos del mismo envío tampoco se guarda — todo o nada por request).
- [ ] Tests HTTP (`TestClient`, sesión de cliente vía OTP como en `test_customer_auth.py`): sin sesión → redirige; con sesión → 200 con datos prellenados; `POST` guarda parcialmente (campos no enviados quedan igual); `POST` con Apartamento nuevo lo crea y asigna; `POST` con Apartamento existente lo reutiliza y **no muta** a otra Persona ya en él; email inválido → error sin persistir; snapshot de un paquete anunciado antes se mantiene tras cambiar de Apartamento.
