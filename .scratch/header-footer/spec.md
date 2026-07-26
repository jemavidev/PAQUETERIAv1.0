Status: ready-for-agent

# Header y footer transversales (Grupo 9 — REQUERIMIENTOS.md)

## Problem Statement

Hoy `base.html` (la plantilla compartida de la capa web del rebuild, PaqueteXv.2) no
tiene ni header ni footer: es un esqueleto vacío (`<title>` + `{% block content %}`).
Cada pantalla (`/anunciar`, `/consultar`, `/otp`, `/mis-datos`, `/paquetes`,
`/announce`, `/residentes`, `/administracion/personal`,
`/administracion/notificaciones`, `/mi-sesion`) es una isla: tiene su propio
`<h1>` y, cuando aplica, su propio botón suelto de "Cerrar sesión", pero no hay
manera de navegar entre pantallas sin escribir la URL a mano. Un cliente que
anuncia un paquete no tiene forma de llegar a "Consultar" ni a "Mis datos"; un
miembro del staff que recibe un paquete no tiene forma de llegar a "Residentes"
sin teclear la URL. Tampoco hay identidad de marca visible (logo, nombre de la
app) en ninguna pantalla del rebuild.

Esto quedó deliberadamente para el final del roadmap (Grupo 9): el usuario pidió
verificar primero que cada pantalla funcionara por separado, y ajustar el
header/footer "viendo" el resultado. La nota original decía "como te lo pedí
anteriormente" sin especificación registrada; investigación confirmó que la app
en producción (legacy) sí distingue navegación pública vs autenticada
(`public-navbar.html` / `authenticated-navbar.html` + un footer sticky para
móvil), con un logo de colibrí geométrico multicolor y el wordmark "PAQUETEX".
El usuario confirmó: tomar ese look and feel como base, ajustando detalles
visuales después de verlo corriendo.

## Solution

Un header y un footer compartidos, montados una sola vez en `base.html`, que
envuelven el `{% block content %}` de cada pantalla existente sin tocar su
contenido interno. Tres variantes de navegación según quién mira la página —
público (nadie ha iniciado sesión), cliente (sesión de `Persona` vía `/otp`), y
staff (sesión de `Usuario` vía `/ingresar`, con un matiz para rol `ADMIN`) —
resueltas todas desde la sesión ya existente, sin nuevas tablas ni nuevos
conceptos de dominio. Visualmente: el mismo logo de colibrí y wordmark
"PAQUETEX" del legacy, reimplementados con el CSS plano/JS vanilla que ya usa
el rebuild (nada de Tailwind ni Alpine.js — ver Implementation Decisions).

Esta es la última pieza visual del roadmap de ajustes; el propio usuario ya
avisó que corregirá detalles de estilo una vez lo vea corriendo en staging, así
que la implementación debe ser sobria y fácil de retocar, no una pulida final.

## User Stories

**Identidad de marca (todas las audiencias)**

1. Como visitante de cualquier pantalla, quiero ver el logo y el nombre
   "PAQUETEX" en la parte superior, para saber en qué aplicación estoy.
2. Como cualquier usuario, quiero que el logo/wordmark enlace a un destino
   sensato según quién soy (público → `/anunciar`; cliente → `/mis-datos`;
   staff → `/paquetes`), para tener un "home" al que volver con un clic.

**Visitante público (sin ninguna sesión)**

3. Como visitante sin sesión, quiero ver enlaces a "Anunciar" (`/anunciar`) y
   "Consultar" (`/consultar`) en el header, para llegar a las dos únicas
   acciones públicas sin saber la URL de memoria.
4. Como visitante sin sesión, quiero ver un enlace para "Iniciar sesión"
   (`/otp`, login de cliente) y otro para el staff (`/ingresar`), para poder
   autenticarme según quién soy.
5. Como visitante en un teléfono, quiero una barra inferior fija con los
   accesos principales (Anunciar, Consultar), para no tener que estirar el
   pulgar hasta arriba de la pantalla.

**Cliente autenticado (sesión de `Persona` vía `/otp`)**

6. Como cliente con sesión, quiero ver "Anunciar", "Consultar" y "Mis datos"
   (`/mis-datos`) en el header, para moverme entre las tres sin recordar URLs.
7. Como cliente con sesión, quiero un botón de "Cerrar sesión" visible en toda
   pantalla (no solo en `/mis-datos`), para salir desde cualquier lugar.
