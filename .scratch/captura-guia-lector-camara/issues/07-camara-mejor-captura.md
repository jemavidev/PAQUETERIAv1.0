# 07 — Cámara: mejor captura (resolución, linterna, reintentos espaciados y lectura de más de 50 caracteres)

**What to build:** sin restricciones, Chrome entrega vídeo a 640x480, una entrada pobre para códigos de barras lineales, y el bucle de lectura reintenta sin pausa mientras no hay código a la vista (más CPU y batería de las necesarias). Con este ticket el escaneo con cámara de los celulares (y de la cámara de 13 MP del F7) captura mejor sin cambiar de librería ni de versión de lectura: pide una resolución mayor, ofrece linterna solo cuando el celular la reporta y espacia los reintentos. Además, una lectura de más de 50 caracteres no se escribe en el campo y avisa. Los formatos de código no se restringen.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 2 a 7, 17, 18 y 35).

**Blocked by:** 06 — Cámara: un solo flujo, botón "Detener" y cierre que la apaga.

**Status:** ready-for-agent

- [ ] La cámara se pide trasera y con resolución **ideal** de 1280x720 (no exacta, para no fallar en cámaras que no la dan); verificado capturando lo que el escáner le pide al navegador en la cámara simulada.
- [ ] Aparece un botón de linterna **solo** si la cámara activa reporta esa capacidad; al pulsarlo enciende y apaga la linterna. Si el celular no la reporta, el botón no aparece. Al detener o terminar el escaneo, el botón desaparece y la linterna queda apagada.
- [ ] Mientras no hay ningún código a la vista, la cantidad de intentos de decodificación por segundo queda acotada (no es un bucle sin pausa); se verifica midiendo con una cámara simulada sin código, con un límite razonable que el ticket fija y deja escrito.
- [ ] Con un código a la vista, la lectura sigue ocurriendo en un tiempo razonable (un QR simulado se lee en pocos segundos).
- [ ] Los formatos no se restringen: un QR simulado de menos de 50 caracteres se lee y se escribe tal como se leyó (sin pasarlo a mayúsculas en el campo; la normalización sigue siendo del servidor al guardar).
- [ ] Una lectura de más de 50 caracteres **no** se escribe en el campo; se muestra un mensaje con el largo leído y el máximo de 50 y la cámara se apaga como con cualquier lectura, de modo que el Operador vuelve a pulsar "Escanear" o teclea la guía. Verificado con un QR simulado de 60 caracteres.
- [ ] Aplica igual a "Confirmar guía" de Entregar; las pruebas de los tickets 05 y 06 siguen pasando.
- [ ] Notas: el comportamiento en iPhone y la calidad de lectura con etiquetas reales no se pueden probar aquí y quedan para la prueba de campo (ticket 13).
