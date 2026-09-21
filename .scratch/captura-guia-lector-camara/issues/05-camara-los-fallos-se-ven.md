# 05 — Cámara: los fallos se ven (mensajes claros)

**What to build:** hoy, si el permiso de cámara se niega o no hay cámara, queda un cuadro de video negro visible sin ningún mensaje y un error en la consola; si el script del lector de códigos no carga, el botón simplemente no hace nada. Con este ticket cada fallo del escaneo con cámara muestra un mensaje claro, en español y sin jerga técnica, junto al botón; el video se oculta y el campo Guía queda siempre editable. Aplica por igual al botón de Recibir y al de "Confirmar guía" (Entregar), que comparten el comportamiento. Este ticket también crea el helper de **cámara simulada** para pruebas de navegador, que reutilizan los tickets 06 y 07.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 12 a 16 y 59).

**Blocked by:** 01 — Aislar la captura de guía del script compartido; 02 — Prueba en navegador real para el modal Recibir.

**Status:** done

- [x] Permiso de cámara negado: se muestra un mensaje que lo dice y sugiere habilitarlo o teclear la guía; el video queda oculto (no hay cuadro negro).
- [x] Sin cámara disponible, y cualquier otro error al iniciar: cada caso muestra un mensaje distinto y claro; el video queda oculto.
- [x] El script del lector no carga (red caída o recurso bloqueado): se muestra un mensaje que dice que no se pudo cargar el escáner y que se escriba la guía a mano. Hoy no muestra nada.
- [x] El mensaje existente para "sin soporte de cámara o contexto sin HTTPS" ("Cámara no disponible; escribe la guía a mano.") sigue igual.
- [x] Después de cualquiera de esos fallos el campo Guía sigue editable y "Recibir" funciona con una guía tecleada a mano.
- [x] Un mensaje de fallo anterior se limpia cuando el siguiente intento de escaneo arranca bien.
- [x] El helper de cámara simulada (sustituye el acceso a la cámara en el navegador de prueba, con éxito o con cada tipo de error) queda documentado y listo para reusar.
- [x] Pruebas en navegador real: un caso por cada tipo de fallo en Recibir, y al menos uno en "Confirmar guía" de Entregar.

## Verificación

- Vistas fallar primero en navegador real: 9 de las 10 pruebas fallaban (sin mensaje, cuadro de video negro
  visible, script que no carga sin aviso); la décima, el mensaje de "sin soporte de cámara", ya pasaba y queda
  fijada. Ahora pasan las 10 de `tests/browser/test_camara_fallos.py` y las 23 del seam completo.
- Causa del silencio: `decodeFromVideoDevice` devuelve una PROMESA que rechaza cuando el navegador niega la
  cámara, y el `try/catch` síncrono de antes nunca la atrapaba; y `onerror` del `<script>` era una función vacía.
- Mensajes (cada uno distinto, en español, sin jerga; la prueba comprueba que los cuatro difieren): permiso
  negado ("Permiso de cámara negado; habilítalo en el navegador o escribe la guía a mano."), sin cámara ("No se
  encontró una cámara en este equipo; ..."), cámara en uso por otra aplicación, y un genérico ("No se pudo iniciar
  la cámara; ...") para cualquier otro. El script del lector que no carga avisa "No se pudo cargar el escáner; ...".
  El mensaje de "sin soporte o sin HTTPS" no cambió.
- En todos los casos el video queda oculto, la cámara (si llegó a abrirse) apagada y el campo Guía editable: la
  prueba teclea una guía a mano después del fallo y "Recibir" la guarda. Un mensaje anterior se limpia al
  arrancar el siguiente intento (verificado: primero permiso negado, luego un intento con cámara que arranca).
  Vale también para "Confirmar guía" de Entregar (una prueba, comparte el mismo código).
- Helper de cámara simulada (`tests/browser/_camara.py`, fixture `camara`, documentado en su docstring): sustituye
  `getUserMedia` con un error de nombre estándar (`con_error`) o con un flujo de video real de un lienzo, con o sin
  QR dibujado con el propio ZXing (`con_video`), y `estado()` reporta llamadas, restricciones y el estado de cada
  pista (`live`/`ended`). Lo reutilizan los tickets 06 y 07.
- Regresión: `test_packages`, `test_search`, `test_announce_new`, `test_customers_manage`, `test_layout` y
  `test_captura_guia` en verde (665 pruebas web repartidas en dos corridas).
- Hallazgo, mismo tipo que en el ticket 03: `test_search::test_boton_entregar_sin_guia_no_muestra_confirmar_guia`
  exige que el texto "Confirmar guía" no aparezca en la página de un paquete sin guía, y un comentario JS que
  escribí en el ticket 03 lo contenía. No lo vi entonces porque no corrí `test_search` en ese ticket. Corregido
  aquí (el comentario dice "el campo de confirmación de guía"); en adelante se corren esos archivos en cada
  ticket que toque el script compartido.