8. Como cliente con sesión, NO quiero ver los enlaces de staff
   (`/paquetes`, `/residentes`, `/administracion/*`), porque no me
   corresponden y no debo ni enterarme de que existen.
9. Como cliente que también es staff en el mismo navegador (sesiones
   coexistentes, ver `security.py`), quiero ver AMBOS conjuntos de enlaces
   (cliente y staff) sin que uno pise al otro, porque las dos sesiones son
   independientes y ambas siguen activas.

**Staff — rol `OPERADOR` (sesión de `Usuario` vía `/ingresar`)**

10. Como staff con sesión, quiero ver "Paquetes" (`/paquetes`), "Declarar
    unidad" (`/announce`), "Residentes" (`/residentes`) y "Consultar"
    (`/consultar`) en el header, para llegar a mi trabajo diario sin URLs de
    memoria.
11. Como staff con sesión, quiero ver mi nombre (o al menos que quede claro que
    tengo una sesión de staff activa) y un botón de "Cerrar sesión"
    (`POST /salir`) en toda pantalla.
12. Como staff con rol `OPERADOR`, NO quiero ver los enlaces de
    "Administración" (`/administracion/personal`,
    `/administracion/notificaciones`), porque mi rol no tiene acceso a esas
    pantallas (hoy devuelven 403 vía `require_admin`) y no deben aparecer como
    si lo tuviera.

**Staff — rol `ADMIN`**

13. Como staff con rol `ADMIN`, quiero ver además "Personal"
    (`/administracion/personal`) y "Notificaciones"
    (`/administracion/notificaciones`) en el header, porque sí tengo acceso a
    esas pantallas.

**Navegación y estado activo**

14. Como cualquier usuario, quiero que el enlace de la pantalla en la que
    estoy se vea visualmente distinto (resaltado) del resto, para orientarme
    dentro de la navegación.
15. Como cualquier usuario, quiero que el header/footer se vea igual (mismos
    enlaces, mismo estado activo) en TODAS las pantallas existentes de mi
    audiencia, para que la navegación sea predecible.
16. Como desarrollador que agrega una pantalla nueva en el futuro, quiero que
    extender `base.html` sea suficiente para heredar el header/footer
    correcto, sin tener que copiar/pegar HTML de navegación en cada plantilla.

**No regresión**

17. Como usuario de cualquier pantalla ya construida (`packages/list.html`,
    `search/form.html`, `announce/form.html`, `announce_new/form.html`,
    `customers_manage/detail.html`, `admin/*.html`, `auth/*.html`), quiero que
    el contenido y el comportamiento (modales, checkbox, escáner ZXing,
    filtros, paginación) sigan funcionando exactamente igual después de que se
    les añada el header/footer alrededor.
18. Como desarrollador, quiero que ningún test de los 287 ya existentes se
    rompa por la introducción del header/footer (los tests actuales no
    afirman que el `<body>` esté vacío de más contenido, pero si alguno
    depende de un conteo exacto de elementos o de que cierto texto sea el
    único texto de la página, debe seguir pasando o ajustarse).

## Implementation Decisions

- **`base.html` deja de ser un esqueleto vacío.** Gana un `<header>` y un
  `<footer>` reales alrededor de `{% block content %}`, más un bloque
  `{% block head %}` que las plantillas hijas siguen usando para su CSS
  específico de pantalla (esto NO cambia — cada plantilla sigue trayendo su
  propio `<style>`, como hoy). `base.html` gana únicamente el CSS mínimo del
  propio header/footer (variables de marca: color de acento, familia
  tipográfica `system-ui` ya usada por todas las pantallas) — no se
  refactoriza ni se centraliza el CSS de las pantallas existentes; eso es un
  cambio distinto y no es parte de este ticket.

- **Sin Tailwind, sin Alpine.js.** El legacy (`public-navbar.html`,
  `authenticated-navbar.html`, `mobile-footer*.html`) usa Tailwind + Alpine
  (`x-data`, `@click`) vía CDN. El rebuild completo (`ADR-0004`, strangler fig)
  es CSS plano por pantalla + JS vanilla (así están hechos el escáner ZXing,
  los modales y el checkbox de notificaciones). El header/footer nuevo sigue
  ESA convención: HTML + CSS plano en `base.html`, y un `<script>` vanilla
  mínimo solo si hace falta (p. ej. un `<details>`/`<summary>` nativo de HTML
  puede resolver un menú desplegable sin JS en absoluto; se prefiere esa
  opción sobre escribir JS si el resultado visual es aceptable). No se agrega
  ninguna dependencia nueva ni de CDN ni a `static/vendor/`.

