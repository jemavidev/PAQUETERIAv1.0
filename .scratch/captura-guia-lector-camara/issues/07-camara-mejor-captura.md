# 07 — Cámara: mejor captura (resolución, linterna, reintentos espaciados y lectura de más de 50 caracteres)

**What to build:** sin restricciones, Chrome entrega vídeo a 640x480, una entrada pobre para códigos de barras lineales, y el bucle de lectura reintenta sin pausa mientras no hay código a la vista (más CPU y batería de las necesarias). Con este ticket el escaneo con cámara de los celulares (y de la cámara de 13 MP del F7) captura mejor sin cambiar de librería ni de versión de lectura: pide una resolución mayor, ofrece linterna solo cuando el celular la reporta y espacia los reintentos. Además, una lectura de más de 50 caracteres no se escribe en el campo y avisa. Los formatos de código no se restringen.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 2 a 7, 17, 18 y 35).

**Blocked by:** 06 — Cámara: un solo flujo, botón "Detener" y cierre que la apaga.

**Status:** done

- [x] La cámara se pide trasera y con resolución **ideal** de 1280x720 (no exacta, para no fallar en cámaras que no la dan); verificado capturando lo que el escáner le pide al navegador en la cámara simulada.
- [x] Aparece un botón de linterna **solo** si la cámara activa reporta esa capacidad; al pulsarlo enciende y apaga la linterna. Si el celular no la reporta, el botón no aparece. Al detener o terminar el escaneo, el botón desaparece y la linterna queda apagada.
- [x] Mientras no hay ningún código a la vista, la cantidad de intentos de decodificación por segundo queda acotada (no es un bucle sin pausa); se verifica midiendo con una cámara simulada sin código, con un límite razonable que el ticket fija y deja escrito.
- [x] Con un código a la vista, la lectura sigue ocurriendo en un tiempo razonable (un QR simulado se lee en pocos segundos).
- [x] Los formatos no se restringen: un QR simulado de menos de 50 caracteres se lee y se escribe tal como se leyó (sin pasarlo a mayúsculas en el campo; la normalización sigue siendo del servidor al guardar).
- [x] Una lectura de más de 50 caracteres **no** se escribe en el campo; se muestra un mensaje con el largo leído y el máximo de 50 y la cámara se apaga como con cualquier lectura, de modo que el Operador vuelve a pulsar "Escanear" o teclea la guía. Verificado con un QR simulado de 60 caracteres.
- [x] Aplica igual a "Confirmar guía" de Entregar; las pruebas de los tickets 05 y 06 siguen pasando.
- [x] Notas: el comportamiento en iPhone y la calidad de lectura con etiquetas reales no se pueden probar aquí y quedan para la prueba de campo (ticket 13).

## Verificación

- Vistas fallar primero en navegador real: 4 de las 7 pruebas de `tests/browser/test_camara_captura.py` fallaban
  (resolución, linterna, reintentos, y la lectura de más de 50 en Recibir; la de "Confirmar guía" también). Medido
  antes del cambio: **119 intentos de decodificar en 2 s** con la cámara apuntando a nada (≈60 por segundo).
  Ahora pasan las 7 y las 39 del seam completo (`pytest -m browser`).
- Resolución: el escáner le pide al navegador `facingMode: environment` con `width` y `height` **ideales** de
  1280 y 720 (nunca `exact`, para que una cámara que no la da igual arranque). Verificado capturando lo que llega a
  `getUserMedia` en la cámara simulada. Se usa `decodeFromConstraints` en vez de `decodeFromVideoDevice(null, ...)`;
  mismo motor y misma versión de lectura.
- Linterna: el botón "Linterna" aparece solo si la pista de la cámara activa reporta la capacidad `torch` (la
  cámara simulada por defecto no la reporta: no aparece); al pulsarlo aplica `advanced: [{torch: true}]` y vuelve a
  apagar con el segundo toque ("Apagar linterna" mientras está encendida). Al detener o terminar el escaneo el botón
  desaparece y la linterna se apaga explícitamente antes de soltar la cámara.
- Reintentos espaciados: `timeBetweenDecodingAttempts` de 100 ms; con la cámara sin código a la vista quedan entre
  1 y 30 intentos en 2 s (el límite de la prueba; medido de 119 antes). Con un código a la vista la lectura sigue
  siendo rápida: un QR simulado se lee en menos de 6 s.
- Formatos sin restringir (decisión 6 del grilling): el QR simulado se lee y se escribe tal como se leyó
  (`gu-77` en minúsculas; la normalización sigue siendo del servidor al guardar).
- Regla de los 50 para la cámara: una lectura de exactamente 50 caracteres se escribe; una de 51 no se escribe,
  muestra "El código leído tiene 51 caracteres; el máximo es 50. Prueba con otro código de la etiqueta o escribe la
  guía a mano." (cuenta la forma normalizada), apaga la cámara como con cualquier lectura y deja "Escanear"
  disponible. Igual en "Confirmar guía" de Entregar (60 caracteres, una prueba).
- Regresión: `test_captura_guia`, `test_packages`, `test_search`, `test_announce_new`, `test_customers_manage`,
  `test_layout` y `test_cache_headers` en verde (618 pruebas web); los tickets 05 y 06 siguen pasando.
- Decisión menor: `focusMode` no se pide (Chrome Android ya enfoca en continuo; Safari no lo implementa), como
  dice la investigación. Sin clases nuevas de Tailwind: los botones nuevos copian las del botón "Escanear".
- No probado aquí, queda para la prueba de campo (ticket 13): el comportamiento en iPhone/Safari, la calidad de
  lectura con etiquetas reales (arrugadas, brillantes, códigos pequeños) y si `1280x720` mejora de verdad la tasa
  de lectura de códigos lineales en los celulares y en la cámara del F7 (no hay fuente que lo cuantifique).
