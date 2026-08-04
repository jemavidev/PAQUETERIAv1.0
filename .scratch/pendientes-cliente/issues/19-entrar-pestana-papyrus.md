# 19 — `/entrar`: pestaña "Soy del staff" → "Papyrus"

**Pedido original (cliente):** "Remplaza la palabra 'Soy del staff' por
'Papyrus'".

**Vista:** `auth/entrar.html`.

**Status:** verificado

## Qué hacer

Cambiar el texto de la pestaña de staff de "Soy del staff" a "Papyrus".
Cambio de copy puro, sin tocar clases/estructura.

## Qué se hizo

`Edit` de una sola línea en el `<label for="tab-staff">`. Sin clases nuevas
(no requiere recompilar tailwind.css); sin tests que dependan del texto
literal (`grep` confirmado vacío).

## Verificación

- [x] Captura confirma el texto "Papyrus" en la pestaña.
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