- **Logo: SVG inline, tomado del legacy.** El colibrí geométrico multicolor de
  `public-navbar.html` (el de facetas de color, no el de gradiente de
  `authenticated-navbar.html`) se reutiliza tal cual como marca única de la
  app — no hace falta una versión distinta por audiencia. Wordmark "PAQUETEX"
  al lado, mismo estilo tipográfico (negrita, tracking amplio) que el legacy.

- **Tres variantes de navegación, resueltas por audiencia y rol:**
  - Pública (ninguna sesión): enlaces a `/anunciar`, `/consultar`; botones a
    `/otp` (cliente) e `/ingresar` (staff).
  - Cliente (`persona_id` en sesión): enlaces a `/anunciar`, `/consultar`,
    `/mis-datos`; botón de salida `POST /otp/salir` (mismo patrón ya usado en
    `auth/customer_me.html`: un `<form method="post" action="/otp/salir">`
    con un botón submit — no un link, porque la ruta es `POST`-only).
  - Staff (`usuario_id` en sesión): enlaces a `/paquetes`, `/announce`,
    `/residentes`, `/consultar`; si el rol es `ADMIN`, además
    `/administracion/personal` y `/administracion/notificaciones`; botón de
    salida `POST /salir` (mismo patrón que `auth/me.html`).
  - Ambas sesiones pueden coexistir (`security.py` ya lo permite
    explícitamente): si están presentes `persona_id` Y `usuario_id` a la vez,
    el header muestra los dos conjuntos de enlaces sin que ninguno oculte al
    otro (dos bloques de navegación, uno por audiencia).
  - `/otp/perfil` NO entra en ningún menú: su propio docstring lo marca como
    "ruta protegida de prueba", no un destino real para el usuario final.

- **El rol necesita estar disponible sin tocar cada ruta.** Hoy la sesión de
  staff solo guarda `usuario_id` (`SESSION_KEY`); resolver el rol para decidir
  si mostrar "Administración" requeriría, si no se hace nada más, una consulta
  a `Usuario` en cada request de cada ruta que renderiza una página completa —
  eso es cirugía a través de ~10 archivos de rutas solo para pintar un menú.
  En vez de eso: `routes/auth.py` (`login_submit`) guarda también el rol en la
  sesión firmada (`request.session["rol"] = usuario.rol.value`) en el momento
  del login, junto a `usuario_id`. `base.html` lee `request.session.get("rol")`
  directamente (Jinja puede leer `request.session` porque `request` ya viaja
  en el contexto de cada `TemplateResponse` existente) sin necesitar una nueva
  dependencia de FastAPI ni tocar el resto de las rutas. Es un dato derivado
  (no fuente de verdad — la fuente de verdad sigue siendo `Usuario.rol` en la
  BD, vía `require_admin`, que sigue siendo la puerta REAL de cada ruta
  administrativa); si el rol de alguien cambia, se refleja en su próximo
  login, exactamente como ya pasa con `usuario_id` mismo si un `Usuario` se
  borra a mitad de sesión (`current_staff` ya maneja ese caso con un 401).

- **Estado activo del enlace actual:** comparar `request.url.path` (disponible
  en todo `TemplateResponse` porque `request` ya viaja en el contexto) contra
  el `href` de cada enlace del menú, con una clase CSS distinta
  (`aria-current="page"` + una clase visual) para el que coincide. Mismo
  mecanismo simple que ya usaba el legacy (`{% if request.path == '/x' %}`),
  adaptado a `request.url.path` que es lo que expone Starlette.

- **Footer = barra de navegación inferior fija en móvil, no un footer de
  copyright.** El legacy llama "footer" a una barra sticky inferior con los
  accesos principales, pensada para pulgar en móvil — se mantiene ese
  concepto, pero SIN la detección de dispositivo por JavaScript del legacy
  (user-agent sniffing, `matchMedia` combinando 6 criterios con un sistema de
  puntaje, recarga de página en `orientationchange`): es una complejidad que
  no aporta nada sobre un simple *breakpoint* CSS (`@media (max-width: ...)`),
  que es exactamente el patrón responsive que el rebuild ya usa en sus
  propias pantallas (`packages/list.html` ya es mobile-first con
  `max-width: 560px`). La barra inferior en móvil replica un subconjunto de
  los mismos enlaces del header (los 2-3 más frecuentes por audiencia); en
  escritorio no se muestra (el header de arriba ya cubre la navegación).

