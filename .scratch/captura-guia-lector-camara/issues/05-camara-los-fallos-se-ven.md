# 05 — Cámara: los fallos se ven (mensajes claros)

**What to build:** hoy, si el permiso de cámara se niega o no hay cámara, queda un cuadro de video negro visible sin ningún mensaje y un error en la consola; si el script del lector de códigos no carga, el botón simplemente no hace nada. Con este ticket cada fallo del escaneo con cámara muestra un mensaje claro, en español y sin jerga técnica, junto al botón; el video se oculta y el campo Guía queda siempre editable. Aplica por igual al botón de Recibir y al de "Confirmar guía" (Entregar), que comparten el comportamiento. Este ticket también crea el helper de **cámara simulada** para pruebas de navegador, que reutilizan los tickets 06 y 07.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 12 a 16 y 59).

**Blocked by:** 01 — Aislar la captura de guía del script compartido; 02 — Prueba en navegador real para el modal Recibir.

**Status:** ready-for-agent

- [ ] Permiso de cámara negado: se muestra un mensaje que lo dice y sugiere habilitarlo o teclear la guía; el video queda oculto (no hay cuadro negro).
- [ ] Sin cámara disponible, y cualquier otro error al iniciar: cada caso muestra un mensaje distinto y claro; el video queda oculto.
- [ ] El script del lector no carga (red caída o recurso bloqueado): se muestra un mensaje que dice que no se pudo cargar el escáner y que se escriba la guía a mano. Hoy no muestra nada.
- [ ] El mensaje existente para "sin soporte de cámara o contexto sin HTTPS" ("Cámara no disponible; escribe la guía a mano.") sigue igual.
- [ ] Después de cualquiera de esos fallos el campo Guía sigue editable y "Recibir" funciona con una guía tecleada a mano.
- [ ] Un mensaje de fallo anterior se limpia cuando el siguiente intento de escaneo arranca bien.
- [ ] El helper de cámara simulada (sustituye el acceso a la cámara en el navegador de prueba, con éxito o con cada tipo de error) queda documentado y listo para reusar.
- [ ] Pruebas en navegador real: un caso por cada tipo de fallo en Recibir, y al menos uno en "Confirmar guía" de Entregar.
