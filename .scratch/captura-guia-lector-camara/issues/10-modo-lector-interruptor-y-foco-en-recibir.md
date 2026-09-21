# 10 — Modo lector: interruptor por equipo y foco al abrir Recibir

**What to build:** el F7 en modo "escribir en el campo enfocado" escribe donde esté el foco, y hoy al abrir Recibir el foco queda en el botón de la fila, no en la Guía: una lectura sin tocar antes el campo se pierde sin aviso. Sin volver a poner autofocus en todas partes (issue 284), cada F7 se marca una sola vez con un interruptor **"Este equipo tiene lector"** en el menú de cuenta. Apagado por defecto y guardado en el propio equipo. Encendido, al abrir Recibir el foco va al campo Guía sin teclado en pantalla y con el contenido seleccionado, de modo que una nueva lectura reemplaza la anterior en vez de concatenarse. Tocar el campo muestra el teclado normal para teclear a mano. Lo específico del F7 queda pequeño y aislado.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 19 a 27, 30, 34 y 65).

**Blocked by:** 02 — Prueba en navegador real para el modal Recibir.

**Status:** done

- [x] El menú de cuenta muestra, solo a Staff con sesión, un ítem "Este equipo tiene lector" con su estado (activado o desactivado) y permite alternarlo; no aparece para visitantes ni en el modal Recibir.
- [x] Por defecto está **apagado**: con él apagado, abrir Recibir no mueve el foco (comportamiento de hoy, respeta el issue 284) y no cambia nada más.
- [x] El estado se guarda en el propio equipo y sobrevive a recargar la página y a cerrar sesión y volver a entrar; otro equipo o navegador tiene su propio estado (verificado con un segundo contexto de navegador que arranca apagado).
- [x] Encendido, al abrir Recibir el foco queda en el campo Guía; el campo enfocado por esta vía no pide teclado en pantalla y su contenido existente queda seleccionado (teclear o insertar texto lo reemplaza).
- [x] Si el Operador toca el campo, el campo vuelve a pedir el teclado normal, para teclear una guía que el lector no logra leer.
- [x] El botón "Escanear con cámara" sigue disponible y funcionando con el modo encendido.
- [x] Apagar el interruptor devuelve el comportamiento de un celular normal.
- [x] Vale en /paquetes, /announce y el Recibir de /consultar (mismo componente); prueba en navegador real en /paquetes y comprobación por HTTP de que las otras dos cargan el mismo componente y el ítem del menú.
- [x] No hay heurísticas de detección del lector (ni por velocidad de tecleo ni por User-Agent): solo el interruptor.

## Verificación

- Vistas fallar primero: 1 de HTTP (no existía el interruptor) y las 9 de navegador real
  (`tests/browser/test_modo_lector.py`); las 2 de HTTP que ya pasaban fijan que el interruptor NO vive en el modal
  Recibir y que un visitante no lo ve. Ahora pasan las 18 de `tests/web/test_captura_guia.py` y las 10 de
  `test_modo_lector` (54 en el seam completo).
- Interruptor: ítem "Este equipo tiene lector" con su estado (Activado/Desactivado) en el menú de cuenta de
  cualquier Staff (Operador o Admin), presente en /paquetes, /announce, /residentes y /consultar, y solo con sesión
  de Staff (el HTML y el JS global salen únicamente cuando hay Staff). No aparece para visitantes ni dentro del modal.
- Por defecto está **apagado**: abrir Recibir no mueve el foco y el campo sigue con `inputmode="text"` (respeta el
  issue 284). El estado vive en `localStorage` del propio equipo: sobrevive a recargar y a cerrar sesión y volver a
  entrar; otro contexto de navegador (otro equipo) arranca "Desactivado". Sin `localStorage` (modo privado) cae a
  memoria sin romper nada.
- Encendido, al abrir Recibir el foco queda en el campo Guía, con `inputmode="none"` (sin teclado en pantalla) y su
  contenido seleccionado: la prueba escribe "primera-1", cierra y reabre el modal, "lee" otra vez sin tocar el
  campo y queda "SEGUNDA-2" (reemplazó, no concatenó). Un toque del Operador en el campo vuelve a `inputmode="text"`
  (y hace blur/focus para que el teclado aparezca); el botón "Escanear con cámara" sigue disponible y funcionando.
- Un modal que llega YA abierto del servidor (el rechazo por guía larga del ticket 04 lo reabre) también recibe el
  foco al cargar. Apagar el interruptor devuelve el comportamiento normal. Sin heurísticas: solo el interruptor.
- Vale en /paquetes (navegador real) y en el Recibir de /consultar (navegador real: foco e `inputmode="none"`); en
  /announce, HTTP: el ítem del menú está y el bloque de captura es idéntico (ticket 03).
- Regresión: toda la capa web repartida en tandas (34 archivos más los cuatro grandes) y el seam completo, en verde.
  El interruptor solo agrega CSS propio (el estado del ítem) y reutiliza `account-menu-item`: ninguna clase nueva de
  Tailwind, no hizo falta reconstruir el CSS.
- Hallazgos (el mismo tipo que en los tickets 03 y 05): dos veces mi propio texto en el script chocó con pruebas que
  verifican por substring: el selector `modal-receive-` (una prueba de /announce exige que no aparezca en páginas sin
  ese modal; ahora se buscan los campos Guía dentro de `[role="dialog"]` en vez de nombrar el id) y la palabra
  "autofocus" en un comentario (las pruebas de /announce la prohíben). Corregidos; los comentarios de este script ya
  no nombran nada de eso.
- Decisión menor: el interruptor se implementó en el JS global de `base.html` (el ítem está en el encabezado de toda
  página de Staff) y el bloque de captura solo consulta `window.paqueteXModoLector.activo()`; así el estado y el foco
  no se duplican.
