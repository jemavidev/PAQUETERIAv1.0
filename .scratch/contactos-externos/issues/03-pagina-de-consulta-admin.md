# 03 — Página de consulta (admin)

**What to build:** `/administracion/contactos-externos`, con buscador (nombre o teléfono) y
paginación simple, mostrando solo los campos que cada contacto realmente tenga.

**Blocked by:** 01 — Núcleo: esquema + fusión pura. (En paralelo con 02 — solo necesita el esquema,
no el script de importación; sus tests pueden sembrar `ContactoExterno` directo.)

**Status:** ready-for-agent

- [ ] Acceso exclusivo de admin (un operador recibe 403)
- [ ] Buscar por nombre encuentra el contacto esperado
- [ ] Buscar por teléfono (en cualquier formato de entrada) también lo encuentra
- [ ] La paginación no repite ni omite filas entre páginas
- [ ] Un contacto sin usuario de WhatsApp no muestra esa columna forzada a vacío
