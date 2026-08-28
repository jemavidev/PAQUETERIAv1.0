# 01 — Admin guarda su propio teléfono/WhatsApp en `/mi-sesion`

**What to build:** En `/mi-sesion`, cualquier staff (ADMIN u OPERADOR) puede guardar su propio teléfono y usuario de WhatsApp, junto al nombre que ya edita ahí — autoservicio, sin gate de rol, mismo patrón que ya existe para editar nombre y cambiar contraseña. Estos campos son contacto propio del staff, sin relación con el modelo de identidad de Persona (Teléfono/WhatsApp de residente, ADR-0003/ADR-0007) — no hay unicidad, no habilitan login/OTP.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `Usuario` (dominio) tiene dos columnas nuevas, teléfono y WhatsApp, ambas opcionales (nullable) — migración Alembic nueva; todo `Usuario` existente arranca con ambas en `NULL`.
- [ ] El formulario de `/mi-sesion` gana dos campos de texto (teléfono, WhatsApp) junto al de nombre que ya existe.
- [ ] Guardar el formulario persiste los tres campos (nombre + teléfono + WhatsApp); recargar `/mi-sesion` muestra los valores guardados.
- [ ] Dejar teléfono/WhatsApp vacíos al guardar los persiste como `NULL`, sin error.
- [ ] Un OPERADOR (no solo ADMIN) puede editar su propio teléfono/WhatsApp, igual que ya puede editar su nombre — autoservicio sin gate de rol.
- [ ] Sin validación de formato (E.164, unicidad, etc.) — se guardan como texto libre, igual de permisivo que el resto de este perfil.
