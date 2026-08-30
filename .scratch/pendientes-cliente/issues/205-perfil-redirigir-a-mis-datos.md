# 205 — `/otp/perfil`: redirigir a `/mis-datos`

**Pedido original (cliente):** "Ver datos básicos de la persona: Funciona,
debería ser redirigido a /mis-datos, aquí se podrán cambiar los datos del
cliente"

**Status:** implementado

## Implementación

`customer_auth.py::customer_me` (`GET /otp/perfil`) ahora redirige (303) a
`/mis-datos` en vez de renderizar `auth/customer_me.html` -- esa plantilla
queda intacta, sin caller (era "ruta protegida de prueba" según su propio
docstring; nada más la enlazaba).

