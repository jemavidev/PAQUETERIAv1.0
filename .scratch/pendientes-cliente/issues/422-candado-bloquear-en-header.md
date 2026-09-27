# 422 — Candado para bloquear el equipo junto al menú de cuenta

**Pedido original (Jesús, 2026-09-27):** "Como puedo acceder a esta vista /bloqueo estando en cualquiera de las otras vistas,
no veo un acceso directo a esta vista, tanto para el desktop como para los dispositivos mobiles, seria bueno incluir un icono
digamos de un candado al lado del boton de login, puede ser a la izquierda de este. Este deberia ser visible solamente si
existe algun usuario logueado en ese dispositivo."

**Status:** desplegado en test (`860699b`, 2026-09-27), pendiente confirmar en vivo — versión corregida, ver abajo

## Alcance

- En el header, a la izquierda del avatar o menú de cuenta, un botón con ícono de candado que bloquea el equipo (mismo
  efecto que "Bloquear" del menú: `POST /bloquear` → `/bloqueo`, y avisa a las demás pestañas).
- Visible en escritorio y en móvil, solo con un Operador activo (sesión de staff). Nunca para un visitante ni para un
  cliente sin sesión de staff.
- Relacionado: `.scratch/pin-operador-dispositivo` (ticket 03, "Bloquear").

## Corrección del pedido (Jesús, 2026-09-27)

"te confirmo el icono de bloqueo no es para bloquear la pantalla, por el contrario deberia estar alli para acceder a la
pantalla de bloqueo, pero solo cuando se esta en otra vista y el usuario esta bloqueado [...] (usuarios logeado y PIN de
bloqueo activado, el usuario digamos que esta en la vista de anunciar (version vista publica), pero quiere desbloquear la
pantala para acceder a la vista de staff), la idea es que en este momento si aparezca el candado para que lo lleve a la
pantalla de bloqueo y pueda ingresar el pin"

**Alcance corregido:**
- El candado es un **enlace a `/bloqueo`**, no un botón que bloquea.
- Solo se ve con el **equipo bloqueado**: sin Operador activo, y con alguien que pueda desbloquear con PIN en este equipo
  (`acepta_pin`). Está a la izquierda del ícono de ingresar del header público, en escritorio y en móvil.
- Con un Operador activo no aparece. Bloquear sigue siendo "Bloquear" del menú de cuenta.
- Se reemplaza lo implementado en `b3d96f9` (candado que bloqueaba).

**Status:** desplegado en test (`860699b`, 2026-09-27), pendiente confirmar en vivo
