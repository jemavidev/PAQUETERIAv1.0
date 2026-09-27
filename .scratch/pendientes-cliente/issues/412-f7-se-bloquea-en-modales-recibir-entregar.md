# 412 — El Farset F7 se queda pensando o se bloquea en los modales Recibir/Entregar, sobre todo al capturar fotos en Recibir

**Pedido original (Jesús, 2026-09-26):** "no se porque al usar este dispositivo para abrir el proyecto ya sea en
localhost o el servidor de test.papyrus.com.co el dispositivo se queda pensando y en ocasiones se bloquea, he notado esto
al interactuar con algunos modales ya sea el de recibir o entregar paquetes, especialmente el de recibir paquetes lo he
notado al tratar de capturar algunas fotos".

**Status:** pendiente

## Alcance

- Pasa igual en localhost y en test.papyrus.com.co, así que no es cosa del servidor: apunta al cliente (JS, cámara, fotos).
- Diagnóstico con `diagnosing-bugs`: reproducir, medir dónde se va el tiempo y corregir la causa real, no el síntoma.

## Diagnóstico (2026-09-26)

- Lazo armado: Playwright + Chromium sin interfaz, viewport 360 px, CPU frenada 6×, `/paquetes?estado=ANUNCIADO`,
  abrir Recibir y agregar 3 fotos de 13 MP (7,8 MB c/u; la subida se intercepta). Mide long tasks del hilo principal
  (sonda validada con un bloqueo de control de 300 ms).
- Resultado en PC: **no reproduce** -- abrir el modal ~210 ms, cada miniatura ~360-430 ms, ninguna long task > 120 ms.
  Una CPU de escritorio frenada no replica el F7 (memoria, GPU, app de cámara de Android que manda Chrome a segundo plano).
- Hechos medidos que pesan en un equipo modesto: `/paquetes?estado=ANUNCIADO` = 1,5 MB de HTML, ~10.600 etiquetas,
  652 SVG, 118 `<script>` y 533 KB de JS en línea -- cada fila anunciada trae sus 5 modales completos (ver, recibir,
  corregir, promover, cancelar), incluido el script de fotos repetido por fila.
- Bloqueado: hace falta correr el mismo lazo sobre el Chrome real del F7 (depuración USB + `adb`), o una captura del
  equipo (grabación de rendimiento de `chrome://inspect`).

## En el F7 real por USB (2026-09-26)

- Equipo: YGF_F7, Android 13, MT6765 (Helio P35), 4 GB RAM, Chrome 153. Acceso: `adb` (regla udev `0e8d`),
  `adb reverse tcp:8010`, `adb forward tcp:9222 localabstract:chrome_devtools_remote`, Playwright `connect_over_cdp`.
  Ojo: con la pantalla apagada o Chrome en segundo plano las mediciones salen falsas (~5 s por miniatura); se dejó
  `svc power stayon usb` (revertir con `adb shell svc power stayon false`).
- Con Chrome al frente: carga de `/paquetes?estado=ANUNCIADO` 1,8 s (local) / 2,4 s (test por WiFi, 1,6 MB sin
  comprimir), abrir Recibir 0,5 s, miniatura 0,5-0,65 s.
- Cámara real (MediaTek, `capture="environment"`), 3 fotos seguidas: cámara abre en 0,5 s, miniatura 1,2 s tras ✓, sin
  recarga de página ni kills de lmkd. Cada foto llega de ~375 KB (1536×2048).
- Hechos laterales: test.papyrus.com.co no comprime (sin `Content-Encoding`); el F7 arrancó con 36 MB libres y 450 MB
  en swap (kswapd activo).
- **Sin reproducir aún.** Grabación HITL de 15 min (`grabar_todo.sh` en el tmp del job) terminó sin actividad del usuario.
- 2ª grabación (2026-09-26 21:14-21:17, Jesús usando el F7 a mano): 3 capturas de cámara desde Chrome, sin bloqueo.
  Logcat sin kills por memoria ni ANR (solo cierres normales de renderers "isolated not needed"); memoria estable
  (~75 MB libres, 440 MB en swap). Chrome tenía 4 pestañas: 2× test `/paquetes` y 2× v1 `paquetex.papyrus.com.co`.
- **Sigue sin reproducirse; queda en espera de que vuelva a ocurrir.** Cuando ocurra: conectar el F7 por USB cuanto
  antes y sacar `adb logcat -d` + `adb bugreport` (el buffer de logcat guarda los minutos previos).
