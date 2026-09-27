# 03 — Pantalla de bloqueo, desbloqueo con PIN y "Bloquear"

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** El menú de cuenta trae **"Bloquear"**, que deja el equipo en la pantalla de bloqueo: nombre del conjunto, teclado numérico de 4 dígitos y el enlace "Ingresar con usuario y contraseña". No muestra quiénes están registrados. Digitar un PIN válido convierte a su dueño en el **Operador activo**, siempre que ese Usuario tenga un registro vigente en este equipo; en otro equipo, el mismo PIN no sirve. Todo lo que se haga después queda a nombre del Operador activo. Si el equipo no tiene registros vigentes, se va directo a `/ingresar`.

**Blocked by:** 02 — Registro del dispositivo y PIN obligatorio.

**Status:** done · 11 tests nuevos verdes; suite web + infra verde (1403)

- [x] `desbloquear(dispositivo, pin)` en el servicio de dominio devuelve el Usuario o un motivo de rechazo genérico: no revela si el PIN existe en otro equipo.
- [x] La sesión guarda el Operador activo. "Bloquear" lo quita y deja el equipo en la pantalla de bloqueo, pero el registro del dispositivo sigue vigente.
- [x] Con el equipo bloqueado, toda vista de staff lleva a la pantalla de bloqueo. En esta etapa es navegación normal; la capa sobre la página llega en el ticket 04.
- [x] Si otro Usuario desbloquea, llega a la vista que pidió si tiene permiso para verla, o al inicio si no.
- [x] Pruebas en la costura web (dos `TestClient` = dos equipos):
  - un PIN válido desbloquea en el equipo registrado y no en otro;
  - un PIN inexistente se rechaza con el mismo mensaje;
  - recibir o entregar un Paquete después de desbloquear con el PIN del Usuario B deja a B como actor;
  - "Bloquear" exige el PIN antes de la siguiente acción;
  - un equipo sin registros vigentes redirige a `/ingresar`;
  - el ingreso por OTP del residente no cambia.

## Comments

- Adelantado del ticket 08: cambiar la contraseña (propia, por un ADMIN o por restablecimiento) sube también `registros_version`. Sin esto, el otro equipo caía en la pantalla de bloqueo y el PIN reabría lo que el issue 383 quiso cerrar. El equipo de quien la cambia se vuelve a registrar al momento.
- Sin Operador activo, `current_staff` manda a `/bloqueo?siguiente=<ruta>` si alguien puede desbloquear ese equipo, y a `/ingresar` si no. `siguiente` solo se pone en navegaciones GET y se sanea: solo rutas locales, y al inicio si un OPERADOR pide Administración.
- El teclado es un componente propio (`components/_teclado_pin.html`, estilos sin clases nuevas de Tailwind), para reusarlo en la capa del ticket 04.
