# 422 — Candado para bloquear el equipo junto al menú de cuenta

**Pedido original (Jesús, 2026-09-27):** "Como puedo acceder a esta vista /bloqueo estando en cualquiera de las otras vistas,
no veo un acceso directo a esta vista, tanto para el desktop como para los dispositivos mobiles, seria bueno incluir un icono
digamos de un candado al lado del boton de login, puede ser a la izquierda de este. Este deberia ser visible solamente si
existe algun usuario logueado en ese dispositivo."

**Status:** implementado (local, sin desplegar)

## Alcance

- En el header, a la izquierda del avatar o menú de cuenta, un botón con ícono de candado que bloquea el equipo (mismo
  efecto que "Bloquear" del menú: `POST /bloquear` → `/bloqueo`, y avisa a las demás pestañas).
- Visible en escritorio y en móvil, solo con un Operador activo (sesión de staff). Nunca para un visitante ni para un
  cliente sin sesión de staff.
- Relacionado: `.scratch/pin-operador-dispositivo` (ticket 03, "Bloquear").
