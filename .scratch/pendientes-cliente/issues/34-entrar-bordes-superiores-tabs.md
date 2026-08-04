# 34 — `/entrar`: redondear los bordes superiores de las pestañas

**Pedido original (cliente):** "que posibilidad existe en que cambies los
bordes superiores de la vista /entrar, específicamente los items 'Soy
residente y Papyrus', esto para que se pueda ver mejor, dime si puedes."

**Status:** verificado

## Diagnóstico

Confirmado visualmente (screenshot de producción de test vía Playwright,
no solo leyendo el código): la pestaña activa ("Soy residente", relleno
azul sólido) tiene sus esquinas superiores a 90° — un bloque duro sentado
justo debajo del título "Iniciar sesión", dentro de una tarjeta que por
lo demás es toda redondeada (`rounded-2xl`). Las pestañas no están pegadas
al borde exterior de la tarjeta (el `<h1>` va primero), así que el
`overflow-hidden` de la tarjeta no las redondea automáticamente.

## Qué se hizo

**Primera vuelta:** `rounded-tl-lg` en "Soy residente" y `rounded-tr-lg`
en "Papyrus" — solo la esquina exterior de cada una, para evitar una
muesca en la costura donde las dos pestañas se tocan sin espacio entre
sí.

**Ampliado (mismo día, a pedido explícito del cliente — "que sean los 2
bordes de cada uno de los tabs"):** cambiado a `rounded-t-lg` en AMBAS
pestañas, redondeando las DOS esquinas superiores de cada una (incluida
la esquina interior, donde se tocan) — el cliente vio el resultado de la
primera vuelta y pidió expresamente las dos esquinas, no solo la de
afuera.

Clases nuevas no estaban en el Tailwind ya compilado — recompilado en
ambas vueltas (`npx tailwindcss@3.4 --content
'src/app/web/templates/**/*.html' --minify -i src/static/css/input.css -o
src/app/web/static/css/tailwind.css`) y subido el cache-bust cada vez
(`tailwind.css?v=23` → `?v=24` en `base.html`).

## Verificación

- [x] Primera vuelta confirmada visualmente en vivo (solo esquina
      exterior).
- [x] Ampliación (las 2 esquinas por pestaña) confirmada visualmente en
      vivo tras el deploy (`tailwind.css?v=24`).