- **Contenido de cada pantalla no cambia.** Ninguna plantilla hija pierde su
  `<h1>` propio ni su lógica interna; el header/footer se agrega alrededor,
  en `base.html`, así que el cambio en cada plantilla hija es cero (todas ya
  usan `{% extends "base.html" %}` y `{% block content %}`).

## Testing Decisions

- Un test solo debe verificar comportamiento observable por HTTP (presencia o
  ausencia de un `href` / texto en `r.text`, o de un botón que apunte a la
  ruta de logout correcta) — no implementación interna del template.
- Seam único: `tests/web/` con `TestClient`, exactamente el patrón ya usado en
  todo el proyecto (`tests/web/test_customer_auth.py`,
  `tests/web/test_customer_verify.py`, etc.), incluyendo el helper
  `_login_cliente` (login de cliente) y el patrón de login de staff via
  `client.post("/ingresar", data={...})` ya usado en varios tests existentes
  (p. ej. `test_customer_verify.py::test_desactivar_detiene_una_notificacion_posterior`).
- Nuevo archivo `tests/web/test_layout.py` cubre:
  - Visitante público en `/anunciar` o `/consultar`: aparecen los enlaces
    públicos y los botones de login; NO aparece ningún enlace de staff ni de
    cliente autenticado.
  - Cliente logueado (rol OPERADOR/ADMIN no aplica): en `/mis-datos` aparecen
    sus enlaces + el form de `POST /otp/salir`; NO aparecen enlaces de staff.
  - Staff `OPERADOR` logueado: en `/paquetes` aparecen sus enlaces + el form
    de `POST /salir`; NO aparecen `/administracion/personal` ni
    `/administracion/notificaciones`.
  - Staff `ADMIN` logueado: sí aparecen los dos enlaces de administración.
  - Ambas sesiones activas a la vez (cliente Y staff en el mismo
    `TestClient`): aparecen ambos conjuntos de enlaces.
  - El enlace de la página actual lleva la marca de "activo" (clase o
    `aria-current`) y los demás no.
  - Regresión: correr la suite completa (287 tests) sin romper ninguno; si
    algún test existente hace una aserción frágil sobre el contenido total de
    `r.text` (por ejemplo, contar apariciones de una palabra que ahora también
    sale en el header), ajustar esa aserción puntual, no debilitar el test
    nuevo.
- Prior art de fixtures y aislamiento: `tests/web/conftest.py` (fixture
  `client`, truncado de tablas entre tests) — no requiere cambios para este
  ticket, ya que no se agrega ninguna tabla nueva.

## Out of Scope

- "Mensajes" (`/messages`) y los badges de contadores en vivo
  (`packages-badge-footer`, `messages-badge-footer`, polling) del legacy: el
  rebuild no tiene concepto de dominio de "Mensaje" ni de notificaciones
  internas — no hay nada que enlazar todavía.
- El enlace de WhatsApp de soporte del legacy footer: no hay decisión tomada
  sobre canal de soporte para el rebuild; se deja fuera hasta que se pida
  explícitamente.
- Cualquier auditoría de accesibilidad más allá de landmarks semánticos
  básicos (`<header>`, `<nav>`, `<footer>`) y `aria-current` en el enlace
  activo — una revisión WCAG completa no fue pedida.
- Rediseño o consolidación del CSS de las pantallas existentes (cada una sigue
  con su propio `<style>` embebido); este ticket solo añade el CSS del
  header/footer mismo.
- Cambiar cualquier ruta, permiso (`current_staff`/`require_admin`/
  `current_customer`) o regla de negocio existente — este ticket es
  exclusivamente de navegación/UI.
- Ajustes finos de estilo (colores exactos, espaciados, tipografía) más allá
  de replicar el look and feel general del legacy: el usuario ya avisó que
  corregirá detalles visuales una vez lo vea corriendo — no es necesario
  buscar la pulida final en esta pasada.

## Further Notes

Este es el último punto pendiente del roadmap de 9 grupos (los otros 8 ya
están implementados y con 287/287 tests pasando). El usuario pidió
explícitamente dejarlo para el final "una vez otras pantallas estén
visualmente corriendo" — ya lo están. Después de implementar, lo correcto es
desplegar a staging y mostrárselo para que dé su feedback visual concreto
(colores, espaciado, qué tan literal debe ser el logo respecto al legacy),
en vez de iterar a ciegas sobre el aspecto exacto.
