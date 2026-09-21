# 13 — Prueba de campo en F7, Android e iPhone

**What to build:** ninguna prueba automática puede confirmar lo que solo el equipo real responde: si el modo del F7 que escribe en el campo enfocado realmente escribe en un campo de Chrome, si su gatillo funciona con un formulario web, si el equipo trae Chrome, y cómo leen las cámaras reales las etiquetas reales. Ejecutar el protocolo de prueba de campo (última sección de la investigación) con al menos un F7, un Android normal y un iPhone, y dejar los resultados escritos. **No es un ticket para un agente**: lo ejecuta Jesús con el equipo físico, y necesita que la feature esté desplegada en `test.papyrus.com.co` (el despliegue solo se hace cuando Jesús lo pide).

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historia 64; sección Further Notes, "Lo que NO se pudo verificar sin el equipo"). Protocolo: `.scratch/captura-guia-lector-camara/investigacion-oficial.md`, sección "Protocolo de prueba de campo para el F7".

**Blocked by:** 12 — Manual del Operador y configuración del F7 (todo lo demás ya está terminado por transitividad); y que Jesús pida desplegar a `test.papyrus.com.co`.

**Status:** pendiente — requiere a Jesús y el equipo físico; no es tomable por un agente

- [ ] Identificado el modelo exacto del F7 (etiqueta trasera: ¿F7, F7-Pro o F7T?), su versión de Android, si trae Chrome (y su versión) y si trae Google Play.
- [ ] Capturas de Ajustes, Scanning Tools, Scanning Settings con el modo de envío y el terminador que trae de fábrica.
- [ ] Confirmado si el modo de envío que escribe en el campo enfocado (con y sin sobrescribir) escribe en un campo de texto normal de Chrome, y si funciona en el campo Guía del modal Recibir.
- [ ] Confirmado si el gatillo lateral y el botón flotante funcionan con Chrome abierto sobre el formulario.
- [ ] Probado con terminador Ninguno, Enter y Tab: en ningún caso el paquete se recibe solo (regla del ticket 03), y una segunda lectura reemplaza la anterior (ticket 10).
- [ ] Una guía real por cada transportadora que llegue (Servientrega, Interrapidísimo, Coordinadora, Envía, TCC, 4-72, Deprisa, Mercado Libre, y las que falten): qué código trae la etiqueta (lineal, QR o ambos), qué texto devuelve el lector y la cámara, y cómo se compara con el número impreso.
- [ ] Lectura con la cámara en el F7, en un Android normal y en un iPhone (Safari): éxito sí o no y tiempo aproximado; linterna y resolución reportadas por el navegador donde se pueda ver.
- [ ] Los resultados quedan escritos en la carpeta de esta feature, y todo ajuste que salga se abre como ticket nuevo (por ejemplo, si un F7 no escribe en el campo de Chrome, o si conviene subir la versión de la librería de lectura).
