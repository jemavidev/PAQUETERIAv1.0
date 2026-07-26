# 02 — Nav de cliente autenticado

**What to build:** para una `Persona` con sesión de cliente activa
(`persona_id` en la sesión, obtenida vía `/otp`), el header construido en 01
muestra, en TODA pantalla donde esa sesión esté presente (`/mis-datos`,
`/anunciar`, `/consultar`):

- Enlaces a `/anunciar`, `/consultar` y `/mis-datos`.
- Un botón "Cerrar sesión" que hace `POST /otp/salir` — mismo patrón ya usado
  en `auth/customer_me.html` (`<form method="post" action="/otp/salir">` con
  un botón submit; la ruta es `POST`-only, no puede ser un link).
- El enlace de la pantalla actual sigue marcado como activo (reutiliza el
  mecanismo de 01).
- Un visitante SIN esta sesión sigue viendo el header público de 01, sin
  cambios.
- `/otp/perfil` no entra en este menú (es una ruta de prueba, no un destino
  real — así lo dice su propio docstring).

**Blocked by:** 01 (reutiliza el esqueleto de `base.html`, el mecanismo de
enlace-activo y el breakpoint responsive ya construidos ahí).

**Status:** ready-for-agent

- [ ] Con `persona_id` en sesión, el header muestra Anunciar/Consultar/Mis
      datos + el form de `POST /otp/salir`, en `/mis-datos` y en cualquier
      otra pantalla que la sesión de cliente alcance.
- [ ] Con esa sesión activa, el header NO muestra ningún enlace de staff
      (Paquetes, Declarar unidad, Residentes, Administración).
- [ ] El footer móvil (barra inferior) también refleja el conjunto de
      enlaces de cliente cuando aplica.
- [ ] `tests/web/test_layout.py`: cliente logueado (usar el helper
      `_login_cliente` ya establecido en otros tests del proyecto) ve sus
      enlaces + el form de logout correcto; un visitante sin sesión en la
      misma pantalla pública sigue viendo solo el header de 01.
- [ ] Suite completa sigue en verde.
