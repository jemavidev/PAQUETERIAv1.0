# 45 — `tailwind.config.js` nunca escaneaba `src/app/web/templates/` (todo el rebuild)

**Origen:** el cliente pidió recompilar Tailwind para que los cambios de `/mis-paquetes` (issue 43)
se vieran reflejados. Al investigar por qué hacía falta, apareció un problema mucho más grande que
el de esa única página.

**Status:** implementado

## Hallazgo

`tailwind.config.js` → `content` solo escaneaba:

```js
content: [
  "./src/templates/**/*.html",   // legacy
  "./src/static/js/**/*.js",
],
```

**`./src/app/web/templates/**` (TODO el rebuild, PaqueteXv.2) nunca estuvo en la lista.** Como
`tailwind.css` se compila una vez y se COMMITEA al repo (no se recompila en el Dockerfile/deploy —
confirmado: commit `b52bc6d "Agregar Tailwind CSS compilado (80KB) para deployment inmediato"`),
esto significa que **cualquier clase de Tailwind usada exclusivamente en una plantilla del rebuild,
y no también en alguna plantilla legacy, nunca llegó a producción** — no es un problema de esta
sesión puntual, es estructural desde que el rebuild empezó a divergir visualmente del legacy (los
16 componentes del Design System, `docs/design-system/`, TODOS corren este riesgo).

## Verificación

Antes del fix, clases usadas en `customer/paquetes.html` (recién editado) estaban ausentes del CSS
compilado: `text-amber-600`, `text-emerald-600`, `shrink-0` no existían en `tailwind.css`, mientras
que `text-blue-800`/`text-red-600` sí aparecían por pura coincidencia (también las usa alguna
plantilla legacy).

## Fix

`tailwind.config.js`:

```js
content: [
  "./src/templates/**/*.html",
  "./src/app/web/templates/**/*.html",  // <- agregado
  "./src/static/js/**/*.js",
],
```

`npm install && npm run build:css` → `tailwind.css` pasó de 85 504 a 100 218 bytes (+17%) — el
volumen de clases que aparecieron confirma que esto venía faltando de forma sustancial, no marginal.

## Desplegado

Además del fix en el repo de desarrollo (MATT/CODE), se copió `tailwind.css` recompilado (100 218
bytes) al repo de despliegue (`jemavidev/PaqueteX`, commit `75f79bc`) y se confirmó en vivo contra
`https://test.papyrus.com.co/static/css/tailwind.css` — mismo tamaño, `shrink-0` presente (antes
ausente). El fix de `tailwind.config.js`/`package.json` en sí (los dos scripts `build:css:*`) vive
solo en MATT/CODE, ya que el repo de despliegue no incluye el toolchain de Tailwind, solo el CSS ya
compilado.

## Hallazgo aparte durante el despliegue — CI en rojo en `main` desde antes

Al verificar antes de pushear, encontré que **CI ya estaba fallando en `main`** desde 2 commits
atrás (`4b5694c` y el anterior), 15 tests de auth/customer_auth/layout — nada relacionado con este
fix ni con issue 43 (confirmado corriendo la suite contra un clone limpio de `origin/main` sin
tocar nada). "Deploy to Staging" sigue en verde porque ese workflow no depende de que CI pase (solo
hace `py_compile` de 2 archivos puntuales) — o sea, los deploys a producción han seguido pasando
sin que nadie note que la suite de tests está rota. Vale la pena revisar esto aparte; no lo
diagnostiqué a fondo (está fuera del alcance de este issue).

## Pendiente / recomendación

No se auditó plantilla por plantilla cuál de los 16 componentes del Design System tenía algún
elemento visualmente roto en producción por esta causa antes del fix — el fix es correcto hacia
adelante (próximo build+deploy va a incluir todo), pero si algo se veía raro en `test.papyrus.com.co`
antes de hoy y se atribuyó a otra causa, esta es la explicación real más probable. Vale la pena que
el cliente revise visualmente el sitio completo después del próximo deploy con este fix.

## Comments
