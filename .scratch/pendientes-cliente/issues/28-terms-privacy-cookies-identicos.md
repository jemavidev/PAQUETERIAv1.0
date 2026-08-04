# 28 — `/terms`, `/privacy`, `/cookies`: réplica IDÉNTICA de producción

**Pedido original (cliente):** "quiero que hagas lo mismo con Términos y
condiciones, Políticas de privacidad y políticas de cookies" (mismo
tratamiento "IDÉNTICO" del ticket 27, aplicado a las otras 3 páginas
legales).

**Vistas:** `terms/form.html`, `privacy/form.html`, `cookies/form.html` --
reescritura completa.

**Status:** verificado

## Qué se hizo

Mismo método que ticket 27: HTML completo de
`paquetex.papyrus.com.co/terms`, `/privacy` y `/cookies` extraído vía
Playwright, contenido copiado literal (secciones, emoji, colores,
estructura de tarjetas con `border-l-4` por color).

Dos ajustes deliberados en las 3 páginas:
- Se omite la sección "Descargar PDF" de cada una -- el archivo (ej.
  `TERMINOS_Y_CONDICIONES.pdf`) no existe en este entorno; un enlace de
  descarga roto sería peor que no tenerlo.
- "Volver al Centro de Ayuda" apunta a `/ayuda` (nuestra ruta real, no
  `/help`). Los enlaces cruzados entre las 3 páginas (Privacidad ↔
  Términos ↔ Cookies) ya apuntaban a rutas que SÍ tenemos
  (`/terms`/`/privacy`), sin cambios ahí.

## Verificación

- [x] Suite de tests completa sin regresiones (454 passed).
- [x] Capturas confirman paridad visual contra producción en las 3
      páginas.
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
