# 15 — Recuperar contraseña de staff (correo)

**Pedido original (cliente, sesión de `/grilling` sobre `/entrar`):** no
existe opción para recuperar la contraseña de staff.

**Vistas nuevas:** pantallas de "olvidé mi contraseña" y "restablecer
contraseña", enlazadas desde `auth/login.html`.

**Status:** verificado

## Decisiones acordadas en grilling

- Enlace por correo con token seguro (no un código corto como OTP — un
  link es más cómodo por correo), válido 30 minutos, un solo uso.
- Mensaje genérico igual si el correo existe o no (mismo principio que
  la restricción de OTP).
- Cuenta SMTP dedicada de staging (`paquetex@papyrus.com.co`, MXroute) —
  separada de cualquier SMTP de producción, ya probada end-to-end
  (correo de prueba confirmado recibido).
- Protección fail-closed igual que SMS: `EMAIL_OVERRIDE_ADDRESS` (por
  defecto `jesus@jemavi.co`) — mientras exista, TODO correo de staging se
  redirige ahí, nunca al correo real de un staff de prueba.

## Qué se hizo

- Modelo `PasswordReset` (migración `0016_password_resets`): token de un
  solo uso, 30 minutos, hasheado con **SHA-256** (no bcrypt -- el token
  es de alta entropía y se busca por igualdad desde la URL, bcrypt
  salado no permite esa búsqueda directa; ver docstring de
  `app/domain/password_reset.py`).
- `solicitar_reset`/`confirmar_reset` (`password_reset_service.py`):
  mensaje genérico si el email no existe o la cuenta está desactivada;
  contraseña débil sí da mensaje específico (validado después de
  confirmar que el token es vigente, así que no es un riesgo de
  enumeración).
- `staff_service.set_password` nuevo -- comparte hasheo/política con el
  reset admin-driven existente (`resetear_password`), para que no
  puedan divergir.
- Conector SMTP real (`smtp_email_sender.py`, `smtplib` puro) sobre la
  cuenta dedicada `paquetex@papyrus.com.co` (MXroute).
- `StagingOverrideEmailSender`: mismo principio fail-closed que SMS,
  con una diferencia deliberada -- `EMAIL_OVERRIDE_ADDRESS` tiene
  default en código (`jesus@jemavi.co`) en vez de "cero envíos" si
  falta la variable.
- Enlaces nuevos `/staff/olvide-password` y `/staff/restablecer-password`,
  desde `auth/login.html` y el panel de staff de `auth/entrar.html`.

## Verificación

- [x] Tests del dominio (generar token, expiración, un solo uso,
      hasheo) -- 8 tests nuevos en `test_password_reset_service.py`.
- [x] Tests de las rutas (mensaje genérico, override fail-closed) -- 9
      tests nuevos en `test_password_reset.py`.
- [x] Suite de tests sin regresiones (454 passed).
- [x] Desplegado a `test.papyrus.com.co` y confirmado en vivo: flujo
      completo con una cuenta de staging real (`admin@paquetex.test`)
      vía Playwright -- solicitar reset, restablecer con un token
      vigente, toast de éxito, login con la contraseña nueva redirige
      a `/paquetes`, token queda marcado usado (no reutilizable,
      confirmado en BD). Envío SMTP real confirmado sin excepción
      contra la cuenta MXroute (dos correos de prueba efectivamente
      enviados a `jesus@jemavi.co` vía el override de staging).
