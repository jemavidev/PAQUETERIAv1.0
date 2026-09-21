# 03 — El Enter (o Tab) del lector no recibe el paquete

**What to build:** hoy un lector que actúa como teclado y manda un Enter al final de la lectura envía el formulario de Recibir: el paquete queda `Recibido` al instante con Normal/Bueno por defecto, sin fotos, sin elegir Residente y sin registrar un posible pago contra entrega. Con este ticket, una lectura **solo llena la Guía**: un Enter o Tab al final deja el Paquete `Anunciado`, el modal abierto y la guía escrita; el Operador confirma con el botón "Recibir". La regla vale para lector físico y para tecleo a mano, y llega a /paquetes, /announce y al Recibir de /consultar por reusar el mismo componente.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 28, 29, 57 y 58).

**Blocked by:** 01 — Aislar la captura de guía del script compartido; 02 — Prueba en navegador real para el modal Recibir.

**Status:** done

- [x] En el modal Recibir, teclear una guía rápido y pulsar Enter deja el Paquete `Anunciado` (verificado en la BD), el modal abierto y la guía escrita en el campo.
- [x] Lo mismo con Tab: el campo conserva el valor y no se envía nada.
- [x] Después de eso, pulsar "Recibir" deja el Paquete `Recibido` con la guía guardada (en mayúsculas, como hoy).
- [x] La guardia no depende de una sola vía: si el formulario intenta enviarse por un camino que no sea pulsar el botón "Recibir" mientras el foco está en el campo Guía, tampoco se recibe el paquete.
- [x] Enter en los demás campos del modal se comporta como hoy (el ticket solo protege el campo Guía).
- [x] "Confirmar guía" de Entregar y de /consultar no cambia (ya está fuera del formulario, un Enter allí no envía nada): sigue igual.
- [x] El mismo comportamiento se verifica en /paquetes en navegador real; para /announce y el Recibir de /consultar basta comprobar por HTTP que cargan el mismo componente con el mismo comportamiento.
- [x] Las pruebas web existentes de Recibir pasan sin modificarse.

## Verificación

- Vistas fallar primero en navegador real (Chromium con Playwright, seam del ticket 02): el Enter tras la
  guía recibía el paquete al instante; recibir después del Enter fallaba porque ya estaba recibido; y un
  envío con el foco en Guía sin gesto sobre el botón también lo recibía. Los otros tres casos (Tab, botón
  activado con teclado, Enter en otro campo) ya pasaban y fijan lo que no debe cambiar.
- Ahora pasan las 7 pruebas de `tests/browser/test_guia_enter.py` (y las 8 del seam completo con las del
  ticket 02): Enter deja el Paquete `Anunciado` en la BD, sin ningún POST a /recibir, con el modal abierto y
  la guía escrita; Tab conserva el valor sin enviar; "Recibir" después del Enter recibe con la guía en
  mayúsculas; `requestSubmit()` con el foco en Guía sin gesto sobre el botón no envía; Enter con el foco en
  el botón "Recibir" sí recibe; Enter en el campo de Apartamento sigue enviando como hoy; y Enter en
  "Confirmar guía" de Entregar no entrega nada (comprobado en navegador real, antes solo leído del HTML).
- HTTP: el bloque de captura es idéntico en /paquetes, /consultar, /announce y /residentes
  (`tests/web/test_captura_guia.py`), así que la guardia llega a /announce y al Recibir de /consultar.
- Pruebas web existentes de Recibir sin modificarse: `test_packages` (238) y `test_captura_guia` en verde.
- Hallazgo: el primer intento rompió 4 pruebas de filtros de `test_packages`, que verifican por substring
  que nombres como `ANA` no aparecen en la página, y el `<script>` de captura viaja en ella. La causa fue
  mía: la constante `VENTANA_GESTO_MS` y un comentario con `"ANA"` contenían ese texto. Se pasó a camelCase
  y a comentarios sin nombres propios, con un aviso en el propio script para el próximo que lo edite.
- Decisión menor: un click simulado por envío implícito no distingue "pulsó Recibir" de "Enter en el
  campo" (`submitter` es el mismo botón), así que el segundo nivel de la guardia compara el gesto sobre el
  botón (puntero o teclado) de los últimos 1.5 s con el foco en Guía al enviar. Riesgo conocido, no
  probado: un lector de pantalla que active el botón sin gesto de puntero con el foco aún en Guía.
