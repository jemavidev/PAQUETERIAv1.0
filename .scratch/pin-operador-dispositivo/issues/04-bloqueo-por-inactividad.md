# 04 — Bloqueo por inactividad (servidor y capa en el navegador)

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** Tras los segundos de inactividad configurados, el equipo se bloquea. **El servidor** rechaza cualquier acción de staff con una señal de bloqueo distinguible del 401 de "sin sesión", y la acción no se aplica. **El navegador** cuenta como actividad cualquier toque, clic o tecla y se lo avisa al servidor como máximo una vez por minuto. Al vencer el tiempo, o al recibir la señal de bloqueo, muestra una **capa de bloqueo sobre la página** sin navegar. Si desbloquea la misma persona, la capa desaparece y todo sigue igual (vista, modal, lo escrito). Si desbloquea otra, la vista actual se recarga limpia, o va al inicio si no tiene permiso.

**Blocked by:** 03 — Pantalla de bloqueo y desbloqueo con PIN.

**Status:** ready-for-agent

- [ ] La sesión guarda la marca de última actividad. `current_staff` la compara con la configuración vigente (ticket 01) en cada petición.
- [ ] Las peticiones del Usuario aceptadas renuevan la marca. Las marcadas como automáticas (encabezado propio) no la renuevan.
- [ ] Endpoint de aviso de actividad: no tiene efectos, renueva la marca solo si el equipo no está bloqueado todavía y, si ya lo está, devuelve la señal de bloqueo.
- [ ] Señal de bloqueo: las peticiones htmx o fetch reciben un código o encabezado que el cliente convierte en la capa; la navegación normal recibe la pantalla de bloqueo del ticket 03.
- [ ] Un guardado rechazado por bloqueo no deja rastro en la BD. Tras desbloquear la misma persona, el formulario sigue ahí y puede reenviarse.
- [ ] Desbloquear desde la capa responde si el Operador cambió, y el cliente decide entre quitar la capa o recargar.
- [ ] Pruebas en la costura web (reloj controlado):
  - una acción después del tiempo configurado se rechaza con la señal de bloqueo y no se aplica;
  - el aviso de actividad y las peticiones del Usuario renuevan la marca;
  - una petición marcada como automática no la renueva;
  - un cambio en la configuración aplica en la siguiente petición.
- [ ] Pruebas en la costura de navegador (reloj del navegador controlado):
  - la capa aparece al vencer el tiempo;
  - las teclas y los toques la posponen;
  - si desbloquea la misma persona, el formulario a medias se conserva;
  - si desbloquea otra, el modal abierto desaparece y la vista se recarga.
