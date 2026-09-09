# 01 — Núcleo: esquema + fusión pura

**What to build:** las entidades `ContactoExterno`/`ContactoExternoTelefono` en el esquema, y la
función pura `fusionar_fuentes(filas)` que agrupa filas de cualquier fuente por teléfono compartido,
resolviendo el nombre (gana Google Contacts) y soportando más de un teléfono por contacto. Sin
persistencia incremental ni UI todavía.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Dos filas de fuentes distintas con el mismo teléfono se fusionan en un solo contacto
- [ ] Gana el nombre de Google Contacts sobre producción cuando difieren para el mismo contacto
- [ ] Una fila sin ningún nombre se descarta
- [ ] Una fila sin ningún teléfono que logre normalizarse se descarta
- [ ] Un contacto con dos teléfonos (Phone 1 + Phone 2) queda con ambos asociados
- [ ] Un teléfono sin "+" de 10 dígitos colombiano se normaliza vía `normalizar_telefono`, igual que
      el resto del sistema
- [ ] Un teléfono no reconocible se ignora sin descartar el resto de la fila si tiene otro teléfono
      válido
