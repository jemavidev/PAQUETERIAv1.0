# 143 — Alinear ancho del contenido con el header en vistas de lista/tabla

**Pedido original (cliente):** "necesito que los contenidos de las diferentes vistas lo hagas
del mismo ancho que el contenido del header" → confirmó extenderlo a "todas las vistas que
aplique" y desplegar a test.papyrus.com.co.

**Status:** implementado (desplegado a test.papyrus.com.co, commit `a8b2a2b`)

## Criterio aplicado

`.site-header-inner` (`base.html`) usa `max-width:1280px` + `padding` responsivo 16px/24px/32px
en los breakpoints 640px/1024px — equivalente exacto a `max-w-7xl` + `px-4 sm:px-6 lg:px-8` de
Tailwind (confirmado contra el CSS compilado).

Se auditaron las 27 vistas del proyecto (`grep` de todo `{% block content %}`) y se distinguió:

- **Vistas de lista/tabla staff** (se widened a `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`,
  alineadas con el header): `/paquetes`, `/residentes`, `/administracion/personal`.
- **El resto se deja con su ancho angosto actual, a propósito** — no es un "olvido", es la
  vista correcta para ese tipo de contenido: formularios de una sola columna (`/entrar`,
  `/anunciar`, OTP, recuperar contraseña), páginas legales/ayuda (`/terminos`, `/privacidad`,
  `/cookies`, `/ayuda`, texto largo se lee peor a 1280px), formularios de configuración
  (`/administracion/conjunto`, `/administracion/notificaciones`), y `/residentes/{id}` (ficha
  de un solo cliente con tabs, no es una lista — sus tarjetas internas ya usan su propio
  `max-w-md`).

## Verificación

- Playwright: bounding box de `.site-header-inner` vs. el div de contenido, comparados en 1280px/1440px/1024px — coinciden exactamente en las 3 vistas.
- Test suite completo (local + del repo de deploy): 1026 passed.
- CI/CD del repo de deploy: `completed success`. Health check 200 en test.papyrus.com.co.
- Pendiente: confirmación del cliente en vivo.
