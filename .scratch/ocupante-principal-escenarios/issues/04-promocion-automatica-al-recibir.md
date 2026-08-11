# 04 — Promoción automática a principal al recibir un paquete

**What to build:** al recibir un paquete (`ANUNCIADO`→`RECIBIDO`), si la unidad del destinatario todavía no tiene principal, el residente resuelto queda promovido automáticamente en el mismo acto — sin paso manual — siempre que tenga Teléfono o WhatsApp propio. Si no tiene contacto propio, o no se puede resolver un Ocupante concreto, no se dispara nada (la unidad queda sin principal hasta que alguien con contacto reciba algo).

**Blocked by:** 03 (necesita que promover también confirme, para no dejar un principal sin confirmar).

**Status:** ready-for-agent

- [ ] Al final de `paquete_lifecycle.receive()`, tras una transición exitosa, se resuelve el Ocupante correspondiente al destinatario del paquete: primero por `recipient_phone` (Persona → Ocupante activo), si no por coincidencia de `recipient_name` dentro del roster de la unidad del snapshot (`snapshot_torre`/`snapshot_apartamento`).
- [ ] Si se resuelve un Ocupante, su unidad no tiene principal todavía, y el Ocupante tiene `persona_id` — se promueve (`promover_a_principal`).
- [ ] Si no se puede resolver ningún Ocupante, o el resuelto no tiene contacto propio, `receive()` completa igual sin error — la promoción simplemente no ocurre.
- [ ] Aplica sin importar por cuál vista se anunció el paquete originalmente (`/announce` los 3 caminos, o `/anunciar`).
- [ ] Si la unidad YA tenía principal, recibir un paquete de otro residente no cambia nada — el principal existente se mantiene.
- [ ] Tests de dominio en `tests/data_model` cubriendo: resolución por teléfono, resolución por nombre, sin resolución posible, destinatario sin contacto propio (no promueve), unidad que ya tenía principal (no cambia).
- [ ] Tests web (`test_packages.py`/`test_announce_new.py`) verificando el efecto end-to-end: recibir un paquete deja al residente como principal cuando corresponde.
