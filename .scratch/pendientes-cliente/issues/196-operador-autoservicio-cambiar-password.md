# 196 — OPERADOR puede cambiar su propia contraseña ("Mi perfil")

**Pedido original (cliente):**
"veo que en las cuentas de staff con rol de operador, no tienen opcion de
geperfil, la idea es que ellos puedan gestionar sus datos como se hacia
antes, no se porque lo quitaste"

Seguimiento directo a issue 195: ahí se quitó el enlace "Mi sesión" del
menú (interpretando "elimina lo relacionado a /mi-sesion del menú del
header" literalmente), sin notar que para un OPERADOR esa era su ÚNICA
entrada al menú de cuenta (Perfiles/Notificaciones/Conjunto son solo-
ADMIN) — y que la página en sí nunca tuvo capacidad de edición real
(solo mostraba Nombre/Email/Rol de solo lectura). El cliente aclaró que
la necesidad real es autoservicio de cuenta para cualquier staff, no solo
un enlace.

**Status:** implementado

## Implementación

- `staff_service.set_password(session, usuario, nueva_password)` ya
  existía (compartida por el reset admin-driven y el reset por correo) y
  no exige actor — se reutiliza tal cual, sin nueva función de dominio.
- Nueva ruta `POST /mi-sesion` (`auth.py`): cualquier staff autenticado
  (`current_staff`) cambia SU PROPIA contraseña — password + confirmación,
  mismo patrón de validación que `/staff/restablecer-password`
  (contraseñas no coinciden → error de campo; contraseña débil →
  `_validar_password` vía `set_password`). El actor sale de la sesión,
  nunca de un campo del form, así que nadie puede tocar la cuenta de otro
  desde acá.
- `auth/me.html` renombrada de "Mi sesión" a "Mi perfil" (título + H1),
  con un segundo formulario "Cambiar mi contraseña" debajo de los datos de
  solo lectura.
- `base.html`: el enlace del menú vuelve, ahora **fuera** del `{% if
  es_admin %}` (issue 195 lo había quitado del todo) — "Mi perfil" es
  visible para TODO staff, no solo ADMIN.

## Verificación

- 4 tests nuevos en `test_auth.py`: OPERADOR cambia su password y puede
  loguearse con la nueva; confirmación que no coincide rechaza; password
  débil rechaza; sin sesión redirige a login.
- Suite `test_auth.py` + `test_layout.py` + `test_password_reset.py` +
  `test_customer_auth.py` + `test_rate_limit.py` + `test_staff_service.py`:
  90 tests, todos pasan.
- Verificado en vivo contra el servidor de dev local con un OPERADOR real
  creado vía el modal de issue 192: el dropdown solo muestra "Mi perfil"
  (correcto, el resto es admin-only); cambió su contraseña y volvió a
  entrar con la nueva.
- Pendiente: deploy a test.papyrus.com.co.
