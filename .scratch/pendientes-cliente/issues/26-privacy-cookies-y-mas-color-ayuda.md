# 26 — `/privacy` y `/cookies` nuevas + más color en `/ayuda` + 2 bugs de íconos reales

**Pedido original (cliente):** "crea estas 2 vistas /privacy y /cookies,
llénala con el contenido de lo que existe en paquetex.papyrus.com.co, más
adelante actualizaremos el contenido, por ahora solo créalo con el look and
feel similar. Corrige la vista de /ayuda para que tenga un mejor look and
feel colorido similar al que está en el sitio de producción." + 2 reportes
de íconos que llevaron a encontrar bugs reales (no eran pedidos de color
nuevos, eran defectos):

1. "No actualizaste el ícono de Anunciar del footer... colores no sean
   oscuros" -> el ícono de Anunciar es SOLID (un solo path relleno,
   círculo+cruz), así que en su estado activo (azul de marca `--site-brand`,
   `#1e40af`) se ve como un círculo pesado/oscuro -- a diferencia de los
   íconos outline (trazo fino) que con el mismo azul se ven livianos.
   Confirmado con el cliente: mismo diseño sólido, pero azul más claro
   solo en el ícono (no en el texto de abajo).
2. "El ícono de whatsapp... debería verse igual al de producción, es más
   redondo" -> el path es IDÉNTICO al de producción (diff carácter por
   carácter, confirmado), pero estaba diseñado para un lienzo `viewBox="0
   0 24 24"` y el macro `enlace_nav_footer` lo renderizaba en `20 20`
   (tamaño por defecto de los íconos solid) -- el borde circular exterior
   del logo de WhatsApp quedaba recortado, dejando solo el teléfono
   visible. Bug real de viewBox, no de color.

**Vistas:** `privacy/form.html` + `cookies/form.html` (nuevas) +
`ayuda/form.html` (más color) + `base.html` (fix de íconos del footer).

**Status:** verificado

## Qué se hizo

- **`/privacy`** y **`/cookies`** nuevas (`routes/privacy.py`,
  `routes/cookies.py`), mismo patrón que `/terms` (única tarjeta blanca,
  secciones numeradas) -- contenido traído de
  `paquetex.papyrus.com.co/privacy` y `/cookies` vía fetch directo (no
  inventado), adaptado a la operadora real (Papyrus Soluciones Integrales
  S.A.S.), sin emoji (consistente con `/terms`). Marcador de posición
  razonable, no revisión legal -- mismo disclaimer que `/terms`.
- **`/ayuda`**: gradientes en vez de color plano en el ícono hero, la
  tarjeta intro, los 3 pilares (antes blancos, ahora con fondo a tono con
  su ícono), las 3 tarjetas de acción y la tarjeta de contacto. Fila de 3
  tarjetas legales (Términos + las 2 nuevas).
- **Fix real 1** (`base.html`): nueva regla CSS
  `.site-footer-mobile nav a[href$="/anunciar"][aria-current="page"] svg`
  (+ `/announce` para el nav de staff) que aclara SOLO el ícono a
  `#60a5fa` en su estado activo, sin tocar el texto. Se usó `$=` (termina
  con) en vez de `=` a propósito -- un test (`test_layout.py`) verifica
  que la palabra `href="/announce"` (ruta staff) nunca aparece para un
  visitante público, y mi primer intento con `=` exacto colisionaba con
  esa cadena literal dentro del CSS del `<head>` (falso positivo, no un
  problema real de seguridad -- corregido).
- **Fix real 2** (`base.html`): `enlace_nav_footer` ahora acepta un
  parámetro `viewbox` explícito; las 2 llamadas al ícono de WhatsApp
  pasan `viewbox=24` -- el círculo completo del logo ya no se recorta.
- Recompilado `tailwind.css` + bump de cache-busting a `v=19`. Suite
  completa corrida antes de desplegar. Sin tests dedicados para
  `/privacy`/`/cookies` (mismo criterio que `/terms`, que tampoco los
  tiene).

## Verificación

- [x] Capturas confirman `/privacy`, `/cookies`, `/ayuda` con más color,
      ícono de WhatsApp redondo completo, ícono de Anunciar más claro en
      su estado activo.
- [x] Suite de tests completa sin regresiones (453 passed + 1 flaky
      conocido, confirmado pasando al reintentar solo).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
