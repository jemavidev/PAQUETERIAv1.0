# 01 — Aislar la captura de guía del script compartido de Recibir/Entregar (prefactor)

**What to build:** hoy el comportamiento de captura de guía (el escáner de cámara y la comparación de guía que llena el ✅/⚠️ de "Confirmar guía" en Entregar) vive mezclado, dentro del mismo `<script>` compartido, con el historial diferido, los modales, el selector de apartamento y el anti doble-envío. Ese script tiene además pruebas que verifican substrings de su contenido, y sus propios comentarios avisan de lo frágil que es editarlo. Separar la captura de guía en su propio bloque de comportamiento dentro del componente compartido, **sin cambiar nada de lo que ve o hace el Staff**. Es preparación: los tickets 03, 05, 06 y 07 reescriben esta parte y así no rozan el resto.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historia 65; no agrega comportamiento nuevo).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] El escáner de cámara y la comparación de guía viven en su propio bloque, distinto del resto del script compartido (modales, historial diferido, selector de apartamento, anti doble-envío), que queda intacto.
- [ ] Las páginas que hoy usan Recibir o Entregar (/paquetes, /announce, /consultar) siguen incluyendo el comportamiento exactamente una vez cada una: nada duplicado, nada faltante.
- [ ] Lo que ve y hace el Staff no cambia: el botón "Escanear con cámara" de Recibir y de "Confirmar guía" sigue llenando el campo, y el ✅ o ⚠️ de Entregar sigue apareciendo al escribir o leer una guía.
- [ ] Las pruebas web existentes de /paquetes, /announce y /consultar pasan sin modificarse. Si alguna verifica un texto que se movió por diseño, se ajusta el mínimo y queda escrito en este ticket por qué.
- [ ] Las pruebas que verifican por substring que la advertencia de nombre distinto del Anunciante quedó apagada siguen pasando.
- [ ] No hay cambios de esquema, de rutas ni de comportamiento visible.
