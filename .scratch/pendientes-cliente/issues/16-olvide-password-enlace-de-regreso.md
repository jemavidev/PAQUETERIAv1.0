# 16 — `/staff/olvide-password`: sin forma de regresar tras enviar el enlace

**Pedido original (cliente, retroalimentación en vivo sobre ticket 15):**
"necesito una forma de regresar desde esta vista
https://test.papyrus.com.co/staff/olvide-password ya que solo aparece el
texto 'Revisa tu correo...'".

**Vista:** `auth/olvide_password_enviado.html`.

**Status:** verificado

## Qué hacer

Agregar un enlace de regreso ("Volver a iniciar sesión" → `/ingresar`) en la
pantalla de confirmación "Revisa tu correo" -- hoy es un callejón sin salida
(sin navegación propia, solo el botón atrás del navegador).

## Qué se hizo

Mismo patrón visual que el enlace "¿Olvidaste tu contraseña?" ya agregado en
`login.html`/`entrar.html` (ticket 15): `<a>` centrado, `text-blue-800
hover:underline`, debajo de la tarjeta.

Nota aparte, aclarada al cliente: el correo de prueba llegó a
`jesus@jemavi.co` en vez de a `jveyes@gmail.com` porque así es COMO SE DISEÑÓ
`EMAIL_OVERRIDE_ADDRESS` en el ticket 15 (fail-closed de staging, todo correo
se redirige ahí sin importar la cuenta) -- no es un bug. Se confirmó en la
BD que la contraseña de `jveyes@gmail.com` sí cambió a la nueva
("Seaboard12", verificado con `verify_credentials`).

## Verificación

- [x] Captura confirma el enlace visible en la pantalla de confirmación.
- [x] Suite de tests sin regresiones.
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo (clic real
      lleva a `/ingresar`).
