# 18 — `/entrar`: "Iniciar sesión" dentro de la tarjeta, como en /anunciar y /consultar

**Pedido original (cliente):** "puedes incluir 'Iniciar sesión' en algún
lugar del formulario como se hace en las otras 2 vistas /anunciar y
/consultar".

**Vista:** `auth/entrar.html`.

**Status:** verificado

## Qué hacer

En `/anunciar` y `/consultar` el título vive DENTRO de la tarjeta blanca
(primera línea, `text-lg font-bold`, vía el parámetro `titulo` de
`formulario_flujo`). En `/entrar` el título "Iniciar sesión" era un `<h1>`
aparte, ARRIBA de la tarjeta de pestañas -- moverlo adentro, mismo
tratamiento visual.

## Qué se hizo

`/entrar` no usa `formulario_flujo` (estructura propia de pestañas), así que
el `<h1>` se movió a ser el primer hijo de la tarjeta (`bg-white ... flex
flex-wrap`), con `w-full` (ocupa su propia línea dentro del flex-wrap) y
`text-lg font-bold text-slate-900 px-6 pt-6 pb-3` -- mismo tamaño de fuente
que el `<h3>` de `formulario_flujo`. Requirió recompilar `tailwind.css`
(`pt-6`/`pb-3` no estaban en el bundle) -- verificado con un render aislado
antes de tocar el sitio en vivo, aprendiendo del error del ticket 13.

## Verificación

- [x] Captura confirma el título dentro de la tarjeta.
- [x] Suite de tests sin regresiones.
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo (ambas
      pestañas, cliente y staff).
