# 262 — `GET /otp`: si ya hay sesión de cliente activa, redirige a /mis-datos en vez de mostrar el login

**Pedido original (cliente):** "en caso de ya estar logueado con otp,
por favor no me redirijas a esta vista /otp."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

`customer_auth.py::customer_login_form` (`GET /otp`) hoy renderiza el
formulario de login SIEMPRE, sin importar si la sesión de cliente
(`CUSTOMER_SESSION_KEY`) ya es válida -- a diferencia de `/otp/verificar`
tras un login exitoso, que redirige a `/mis-datos`.

Cambio: si `request.session` ya trae un `CUSTOMER_SESSION_KEY` que
resuelve a una Persona real (misma validación que `current_customer`,
sin lanzar 401 -- solo chequear), `GET /otp` redirige directo a
`/mis-datos` en vez de mostrar el formulario de login de nuevo.

## Verificación

Test nuevo `test_get_customer_login_con_sesion_activa_redirige_a_mis_datos`
(`test_customer_auth.py`): login real por OTP, luego `GET /otp` con esa
sesión -> 303 a `/mis-datos`. Suite completa (`tests/web` +
`tests/data_model`): 1245 passed.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
