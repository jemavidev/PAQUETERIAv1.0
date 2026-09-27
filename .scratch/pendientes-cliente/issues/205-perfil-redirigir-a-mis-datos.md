# 205 — `/otp/perfil`: redirigir a `/mis-datos`

**Pedido original (cliente):** "Ver datos básicos de la persona: Funciona,
debería ser redirigido a /mis-datos, aquí se podrán cambiar los datos del
cliente"

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

`customer_auth.py::customer_me` (`GET /otp/perfil`) ahora redirige (303) a
`/mis-datos` en vez de renderizar `auth/customer_me.html` -- esa plantilla
queda intacta, sin caller (era "ruta protegida de prueba" según su propio
docstring; nada más la enlazaba).

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
