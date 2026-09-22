# 12 — Manual del Operador y configuración del F7

**What to build:** el manual del Operador hoy solo dice "número de guía (opcional)" y no menciona ni la cámara ni el lector. Documentar cómo se captura la guía con un celular y con un F7, qué hace y qué no hace cada camino, y cómo dejar cada F7 listo. Es documentación, sin código.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 60 a 62).

**Blocked by:** 03 — El Enter del lector no recibe el paquete; 04 — Guía de más de 50 caracteres; 07 — Cámara: mejor captura; 08 — Aviso de guía repetida; 09 — /consultar con varios paquetes; 11 — Modo lector en Entregar. (Documenta el comportamiento ya terminado, no el previsto.)

**Status:** done

- [x] El manual del Operador tiene una sección corta de captura de guía en el mismo tono y registro del resto del manual, que explica: escribirla a mano, escanear con la cámara (permiso, linterna, detener), y leer con el lector del F7.
- [x] Dice con claridad que **una lectura solo llena la guía** y que el Operador siempre confirma con "Recibir", incluso si el lector manda un Enter.
- [x] Explica los mensajes que puede ver el Operador: guía de más de 50 caracteres, aviso de "Ya hay N paquete(s) con esta guía" (no bloquea), y qué pasa al consultar una guía que está en varios paquetes.
- [x] Explica cómo activar el modo lector ("Este equipo tiene lector" en el menú de cuenta), qué cambia en Recibir y en "Confirmar guía" de Entregar, y que es una preferencia por equipo.
- [x] Incluye los pasos para dejar un F7 listo: de fábrica su lector no escribe en páginas web; hay que poner su modo de envío en el que escribe en el campo enfocado sobrescribiendo, con terminador Ninguno (Enter y Tab también se toleran). Indica dónde está el ajuste en el equipo (Ajustes, Scanning Tools, Scanning Settings).
- [x] Deja escrita la salvedad de que esa configuración del F7 sale de documentación del fabricante que no está confirmada en el equipo, y que se valida en la prueba de campo (ticket 13).
- [x] Los ejemplos usan el mismo grupo de vecinos inventados del manual, y el vocabulario del glosario (Staff/Operador, Residente).

## Verificación

Es documentación, sin código: la verificación es contrastar cada afirmación del manual contra el comportamiento ya
implementado y probado en los tickets 01 a 11, y comprobar que los enlaces internos existen.

- Qué se agregó al manual del Operador: una sección **"La guía: a mano, con la cámara o con el lector"** al final del
  bloque 3 (Recibir), una sección **"Usar el lector del Farset F7"** justo después, una línea sobre "Confirmar guía"
  en el bloque 4 (Entregar), un párrafo sobre la lista de coincidencias en el bloque 12 (Consultar) y una fila en la
  tabla "Todo lo que podés hacer, de un vistazo". Mismo registro (voseo) y mismo grupo de vecinos del manual
  (Angélica Ramírez, Torre 5 - 302), con el vocabulario del glosario (Operador, Residente, Anunciado/Recibido).
- Contraste con lo implementado: teclear pasa a mayúsculas solo (ticket 02); "📷 Escanear con cámara", **Detener** y
  **Linterna** (solo si el celular la tiene) y que cerrar el modal apaga la cámara (tickets 06 y 07); los mensajes de
  fallo de la cámara (ticket 05); que leer solo llena el campo y que un "Enter" del lector no recibe el paquete
  (ticket 03); el aviso "La guía tiene N caracteres; el máximo es 50." y que "Recibir" no envía mientras esté pasada, y
  que la cámara no escribe un código de más de 50 (tickets 04 y 07); el aviso ámbar "Ya hay N paquetes con esta guía
  (...)" que no bloquea (ticket 08); la lista de coincidencias para Staff y el aviso neutro para el público en
  Consultar (ticket 09); el interruptor "Este equipo tiene lector" (Activado/Desactivado), que queda guardado en ese
  equipo, que enfoca Guía sin teclado en pantalla, que una segunda lectura reemplaza a la anterior y que en Entregar
  el cursor queda en "Confirmar guía" (tickets 10 y 11).
- Configuración del F7 (de la investigación, `investigacion-oficial.md`): de fábrica el lector NO escribe en páginas web
  (modo de envío por defecto que manda la lectura a otras aplicaciones); Ajustes → Scanning Tools → Scanning Settings;
  modo de envío que escribe en el campo enfocado (con sobrescritura, si existe) y terminador ninguno, tolerando Enter
  y Tab. La salvedad quedó escrita en el propio manual (recuadro "Cuidado"): salen de la documentación del fabricante,
  no se confirmaron en un F7 real y los nombres de las opciones pueden variar. La validación real es el ticket 13.
- Enlaces internos: `#la-guía-a-mano-con-la-cámara-o-con-el-lector`, `#4-entregar-un-paquete` y
  `#3-recibir-un-paquete` existen como encabezados (comprobado con un script).
- Decisión menor: la explicación de la configuración del F7 vive en el manual del Operador porque es quien tiene el
  equipo en la mano; no se tocó el manual de Administrador ni el README del directorio.
