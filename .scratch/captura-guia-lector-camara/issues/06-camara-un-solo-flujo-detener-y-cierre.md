# 06 — Cámara: un solo flujo, botón "Detener" y cierre que la apaga

**What to build:** hoy un doble clic en "Escanear con cámara" abre dos flujos de cámara y, al cerrar el modal, solo se libera uno: la cámara queda encendida detrás del modal hasta recargar la página. Tampoco hay cómo cancelar un escaneo sin haber leído nada. Con este ticket el escaneo tiene un ciclo de vida claro: el botón queda deshabilitado mientras escanea, hay un botón "Detener", y cualquier forma de terminar (leer un código, detener, cerrar el modal con ✕, tocar el fondo o pulsar Escape) deja **cero flujos de cámara vivos**. Aplica a Recibir y a "Confirmar guía" de Entregar.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 8 a 11 y 59).

**Blocked by:** 05 — Cámara: los fallos se ven.

**Status:** done

- [x] Mientras hay un escaneo en curso, el botón "Escanear con cámara" queda deshabilitado: un doble clic abre un único flujo de cámara.
- [x] Hay un botón "Detener" visible mientras escanea: al pulsarlo el video se oculta, la cámara se apaga, el campo queda como estaba y el botón "Escanear" vuelve a estar disponible.
- [x] Al leer un código el campo se llena, el video se oculta, la cámara se apaga y "Escanear" vuelve a estar disponible para otra lectura (usa la cámara simulada con un QR dibujado para producir una lectura real).
- [x] Cerrar el modal con la ✕, tocando el fondo o con Escape apaga la cámara: no queda ningún flujo vivo, incluidos los que se hubieran abierto por un doble toque.
- [x] Reabrir el modal y escanear otra vez funciona (el estado se reinició).
- [x] Pruebas en navegador real con la cámara simulada, verificando el estado de todos los flujos creados (ninguno "vivo" al final de cada camino) en Recibir, y al menos un camino en "Confirmar guía" de Entregar.
- [x] Lo que se lee y cómo se rellena el campo no cambia respecto de hoy (solo el ciclo de vida).

## Verificación

- Vistas fallar primero en navegador real: 5 de las 9 pruebas de `tests/browser/test_camara_ciclo.py` fallaban
  (doble clic con dos flujos, sin botón "Detener", el flujo que llega tarde tras cancelar, y el ciclo en
  "Confirmar guía"); las otras 4 ya pasaban (lectura, y cerrar con ✕/fondo/Escape en el camino de un solo clic)
  y quedan fijadas. Ahora pasan las 9 y las 32 del seam completo.
- Un solo flujo: `dblclick` sobre "Escanear" deja `llamadas == 1` y una sola pista viva; el botón queda
  deshabilitado mientras escanea (con estilo propio: opacidad y cursor) y aparece "Detener".
- "Detener" apaga la cámara (todas las pistas `ended`), oculta el video, quita su propio botón, vuelve a habilitar
  "Escanear" y deja el campo como estaba (la prueba había tecleado "abc").
- Una lectura real (un QR dibujado con el propio ZXing frente a la cámara simulada) llena el campo tal como se
  leyó, oculta el video, apaga la cámara y deja "Escanear" listo para una segunda lectura, que también funciona.
- Cerrar con la ✕, tocando el fondo o con Escape apaga la cámara; reabrir el modal y escanear otra vez funciona
  (segunda llamada a la cámara).
- Carrera con una cámara lenta (aviso de permiso sin contestar): cancelar con "Detener" ANTES de que la cámara
  responda no deja el flujo que llega tarde encendido (se reinicia el lector cuando la promesa por fin se
  resuelve). El helper de cámara simulada ganó `retardo_ms` para poder probarlo.
- Mismo ciclo en "Confirmar guía" de Entregar (una prueba: doble clic, detener, escanear y cerrar con Escape).
- Regresión: `test_captura_guia`, `test_packages`, `test_search`, `test_announce_new`, `test_customers_manage`,
  `test_layout` y `test_cache_headers` en verde (618 pruebas web en tres corridas).
- Decisión menor: el registro interno pasó de un mapa de lectores a un mapa de "escaneos" (lector, botón, video,
  botón "Detener", terminado), para que cualquier forma de terminar restablezca todo igual. El botón "Detener" se
  crea al pulsar "Escanear" y copia las clases del botón "Escanear" (ninguna clase nueva de Tailwind: no hace falta
  reconstruir el CSS).
