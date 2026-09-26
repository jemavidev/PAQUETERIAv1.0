# 411 — Pantalla "Respaldos" con el look and feel del resto de la app: sencilla, con modales

**Pedido original (Jesús, 2026-09-26):** "esas mismas funcionalidades que maneja la vista de respaldos, las reflejes con
las mismas políticas de look and feel de todo el aplicativo, donde las cosas deberían ser sencillas, fáciles de
identificar y con las funcionalidades a la mano, amigable para que lo vea cualquier usuario, si es información no toda
se debe mostrar enseguida, podrías incluir modales y hacer todo más fácil".

**Status:** desplegado en test (`53b6964`), pendiente confirmar en vivo

## Alcance

- Mismas funciones que hoy (estado del último respaldo, "Respaldar ahora", lista y descarga `.zip`, comando de
  restauración, copia y descarga de fotos); ninguna nueva.
- Estilo de las demás pantallas (tarjetas, íconos, componentes `modal`/botones de la app); lo esencial a la vista y el
  detalle (explicaciones, comando de restauración, pasos) en modales.
- Se prototipa primero en localhost (capturas en escritorio y celular) y, aprobado, se pasa al código real con pruebas.

## Prototipo (2026-09-26)

Rama `prototipo/respaldos-amigable` (sin push, NO se mergea), servidor en `http://localhost:8011/administracion/respaldos`
con `?variant=A|B|C` (flechas de la barra flotante o del teclado). Misma BD y carpetas locales que `:8010`.
- **A · Panel de control:** estado grande (verde/rojo) con "Respaldar ahora"; dos tarjetas (Respaldos guardados, Fotos)
  que abren modales; "¿Cómo funciona?" en modal.
- **B · Lista como /paquetes:** barra de estado en una línea, cada respaldo como tarjeta con botones de ícono
  (descargar, recuperar, detalle); fotos en su tarjeta.
- **C · Por tareas:** "¿Mis datos están a salvo?", "Quiero una copia", "Quiero recuperar datos" (asistente: elegir
  fecha → instrucciones), "Descargar las fotos".
Común a las tres: fechas amigables ("sáb 26 sep · 7:00 a. m."), la recuperación explicada en lenguaje simple con el
comando en un modal, y lo técnico (bucket, retenciones) solo en "¿Cómo funciona?". Sin scroll lateral a 390 px y sin
errores de consola.

**Elegida: B** ("me gusta la B, aplícala", 2026-09-26). Se reescribe en la plantilla real con pruebas; A y C quedan solo en la rama del prototipo.

## Implementado (2026-09-26)

Variante B reescrita en la plantilla real: estado en una línea (a pedido en curso / interrumpido / falló si es más
reciente que el último registro / todo respaldado / último falló / sin registro), tarjetas por respaldo con descargar,
recuperar (modal con advertencia, pasos y comando) y detalle (modal); tarjeta de fotos con modal de 2 pasos (copiar,
descargar); "¿Cómo funciona?" en modal. Fechas amigables calculadas en la ruta (`fecha_amigable`). En celular el tamaño
se oculta en la tarjeta (queda en el detalle). Pruebas: 2 ajustadas a propósito (formato de fecha, tarjeta `<article>`),
23 en verde. Tailwind `?v=110`.
