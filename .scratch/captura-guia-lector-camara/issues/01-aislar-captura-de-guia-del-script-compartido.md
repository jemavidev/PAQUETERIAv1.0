# 01 — Aislar la captura de guía del script compartido de Recibir/Entregar (prefactor)

**What to build:** hoy el comportamiento de captura de guía (el escáner de cámara y la comparación de guía que llena el ✅/⚠️ de "Confirmar guía" en Entregar) vive mezclado, dentro del mismo `<script>` compartido, con el historial diferido, los modales, el selector de apartamento y el anti doble-envío. Ese script tiene además pruebas que verifican substrings de su contenido, y sus propios comentarios avisan de lo frágil que es editarlo. Separar la captura de guía en su propio bloque de comportamiento dentro del componente compartido, **sin cambiar nada de lo que ve o hace el Staff**. Es preparación: los tickets 03, 05, 06 y 07 reescriben esta parte y así no rozan el resto.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historia 65; no agrega comportamiento nuevo).

**Blocked by:** None — can start immediately.

**Status:** done

- [x] El escáner de cámara y la comparación de guía viven en su propio bloque, distinto del resto del script compartido (modales, historial diferido, selector de apartamento, anti doble-envío), que queda intacto.
- [x] Las páginas que hoy usan Recibir o Entregar (/paquetes, /announce, /consultar) siguen incluyendo el comportamiento exactamente una vez cada una: nada duplicado, nada faltante.
- [x] Lo que ve y hace el Staff no cambia: el botón "Escanear con cámara" de Recibir y de "Confirmar guía" sigue llenando el campo, y el ✅ o ⚠️ de Entregar sigue apareciendo al escribir o leer una guía.
- [x] Las pruebas web existentes de /paquetes, /announce y /consultar pasan sin modificarse. Si alguna verifica un texto que se movió por diseño, se ajusta el mínimo y queda escrito en este ticket por qué.
- [x] Las pruebas que verifican por substring que la advertencia de nombre distinto del Anunciante quedó apagada siguen pasando.
- [x] No hay cambios de esquema, de rutas ni de comportamiento visible.

## Verificación

- Prueba nueva, vista fallar primero (la captura y el resto eran el mismo bloque): en `/paquetes`,
  `/consultar`, `/announce` y `/residentes` hay exactamente un bloque de captura y uno del resto
  (selector de apartamento, historial diferido), distintos entre sí, y los estilos de escaneo salen
  una sola vez (`tests/web/test_captura_guia.py`).
- Pruebas web existentes **sin modificarse**: 149 en `test_search`, `test_announce_new` y
  `test_cache_headers` (más la nueva) y 434 en `test_packages` y `test_customers_manage`, todas verdes.
- Navegador real (Chromium con Playwright contra una segunda instancia de la app, sin tocar el
  servidor de siempre): mismos resultados que antes del movimiento -- el Enter sigue enviando el
  formulario (eso se corrige en el ticket 03), la lectura simulada llena el campo y apaga el flujo, el
  rechazo de la cámara sigue sin mensaje (ticket 05), el doble clic sigue dejando un flujo vivo (ticket
  06) y Escape apaga el flujo del camino de un solo clic.
- Decisión menor: el listener que esconde el modal ya no llama a `stopReaders()`; el bloque de captura
  tiene su propio listener de cierre, con la misma exclusión de `data-open` (traspaso entre modales)
  que tenía el original, así que el comportamiento es el mismo.
