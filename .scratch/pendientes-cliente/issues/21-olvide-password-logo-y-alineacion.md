# 21 — `/staff/olvide-password`: logo + alineación, mismo tratamiento que /entrar

**Pedido original (cliente):** "APLICA EL MISMO ESTO DE LAS OPCIONES
ANTERIORES A https://test.papyrus.com.co/staff/olvide-password recuerda el
logo en la parte superior del formulario".

**Vistas:** `auth/olvide_password.html` + las otras dos pantallas del mismo
flujo (`olvide_password_enviado.html`, `restablecer_password.html`) --
mismo `py-12` sin logo, mismo defecto, mismo fix, para no dejar 2 de 3
pantallas del flujo inconsistentes con la tercera.

**Status:** verificado

## Qué hacer

Igual que ticket 17 (logo) + ticket 20 (alineación `py-8`) pero para el
flujo de recuperación de contraseña completo.

## Qué se hizo

- Logo de Papyrus (mismo `<img>` que `/anunciar`/`/consultar`/`/entrar`)
  agregado arriba del contenido en las 3 pantallas.
- `py-12` → `py-8` en el wrapper de las 3, mismo ajuste que ticket 20.
- `olvide_password.html`/`restablecer_password.html` ya tenían el título
  DENTRO de la tarjeta (usan `formulario_flujo`, a diferencia de
  `/entrar` que tuvo que reestructurarse en el ticket 18) -- sin cambios
  ahí.

## Verificación

- [x] Captura confirma el logo y la alineación en las 3 pantallas.
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo.
