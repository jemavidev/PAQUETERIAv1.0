# 30 — Rutas de las vistas legales en español

**Pedido original (cliente):** "pero en las vistas veo que se llaman
'/terms, /privacy y /cookies'".

**Vistas:** `routes/terms.py`, `routes/privacy.py` (+ todos los enlaces
internos que apuntaban a ellas).

**Status:** verificado

## Qué se hizo

El resto del rebuild usa rutas en español (`/anunciar`, `/consultar`,
`/entrar`, `/ayuda`) -- `/terms` y `/privacy` desentonaban (vienen de
producción, que sí usa inglés en las URLs pese a que el contenido es
español). Renombradas:

- `/terms` → `/terminos`
- `/privacy` → `/privacidad`
- `/cookies` se deja igual -- es un préstamo del inglés que el propio
  español usa tal cual (no se tradujo tampoco en el nombre visible,
  "Política de Cookies").

Los archivos/carpetas de plantilla (`terms/form.html`, `privacy/form.html`)
se dejan con su nombre en inglés -- es un detalle interno sin URL propia,
renombrarlos no aporta nada visible y agrega riesgo/alcance no pedido.

Todos los enlaces internos actualizados: checkbox de T&C en `/anunciar`,
las 3 tarjetas legales de `/ayuda`, los enlaces cruzados entre
`/terminos`↔`/privacidad`↔`/cookies`.

## Verificación

- [x] `/terminos`, `/privacidad`, `/cookies` responden 200; `/terms` y
      `/privacy` ahora 404 (confirmado local y en vivo).
- [x] Suite de tests completa sin regresiones (454 passed).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo, incluyendo
      los enlaces cruzados desde `/ayuda` y el checkbox de T&C en
      `/anunciar`.
