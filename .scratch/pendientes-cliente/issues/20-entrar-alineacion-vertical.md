# 20 — `/entrar`: posiciones no coinciden con /anunciar y /consultar

**Pedido original (cliente):** "para la vista /entrar no están en el mismo
lugar los logos o formularios, esto de igual forma que en /consultar o
/anunciar, puedes ajustarlo para que al cambiar entre uno y otro esto se vea
similar con relación a las posiciones y lugares de sus items".

**Vista:** `auth/entrar.html`.

**Status:** verificado

## Qué hacer

Diagnosticar y corregir el desfase de posición entre `/entrar` y las otras
dos vistas públicas.

## Qué se hizo

Medido con Playwright (`getBoundingClientRect`) contra `/anunciar` y
`/consultar`: el logo, la tarjeta y el ancho coincidían EXACTO salvo un
desfase vertical constante de 16px (logo en `top:109` vs `top:93`) --
causado por el wrapper externo de `/entrar` usando `py-12` (48px) en vez de
`py-8` (32px), que sí usan las otras dos. Cambiado a `py-8` -- ya existía en
el bundle de Tailwind (usado por las otras vistas), sin recompilar.

## Verificación

- [x] Captura confirma logo/tarjeta en la misma posición Y que /anunciar y
      /consultar -- medido con Playwright, coinciden exacto (logo
      `top:93 left:35`, tarjeta `top:218.5 left:16 width:358` en las tres
      vistas).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
