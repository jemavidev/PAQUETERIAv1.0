# 322 — OTP y código de acceso: nunca visibles en vistas públicas no autenticadas

**Pedido original (cliente):**

> "El OTP nunca debe ser visible para las vistas publicas, este solo se mandara por mensaje de
> texto SMS unicamente. analiza que vistas generan y muestran el OTP, te dire que hacer con esas
> vistas."

Tras el análisis, dos correcciones puntuales derivadas:

> "corrije la fuga y por ahora continuemos con el codigo de acceso"

> "Vamos a enfocarnos en el como sera compartido este codigo. Este codigo el personal de staff
> siempre tendra acceso a el. Solo se compartira a los clientes/residentes por medio de
> sms/whatsapp/email, en las vistas publicas (no autenticadas) no sera posible visualizar el
> codigo. En caso que en una vista publica se consulte un codigo de acceso es porque ya este se
> conoce y se podra interactuar con este, pero nunca revelarlo en vistas publicas."

**Status:** implementado, desplegado a test.papyrus.com.co (2026-09-06, commits `bf2e54f`/`3b4e544`
en PaqueteX) -- pendiente que el cliente lo confirme visualmente.

## Análisis (OTP)

El flujo OTP activo en producción (`app.web.app:app`, confirmado contra el Dockerfile del repo de
deploy -- NO `src/main.py`, un monolito legado que no corre en producción) ya cumplía la regla:
`app/domain/otp_service.py::preparar_otp` genera el código y lo devuelve SOLO como tupla para un
`BackgroundTask` que lo entrega vía `OtpSender` (SNS/LIWA/Twilio) -- nunca pasa por un
`TemplateResponse` ni un JSON de respuesta. Los templates `auth/customer_login.html` y
`auth/customer_verify.html` son solo formularios.

Sí se encontró una fuga real, pero en el monolito legado (`app/routes/customer_portal.py` +
`app/services/customer_portal_service.py`, NO desplegado en producción): el código se escribía en
texto plano en los logs del servidor (`logger.info(f"...código: {otp.otp_code}...")`, tanto al
enviarlo como al verificarlo). Corregido: los logs ya no incluyen el valor del código.

(Nota aparte, no corregida en esta ronda -- fuera del alcance que el cliente pidió enfocar: ese
mismo código legado también envía el código/"contraseña temporal" por EMAIL en
`customer_preferences_otp.py`/`email_service.py`, lo que violaría "solo por SMS" si ese código
volviera a activarse. Queda registrado para una futura limpieza de código muerto.)

## Análisis (código de acceso)

El código de acceso (`Paquete.access_code`, 4 caracteres, `paquete_service.py`) es distinto al
OTP -- por diseño es la llave de consulta pública en `/consultar` ("el access_code únicamente lo
conoce quien anunció, así que es la única llave de consulta pública", comentario ya existente en
`search.py`). El cliente confirmó 3 decisiones de alcance antes de implementar:

1. Criterio de "mismo cliente" para trabajo relacionado (issue 323): mismo `recipient_phone`.
2. `/paquetes` (staff) sigue mostrando el código sin restricción -- no cambia.
3. `/mis-paquetes` (cliente autenticado por OTP) sigue mostrando el código -- es una vista
   autenticada, no "pública" en el sentido de esta regla.

Se encontró una sola vista pública no autenticada que sí lo exponía: `GET /anunciar/confirmacion`
(`app/web/routes/announce.py`) -- lo mostraba en pantalla (`components/_confirmacion.html`) Y en
la URL (`?codigo=<access_code>`), inmediatamente después de crear el paquete, antes de que llegara
el SMS. `/consultar` (la otra vista pública) ya cumplía: solo repite en el buscador lo que la
propia persona ya tecleó, nunca imprime `paquete.access_code` de forma independiente.

## Implementación

- `app/services/customer_portal_service.py`: los 2 `logger.info` que incluían el código OTP en
  texto plano ya no lo hacen (líneas ~116 y ~158).
- `app/web/routes/announce.py`: `POST /anunciar` redirige a
  `/anunciar/confirmacion?id=<uuid del Paquete>` en vez de `?codigo=<access_code>`. `GET
  /anunciar/confirmacion` busca por `id` (UUID), ya no por `access_code`, y ya no lo pasa al
  contexto del template. `id` no sirve como llave en ningún otro endpoint público (`/consultar`
  solo acepta `access_code`/`guide_number`), así que no se abre una puerta nueva.
- `app/web/templates/announce/confirmacion.html`: ya no llama a `confirmacion_exito` con
  `codigo=access_code` -- el bloque de código destacado no se renderiza. Subtítulo cambiado a "En
  un momento te llega por SMS el código que vas a necesitar...".
- `tests/web/test_announce.py`: 2 tests actualizados para afirmar que el código NUNCA aparece en
  el HTML ni en la URL de esta vista pública (antes afirmaban lo contrario).

## Verificación

- Suite `tests/web/` completa: 837/837 en verde (sin regresiones).
- En vivo contra el servidor real de dev (`localhost:8010`): anuncio real → confirmación con
  `?id=<uuid>` en la URL, código real (`9ZQF` en la prueba) presente en la BD pero ausente del
  HTML y de la URL de la respuesta.
