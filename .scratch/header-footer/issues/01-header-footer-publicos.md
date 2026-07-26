# 01 — Header y footer para visitantes públicos

**What to build:** `base.html` (hoy un esqueleto vacío) gana un header y un
footer reales que envuelven `{% block content %}` sin tocar el contenido de
ninguna pantalla existente. Para un visitante SIN ninguna sesión (`persona_id`
ni `usuario_id`), en cualquier pantalla pública (`/anunciar`, `/consultar`):

- Header con logo (SVG inline, colibrí geométrico multicolor tomado del
  legacy) + wordmark "PAQUETEX", enlaces a `/anunciar` y `/consultar`, y
  botones hacia `/otp` (login cliente) y `/ingresar` (login staff).
- El enlace de la pantalla en la que se está queda marcado como activo
  (comparando `request.url.path` contra el `href` de cada enlace —
  `request` ya viaja en el contexto de cada `TemplateResponse` existente).
- Footer = barra de navegación inferior fija SOLO en móvil (breakpoint CSS,
  sin ningún JavaScript de detección de dispositivo), con los mismos enlaces
  públicos.
- Todo en HTML + CSS plano + JS vanilla si hace falta — nada de Tailwind ni
  Alpine.js (ADR-0004: el rebuild es clean-room, aislado del stack legacy).
  Un `<details>/<summary>` nativo es preferible a JS si resuelve un menú
  desplegable.
- El CSS nuevo vive en `base.html` (tokens de marca: color de acento, familia
  tipográfica `system-ui`) — NO se toca ni se centraliza el `<style>` propio
  de cada pantalla existente.
- Este ticket es también el prefactor de 02 y 03: el mecanismo de
  enlace-activo y el breakpoint responsive se construyen aquí una sola vez,
  para que las otras audiencias solo necesiten sumar su propio conjunto de
  enlaces al mismo esqueleto.

**Blocked by:** Ninguno — puede empezar de inmediato.

**Status:** ready-for-agent

- [ ] `base.html` renderiza un `<header>` con logo+wordmark, enlaces a
      `/anunciar` y `/consultar`, y botones a `/otp` y `/ingresar`, visible en
      TODAS las pantallas públicas existentes (heredado vía `{% extends %}`,
      sin copiar HTML en cada plantilla hija).
- [ ] El enlace correspondiente a la pantalla actual lleva una marca visual
      distinta (clase CSS + `aria-current="page"`) y ningún otro enlace la
      lleva.
- [ ] `base.html` renderiza un `<footer>` que en viewport de escritorio no se
      muestra, y en viewport móvil se muestra como barra fija inferior con
      los mismos enlaces públicos.
- [ ] No se usa Tailwind, Alpine.js, ni ninguna dependencia nueva (CDN o
      `static/vendor/`); no hay detección de dispositivo por JavaScript.
- [ ] El `<h1>` y el contenido interno de cada pantalla pública existente
      (`announce/form.html`, `search/form.html`) no cambian.
- [ ] Nuevo `tests/web/test_layout.py`: un visitante sin sesión en
      `/anunciar` y en `/consultar` ve los enlaces públicos y los botones de
      login, marcados como activo/inactivo correctamente; NO ve ningún
      enlace de cliente ni de staff.
- [ ] Suite completa (287 tests existentes) sigue en verde; cualquier
      aserción frágil sobre el contenido total de `r.text` que choque con el
      nuevo header/footer se ajusta puntualmente.
