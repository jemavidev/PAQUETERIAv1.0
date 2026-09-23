# 376 — Modo lector: abrir el teclado al enfocar Guía para que el gatillo del F7 escriba

**Reporte original (Jesús), probando en el F7 real:** "la lectura desde el FARSET F7 solo funciona si se habilita
el teclado para que la lectura la escriba el lector ... si solo se ingresa con el lector activado ... solo queda el
foco en el input de la guia y al presionar el boton del lector esto no realiza la lectura ... no funciona si el
teclado no esta activo". Celular (cámara) y escritorio funcionan bien.

**Status:** descartado — NO funcionó en el F7 real (probado por Jesús, 2026-09-22: ninguna de las dos variantes
escribe; el gatillo solo escribe con el teclado abierto a mano). Código revertido el 2026-09-23 sin llegar a commitearse
(`enfocarParaLector` vuelve a solo enfocar y seleccionar). Siguiente camino, fuera de la web: ajustes del propio equipo
(modo de salida "simular teclas" en Scanning Settings, o "mostrar teclado virtual con el teclado físico" de Android).

## Diagnóstico

El modo de envío del F7 que escribe en el campo enfocado no simula teclas: entrega el texto por la conexión de
entrada del teclado en pantalla de Android, que solo existe mientras el teclado está activo sobre el campo. Con el
modo lector el foco lo pone el código (`enfocarParaLector`, `_recibir_paquete.html`) y Chrome no abre el teclado,
así que el campo queda enfocado pero sin conexión: el gatillo decodifica y la lectura se pierde. Tocar el campo abre
el teclado y ahí sí escribe. Quitar `inputmode="none"` ([[374]]) era necesario pero no suficiente.

## Decisión

- Al enfocar por el modo lector (dentro del toque del Operador que abre el modal), se pide a Chrome que abra el
  teclado con la VirtualKeyboard API (`navigator.virtualKeyboard.show()`, exige `virtualkeyboardpolicy="manual"`
  en el campo y activación del usuario). La política `manual` se pone solo mientras dura la llamada: después el
  campo vuelve al comportamiento normal (tocarlo abre el teclado como siempre).
- Sin la API (o sin activación de usuario, p. ej. un modal que el servidor reabre al cargar), queda como antes:
  tocar el campo sigue funcionando.
- **Variante en prueba (temporal):** con `?teclado_lector=ocultar` en la URL (queda guardado en el equipo;
  `?teclado_lector=mostrar` vuelve al default) el teclado se abre y se esconde enseguida, para probar si la
  conexión sobrevive sin el teclado visible. Tras la prueba de Jesús se deja solo la variante que funcione.

## Verificación

- `tests/browser/test_modo_lector.py`: con la API simulada, abrir Recibir en modo lector llama `show()` (y
  `hide()` con la variante `ocultar`), apagado no la llama, y el campo termina sin la política `manual`.
- Resultado: 4 pruebas nuevas (2 fallaban antes del cambio); seam `browser` completo 75/75 y `test_captura_guia`,
  `test_packages`, `test_search`, `test_announce_new` 408/408 en verde.
- Pendiente: Jesús prueba ambas variantes en el F7 contra el servidor local por red.
