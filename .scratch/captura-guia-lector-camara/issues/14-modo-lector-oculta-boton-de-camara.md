# 14 — Modo lector: sin botón de cámara (revierte una decisión del ticket 10)

**Origen:** reporte en vivo de Jesús probando en el Farset F7 real (2026-09-22), después del despliegue a
`test.papyrus.com.co`. Al tocar "Escanear con cámara" aparecía el botón "Detener" (el clic sí registraba el
escaneo) pero la sección quedaba en negro, sin capturar nada y sin ningún mensaje de error — consistente con
que `getUserMedia` obtiene un stream, pero ese stream no trae video real (motor de escaneo del propio equipo
compitiendo por el sensor, cámara equivocada, o algo similar; no se llegó a una causa exacta porque no hacía
falta para la solución). En un celular normal la cámara sigue funcionando bien. Jesús reportó además que, con
el campo Guía enfocado, el gatillo físico del F7 captura la guía "bastante rápido".

**Decisión (Jesús, tras mi análisis de las alternativas):** no se intenta detectar el equipo por software (ni
por `User-Agent`, ni tomando un fotograma para medir si es negro) — ambos caminos son frágiles (el primero
exige conocer el string exacto del modelo y no cubre otro equipo distinto que compren después; el segundo
exige pedir permiso de cámara a TODOS los equipos para poder medir, y puede confundir un lugar oscuro real con
una cámara rota). Se reutiliza el interruptor **"Este equipo tiene lector"** del ticket 10 (ya es la
declaración explícita por equipo que hacía falta) para que, además de mover el foco, **oculte el botón
"Escanear con cámara"** por completo. Con el interruptor activado, el único camino para cargar la guía es el
lector físico; con el interruptor apagado (el default, celulares normales), nada cambia.

Esto **revierte** un criterio explícito del ticket 10 ("el botón de la cámara sigue disponible ... por si una
etiqueta dañada no se deja leer") y del manual del Operador ("El botón de la cámara sigue disponible por si
una etiqueta dañada no se deja leer") — con evidencia real de que, en el único equipo con lector que existe
hoy, ese botón nunca funciona, deja de tener sentido ofrecerlo ahí.

**Blocked by:** 10 — Modo lector: interruptor por equipo y foco al abrir Recibir; 11 — Modo lector en Entregar.

**Status:** done

- [x] Con el modo lector activado, el botón "Escanear con cámara" de Recibir y de "Confirmar guía" (Entregar)
      queda oculto (`display:none`), en cualquier fila de la página, incluidas las que la búsqueda en vivo de
      /paquetes agregue después sin recargar.
- [x] Con el modo lector apagado (el default), el botón sigue exactamente igual que siempre.
- [x] Alternar el interruptor oculta o muestra el botón al instante, sin recargar la página.
- [x] El manual del Operador ya no dice que el botón de cámara "sigue disponible" con el modo activado.

## Verificación

- Vistas fallar primero en navegador real: 4 pruebas nuevas fallaban (botón oculto en Recibir, en una fila
  nunca abierta, al alternar en vivo, y en "Confirmar guía" de Entregar); una prueba existente del ticket 10
  ("el botón de la cámara sigue disponible con el modo activo") fijaba el criterio contrario y hubo que
  reescribirla a propósito -- documenta la reversión, no un error mío. Ahora pasan las 23 de
  `tests/browser/test_modo_lector.py` + `test_modo_lector_entregar.py`, y las 71 del seam completo.
- Implementación: puro CSS. El interruptor del menú de cuenta (`base.html`) pone un atributo
  `data-modo-lector-activo` en `<html>` (antes solo tocaba `aria-checked`/el texto del ítem); el bloque de
  captura (`_recibir_paquete.html`) agrega la regla `html[data-modo-lector-activo] .scan-btn { display:none;
  }`. Sin JS por fila ni re-escaneo del DOM: se aplica solo con que el navegador lea la hoja de estilos, así
  que cubre de entrada cualquier modal que la búsqueda en vivo agregue después, y reacciona al instante si el
  interruptor se alterna sin recargar la página (probado: abrir el modal, alternar, reabrir, verificar oculto;
  alternar de nuevo, reabrir, verificar visible).
- Regresión: `test_captura_guia`, `test_packages`, `test_search`, `test_announce_new`,
  `test_announce_sugerencia_contacto_externo`, `test_customers_manage`, `test_layout` (649 pruebas web) en
  verde.
- Manual del Operador actualizado en las dos secciones que mencionaban la cámara junto al modo lector.
- **Lo que sigue sin saberse:** la causa exacta de por qué la cámara del F7 no entrega video (motor de
  escaneo compitiendo por el sensor, cámara equivocada seleccionada, u otra cosa). No hizo falta averiguarlo
  para esta solución -- si el cliente compra a futuro OTRO equipo con lector físico y su cámara SÍ funciona
  bien, igual quedará sin botón de cámara mientras tenga el interruptor activado (limitación aceptada: la
  declaración es por equipo, no por si la cámara de ese equipo funciona o no).
