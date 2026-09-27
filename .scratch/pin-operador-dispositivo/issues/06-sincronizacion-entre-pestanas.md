# 06 — Sincronización entre pestañas

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** En un equipo hay un solo Operador activo, sin importar cuántas pestañas estén abiertas. Bloquear en una pestaña (por tiempo o con el botón) muestra la capa en todas. Desbloquear en una quita la capa en todas; si cambió el Operador, las demás se recargan limpias. La actividad en cualquier pestaña reinicia el mismo contador de inactividad.

**Blocked by:** 04 — Bloqueo por inactividad.

**Status:** ready-for-agent

- [ ] Las pestañas se comunican por un canal del navegador (BroadcastChannel, con respaldo en eventos de `storage`) para bloquear, desbloquear, cambiar de Operador y compartir la actividad.
- [ ] El servidor sigue siendo la fuente de verdad: si un mensaje entre pestañas se pierde, la siguiente petición igual recibe la señal de bloqueo.
- [ ] Los avisos de actividad al servidor siguen limitados a uno por minuto por equipo, no uno por pestaña.
- [ ] Pruebas en la costura de navegador (dos pestañas del mismo contexto):
  - "Bloquear" en A muestra la capa en B;
  - desbloquear como otro Usuario en A recarga B;
  - teclear en A mantiene desbloqueada a B pasado el tiempo configurado.
