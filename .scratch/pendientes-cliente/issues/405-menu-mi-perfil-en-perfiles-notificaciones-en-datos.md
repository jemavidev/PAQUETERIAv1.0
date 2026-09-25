# 405 — Menú de cuenta: "Mi perfil" dentro de Perfiles, "Notificaciones" dentro de Datos

**Pedido original (Jesús):** "incluyas la opción de 'Mi perfil' dentro de la sección de 'Perfiles', adicional ... en
la sección de 'Perfiles' muevas 'Notificaciones' hasta la sección de 'Datos'. Debería todo quedar como notificaciones
dentro de datos con el resto de otros datos y mi perfil dentro de perfiles al igual que usuarios."

**Status:** implementado (localhost), pendiente confirmar en vivo

## Decisiones (acordadas)

- Admin: "Mi perfil" sale del nivel superior y pasa a Perfiles, primero (Mi perfil, Usuarios).
- Operador (no ve las categorías, solo admin): conserva "Mi perfil" arriba como hoy -- lo necesita para cambiar su
  contraseña (issue 196).
- "Notificaciones" pasa de Perfiles al final de Datos.

## Verificación

- `test_layout.py`: 2 nuevas (admin: Mi perfil antes de Usuarios dentro de Perfiles, Notificaciones en Datos, Mi perfil sin copia suelta arriba; operador: conserva Mi perfil). La del admin vista fallar antes del cambio. `test_layout.py` + `test_auth.py`: 50 en verde.
