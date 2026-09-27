# 07 — 5 PIN fallidos → contraseña → cambio de PIN, con aviso al ADMIN

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** Cada equipo cuenta los PIN incorrectos seguidos. Al quinto, el equipo deja de aceptar PIN y muestra usuario y contraseña. Quien entra ahí con su contraseña pasa obligatoriamente a cambiar su PIN, y puede dejar el mismo. Un PIN correcto o un ingreso con contraseña ponen el contador en cero. Cada bloqueo por intentos queda registrado, y el ADMIN ve los últimos (fecha, hora y equipo) como aviso en `/administracion/personal`.

**Blocked by:** 03 — Pantalla de bloqueo y desbloqueo con PIN.

**Status:** done · 6 tests nuevos verdes

- [x] `desbloquear` cuenta los fallos en el Dispositivo. Al quinto, deja el equipo en "requiere contraseña" y registra el evento de seguridad.
- [x] Con el equipo en "requiere contraseña", la pantalla de bloqueo lleva a `/ingresar` y ningún PIN es aceptado, ni siquiera uno correcto.
- [x] El ingreso con contraseña después de un bloqueo por intentos restringe al Usuario a "Cambia tu PIN" hasta que lo confirme. Repetir el mismo PIN es válido.
- [x] Aviso en `/administracion/personal`, visible solo para el ADMIN, con los últimos bloqueos por intentos.
- [x] Pruebas en la costura web:
  - 4 fallos siguen permitiendo PIN;
  - el quinto exige contraseña y luego el cambio de PIN, aceptando el mismo;
  - un acierto intermedio pone el contador en cero;
  - el evento aparece en el aviso del ADMIN y no en la vista de un OPERADOR.

## Comments

- Sin migración: "requiere contraseña" se deriva de `intentos_pin_fallidos >= 5` en el Dispositivo, y entrar con contraseña lo pone en cero.
- Quien entra con contraseña en un equipo bloqueado por intentos (ADMIN incluido) queda con `debe_cambiar_pin` en la sesión hasta confirmar un PIN en `/mi-pin`.
- `acepta_pin` reemplaza a `tiene_registros_vigentes` como condición para mostrar la pantalla o la capa de bloqueo. La cola de fotos sigue usando solo el registro del dispositivo.
- El aviso en `/administracion/personal` muestra los últimos 10 bloqueos con fecha, hora local y los primeros 8 caracteres del id del equipo.
