# 425 — PIN correcto de un Usuario sin registro en el equipo: a `/ingresar`

**Pedido original (Jesús, 2026-09-27):** "ten presente que si se ingresa el pin de un usuario que si esta registrado como
staff pero no se ha logueado y el pin si existe o si es correcto, deberia poder redirigirlo a la pantalla de login,
indiferentemente que otro usuario sea el que haya bloqueado la pantalla con PIN"

**Status:** implementado (local, sin desplegar)

## Alcance

- En `/bloqueo` y en la capa: si el PIN es correcto y de un Usuario **activo**, pero este no tiene registro vigente en ESTE
  equipo (nunca entró acá con contraseña, o el registro venció o se cerró), se va a `/ingresar` con un aviso para entrar
  con usuario y contraseña. No importa quién dejó bloqueado el equipo.
- Cambia una decisión del grilling ("un solo mensaje, no revela si el PIN existe"). Mitigación acordada:
  - sigue contando como intento fallido del equipo (5 → exige contraseña);
  - `/ingresar` no recibe el nombre ni el correo del dueño del PIN.
- Un Usuario desactivado sigue dando "PIN incorrecto".
