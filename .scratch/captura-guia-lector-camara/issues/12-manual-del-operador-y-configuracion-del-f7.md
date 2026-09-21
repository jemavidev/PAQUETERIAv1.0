# 12 — Manual del Operador y configuración del F7

**What to build:** el manual del Operador hoy solo dice "número de guía (opcional)" y no menciona ni la cámara ni el lector. Documentar cómo se captura la guía con un celular y con un F7, qué hace y qué no hace cada camino, y cómo dejar cada F7 listo. Es documentación, sin código.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 60 a 62).

**Blocked by:** 03 — El Enter del lector no recibe el paquete; 04 — Guía de más de 50 caracteres; 07 — Cámara: mejor captura; 08 — Aviso de guía repetida; 09 — /consultar con varios paquetes; 11 — Modo lector en Entregar. (Documenta el comportamiento ya terminado, no el previsto.)

**Status:** ready-for-agent

- [ ] El manual del Operador tiene una sección corta de captura de guía en el mismo tono y registro del resto del manual, que explica: escribirla a mano, escanear con la cámara (permiso, linterna, detener), y leer con el lector del F7.
- [ ] Dice con claridad que **una lectura solo llena la guía** y que el Operador siempre confirma con "Recibir", incluso si el lector manda un Enter.
- [ ] Explica los mensajes que puede ver el Operador: guía de más de 50 caracteres, aviso de "Ya hay N paquete(s) con esta guía" (no bloquea), y qué pasa al consultar una guía que está en varios paquetes.
- [ ] Explica cómo activar el modo lector ("Este equipo tiene lector" en el menú de cuenta), qué cambia en Recibir y en "Confirmar guía" de Entregar, y que es una preferencia por equipo.
- [ ] Incluye los pasos para dejar un F7 listo: de fábrica su lector no escribe en páginas web; hay que poner su modo de envío en el que escribe en el campo enfocado sobrescribiendo, con terminador Ninguno (Enter y Tab también se toleran). Indica dónde está el ajuste en el equipo (Ajustes, Scanning Tools, Scanning Settings).
- [ ] Deja escrita la salvedad de que esa configuración del F7 sale de documentación del fabricante que no está confirmada en el equipo, y que se valida en la prueba de campo (ticket 13).
- [ ] Los ejemplos usan el mismo grupo de vecinos inventados del manual, y el vocabulario del glosario (Staff/Operador, Residente).
