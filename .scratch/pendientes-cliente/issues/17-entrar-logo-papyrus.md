# 17 — `/entrar`: logo de Papyrus arriba del formulario

**Pedido original (cliente):** "para esta vista https://test.papyrus.com.co/entrar
necesito que también incluyas el logo de papyrus en la parte superior del
formulario como hiciste en /anunciar y /consultar, mismo tamaño, mismo
lugar".

**Vista:** `auth/entrar.html`.

**Status:** verificado

## Qué hacer

Mismo `<img>` de logo (asset local `/static/branding/papyrus-logo.png`,
`max-w-xs`, `max-height:120px;min-height:80px`) que ya usan `announce/form.html`
y `search/form.html`, en la misma posición (arriba del contenido, dentro del
wrapper `max-w-md mx-auto`).

## Qué se hizo

Bloque `<img>` copiado tal cual de `announce/form.html`/`search/form.html`,
insertado antes del `<h1>Iniciar sesión</h1>`.

## Verificación

- [x] Captura confirma el logo en `/entrar`, mismo tamaño/lugar que en
      `/anunciar` y `/consultar`.
- [x] Suite de tests sin regresiones.
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
