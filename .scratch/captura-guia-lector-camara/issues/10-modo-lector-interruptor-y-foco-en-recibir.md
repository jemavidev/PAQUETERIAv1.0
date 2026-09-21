# 10 — Modo lector: interruptor por equipo y foco al abrir Recibir

**What to build:** el F7 en modo "escribir en el campo enfocado" escribe donde esté el foco, y hoy al abrir Recibir el foco queda en el botón de la fila, no en la Guía: una lectura sin tocar antes el campo se pierde sin aviso. Sin volver a poner autofocus en todas partes (issue 284), cada F7 se marca una sola vez con un interruptor **"Este equipo tiene lector"** en el menú de cuenta. Apagado por defecto y guardado en el propio equipo. Encendido, al abrir Recibir el foco va al campo Guía sin teclado en pantalla y con el contenido seleccionado, de modo que una nueva lectura reemplaza la anterior en vez de concatenarse. Tocar el campo muestra el teclado normal para teclear a mano. Lo específico del F7 queda pequeño y aislado.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 19 a 27, 30, 34 y 65).

**Blocked by:** 02 — Prueba en navegador real para el modal Recibir.

**Status:** ready-for-agent

- [ ] El menú de cuenta muestra, solo a Staff con sesión, un ítem "Este equipo tiene lector" con su estado (activado o desactivado) y permite alternarlo; no aparece para visitantes ni en el modal Recibir.
- [ ] Por defecto está **apagado**: con él apagado, abrir Recibir no mueve el foco (comportamiento de hoy, respeta el issue 284) y no cambia nada más.
- [ ] El estado se guarda en el propio equipo y sobrevive a recargar la página y a cerrar sesión y volver a entrar; otro equipo o navegador tiene su propio estado (verificado con un segundo contexto de navegador que arranca apagado).
- [ ] Encendido, al abrir Recibir el foco queda en el campo Guía; el campo enfocado por esta vía no pide teclado en pantalla y su contenido existente queda seleccionado (teclear o insertar texto lo reemplaza).
- [ ] Si el Operador toca el campo, el campo vuelve a pedir el teclado normal, para teclear una guía que el lector no logra leer.
- [ ] El botón "Escanear con cámara" sigue disponible y funcionando con el modo encendido.
- [ ] Apagar el interruptor devuelve el comportamiento de un celular normal.
- [ ] Vale en /paquetes, /announce y el Recibir de /consultar (mismo componente); prueba en navegador real en /paquetes y comprobación por HTTP de que las otras dos cargan el mismo componente y el ítem del menú.
- [ ] No hay heurísticas de detección del lector (ni por velocidad de tecleo ni por User-Agent): solo el interruptor.
