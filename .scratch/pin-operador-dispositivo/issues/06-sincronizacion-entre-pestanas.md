# 06 — Sincronización entre pestañas

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** En un equipo hay un solo Operador activo, sin importar cuántas pestañas estén abiertas. Bloquear en una pestaña (por tiempo o con el botón) muestra la capa en todas. Desbloquear en una quita la capa en todas; si cambió el Operador, las demás se recargan limpias. La actividad en cualquier pestaña reinicia el mismo contador de inactividad.

**Blocked by:** 04 — Bloqueo por inactividad.

**Status:** done · 4 tests de navegador nuevos verdes

- [x] Las pestañas se comunican por un canal del navegador (BroadcastChannel, con respaldo en eventos de `storage`) para bloquear, desbloquear, cambiar de Operador y compartir la actividad.
- [x] El servidor sigue siendo la fuente de verdad: si un mensaje entre pestañas se pierde, la siguiente petición igual recibe la señal de bloqueo.
- [x] Los avisos de actividad al servidor siguen limitados a uno por minuto por equipo, no uno por pestaña.
- [x] Pruebas en la costura de navegador (dos pestañas del mismo contexto):
  - "Bloquear" en A muestra la capa en B;
  - desbloquear como otro Usuario en A recarga B;
  - teclear en A mantiene desbloqueada a B pasado el tiempo configurado.

## Comments

- Mensajes del canal `paquetex-bloqueo`: `actividad` (a lo sumo uno cada 5 s por pestaña), `aviso` (comparte el minuto entre avisos al servidor), `bloqueo`, y `desbloqueo` (con `mismo_operador` y `es_admin`, que ahora también devuelve el JSON de `/bloqueo`, para que la otra pestaña vaya al inicio si el nuevo Operador no tiene permiso para su vista).
- "Bloquear" del menú avisa a las demás pestañas antes de navegar. La pantalla completa `/bloqueo` también escucha y sigue a su vista cuando otra pestaña desbloquea.
