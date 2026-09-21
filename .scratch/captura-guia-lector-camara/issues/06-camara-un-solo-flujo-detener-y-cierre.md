# 06 — Cámara: un solo flujo, botón "Detener" y cierre que la apaga

**What to build:** hoy un doble clic en "Escanear con cámara" abre dos flujos de cámara y, al cerrar el modal, solo se libera uno: la cámara queda encendida detrás del modal hasta recargar la página. Tampoco hay cómo cancelar un escaneo sin haber leído nada. Con este ticket el escaneo tiene un ciclo de vida claro: el botón queda deshabilitado mientras escanea, hay un botón "Detener", y cualquier forma de terminar (leer un código, detener, cerrar el modal con ✕, tocar el fondo o pulsar Escape) deja **cero flujos de cámara vivos**. Aplica a Recibir y a "Confirmar guía" de Entregar.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 8 a 11 y 59).

**Blocked by:** 05 — Cámara: los fallos se ven.

**Status:** ready-for-agent

- [ ] Mientras hay un escaneo en curso, el botón "Escanear con cámara" queda deshabilitado: un doble clic abre un único flujo de cámara.
- [ ] Hay un botón "Detener" visible mientras escanea: al pulsarlo el video se oculta, la cámara se apaga, el campo queda como estaba y el botón "Escanear" vuelve a estar disponible.
- [ ] Al leer un código el campo se llena, el video se oculta, la cámara se apaga y "Escanear" vuelve a estar disponible para otra lectura (usa la cámara simulada con un QR dibujado para producir una lectura real).
- [ ] Cerrar el modal con la ✕, tocando el fondo o con Escape apaga la cámara: no queda ningún flujo vivo, incluidos los que se hubieran abierto por un doble toque.
- [ ] Reabrir el modal y escanear otra vez funciona (el estado se reinició).
- [ ] Pruebas en navegador real con la cámara simulada, verificando el estado de todos los flujos creados (ninguno "vivo" al final de cada camino) en Recibir, y al menos un camino en "Confirmar guía" de Entregar.
- [ ] Lo que se lee y cómo se rellena el campo no cambia respecto de hoy (solo el ciclo de vida).
