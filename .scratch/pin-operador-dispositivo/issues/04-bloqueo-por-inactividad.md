# 04 — Bloqueo por inactividad (servidor y capa en el navegador)

**Spec:** `.scratch/pin-operador-dispositivo/spec.md` · **Glosario:** Usuario, PIN, Dispositivo registrado, Operador activo, Bloqueo · **ADR:** 0002 (Alembic raíz única)

**What to build:** Tras los segundos de inactividad configurados, el equipo se bloquea. **El servidor** rechaza cualquier acción de staff con una señal de bloqueo distinguible del 401 de "sin sesión", y la acción no se aplica. **El navegador** cuenta como actividad cualquier toque, clic o tecla y se lo avisa al servidor como máximo una vez por minuto. Al vencer el tiempo, o al recibir la señal de bloqueo, muestra una **capa de bloqueo sobre la página** sin navegar. Si desbloquea la misma persona, la capa desaparece y todo sigue igual (vista, modal, lo escrito). Si desbloquea otra, la vista actual se recarga limpia, o va al inicio si no tiene permiso.

**Blocked by:** 03 — Pantalla de bloqueo y desbloqueo con PIN.

**Status:** done · 9 tests web + 5 de navegador nuevos verdes; suite web + data_model + infra (2387) y browser (89) verdes

- [x] La sesión guarda la marca de última actividad. `current_staff` la compara con la configuración vigente (ticket 01) en cada petición.
- [x] Las peticiones del Usuario aceptadas renuevan la marca. Las marcadas como automáticas (encabezado propio) no la renuevan.
- [x] Endpoint de aviso de actividad: no tiene efectos, renueva la marca solo si el equipo no está bloqueado todavía y, si ya lo está, devuelve la señal de bloqueo.
- [x] Señal de bloqueo: las peticiones htmx o fetch reciben un código o encabezado que el cliente convierte en la capa; la navegación normal recibe la pantalla de bloqueo del ticket 03.
- [x] Un guardado rechazado por bloqueo no deja rastro en la BD. Tras desbloquear la misma persona, el formulario sigue ahí y puede reenviarse.
- [x] Desbloquear desde la capa responde si el Operador cambió, y el cliente decide entre quitar la capa o recargar.
- [x] Pruebas en la costura web (reloj controlado):
  - una acción después del tiempo configurado se rechaza con la señal de bloqueo y no se aplica;
  - el aviso de actividad y las peticiones del Usuario renuevan la marca;
  - una petición marcada como automática no la renueva;
  - un cambio en la configuración aplica en la siguiente petición.
- [x] Pruebas en la costura de navegador (reloj del navegador controlado):
  - la capa aparece al vencer el tiempo;
  - las teclas y los toques la posponen;
  - si desbloquea la misma persona, el formulario a medias se conserva;
  - si desbloquea otra, el modal abierto desaparece y la vista se recarga.

## Comments

- **Margen del servidor:** el servidor bloquea tras los segundos configurados **+ 60 s** (`MARGEN_AVISO_SEGUNDOS`), porque el navegador avisa de la actividad como máximo una vez por minuto. Quien manda el Bloqueo en pantalla es el navegador; en cuanto muestra la capa, hace `POST /bloquear` y el servidor bloquea en el acto.
- **Qué pasa con la sesión al bloquear:** se **quita** al Operador y se guarda su id aparte (`operador_bloqueado`), en vez de marcarlo como bloqueado. Así, las vistas que solo miran si hay sesión de staff (búsqueda, `/entrar`) no muestran nada con el equipo bloqueado, y al desbloquear el servidor sabe si es la misma persona.
- **Cómo distingue un `fetch`:** por `Sec-Fetch-Mode` (distinto de `navigate`). A un `fetch` bloqueado le responde 423 con `X-PaqueteX-Bloqueo: 1`; a una navegación, la pantalla de bloqueo.
- **Cola de fotos:** trata el 423 como "reintentar" (hasta el ticket 05 no quedaba exenta).
- El encabezado se llamaba `X-PaqueteX-Bloqueado`, pero chocaba con una prueba que busca la palabra "Bloqueado" en toda la página.
- **Correcciones tras `code-review` (2026-09-27):**
  - El middleware `bloquear_si_vencio` (dentro de la sesión) bloquea el equipo antes de cualquier ruta cuando la inactividad venció. Así, `/consultar` y `/entrar`, que solo miran si hay sesión de staff, tampoco muestran nada con un Operador vencido.
  - La capa escucha también `htmx:afterRequest` (423).
  - El teclado usa `data-enfocar` en vez de `autofocus` (issue 418).
  - El spec ahora dice explícitamente el minuto de margen del servidor.
- Queda sin corregir, a propósito: un envío de formulario normal (no `fetch`) rechazado por el servidor pierde lo escrito. Solo ocurre si el navegador no mostró la capa a tiempo, porque la capa bloquea los envíos antes.
