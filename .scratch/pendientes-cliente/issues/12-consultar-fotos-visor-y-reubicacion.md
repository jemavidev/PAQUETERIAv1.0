# 12 — `/consultar`: fotos dentro de "Recibido" + visor con zoom y navegación

**Pedido original (cliente):** "algunas modificaciones al como se ven tus
cambios, la seccion 'Fotos del paquete' debe ir dentro de 'Recibido' ya
que estas fotos son evidencia que se recibio el paquete, adicional
necesito poder visualizar el paquete, poder hacer pinch zoom, poder pasar
de una foto a otra, en general tener una experiencia de usuario fluida
para esta seccion de fotos."

**Vista:** `search/form.html` + `components/_timeline.html` (`/consultar`).

**Status:** verificado

## Qué hacer

1. **Reubicar**: "Fotos del paquete" deja de ser una sección aparte
   después de todo el timeline — pasa a vivir DENTRO de la tarjeta del
   paso "Recibido" (evidencia de que se recibió, no un dato genérico del
   paquete).
2. **Visor con zoom y navegación** (componente nuevo,
   `components/_visor_fotos.html`): clic en una miniatura abre un
   lightbox de pantalla completa con:
   - Botones anterior/siguiente para pasar de una foto a otra (+ flechas
     de teclado).
   - Zoom vía pinch-zoom NATIVO del navegador (el viewport de `base.html`
     ya lo permite, no se bloquea con `touch-action`) — más confiable que
     reimplementar gestos de pinza a mano.
   - Cerrar con X, clic afuera, o Escape.
3. `paso_timeline()` (`components/_timeline.html`) gana soporte de
   `{% call %}` (contenido extra opcional dentro de la tarjeta de un
   paso) para poder inyectar la galería solo en "Recibido".

## Verificación

- [x] Captura confirma "Fotos del paquete" dentro de la tarjeta de
      Recibido, ya no como sección aparte.
- [x] Prueba interactiva con Playwright: clic en miniatura abre el visor
      con fondo oscuro, clic en "siguiente" cambia de foto (contador
      confirmado "2 / 2"), flechas y botón cerrar visibles.
- [x] 229/229 `tests/web/` + 436/436 suite completa.
- [x] Desplegado a `test.papyrus.com.co` (commit final `a842743`).

## Bug encontrado y corregido en el camino

Primer deploy (`0ec1cb5`): el fondo oscuro del lightbox no aparecía —
usaba 3 clases de Tailwind nunca antes usadas en el proyecto
(`bg-black/90`, `cursor-zoom-in`, `focus-visible:ring-white/50`), que por
lo tanto no estaban en el `tailwind.css` compilado (el build es
content-scanned, no CDN). Recompilado + cache-buster `v12` → `v13`
(commit `a842743`) — confirmado con una segunda prueba interactiva que
el fondo ya se ve oscuro correctamente.
