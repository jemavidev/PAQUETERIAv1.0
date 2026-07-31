# 02 — Twilio como proveedor SMS real + selección multi-proveedor (LIWA → Twilio)

**What to build:** Un operador que configura
`TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN`/`TWILIO_FROM_NUMBER` junto al
`LIWA_API_KEY` ya existente obtiene respaldo automático: todo SMS de evento
de paquete y todo código OTP le sigue llegando al residente aunque LIWA no
responda, porque el mismo mensaje se reintenta por Twilio sin ningún paso
manual. Con solo uno de los dos configurado, el comportamiento es idéntico
al de hoy (ese proveedor, directo, sin envoltorio). Sin ninguno configurado,
el comportamiento de desarrollo/test (`ConsoleNotificationSender`/
`DevOtpSender`) no cambia.

**Blocked by:** 01 — Failover genérico de SMS + mensaje OTP compartido

**Status:** ready-for-agent

- [x] `TwilioNotificationSender` y `TwilioOtpSender` existen en
      `app/domain/twilio_sender.py`, implementan
      `NotificationSender`/`OtpSender` vía `POST` directo por `httpx` a la
      Messages API de Twilio (Basic Auth con Account SID/Auth Token), y
      lanzan `RuntimeError` con mensaje claro si
      `TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN`/`TWILIO_FROM_NUMBER` no están
      los tres configurados.
- [x] El teléfono se envía a Twilio tal cual llega (ya viene en E.164 con
      `"+"`, forma canónica de `telefono.py`) — a diferencia de LIWA, que le
      quita el `"+"`.
- [x] `app/web/notifications.py::_sender_base()` y
      `app/web/otp.py::get_otp_sender()` arman el sender revisando LIWA y
      luego Twilio, en ese orden: con solo uno configurado, se devuelve ese
      sender directo (sin envoltorio de failover); con ambos configurados,
      se envuelven con el mecanismo del ticket 01 en orden LIWA → Twilio.
      (Revisión de code-review: "configurado" mira las TRES variables de
      cada proveedor vía `configurado()`, no solo una — un Twilio a medias
      ya no entra a la cadena.)
- [x] `StagingOverrideSender` sigue envolviendo lo que `_sender_base()`
      devuelva (sender único o cadena de 2) sin ningún cambio en su propio
      código, y el test fail-closed existente
      (`test_staging_sin_override_number_cero_llamadas_tras_transicion_real`)
      sigue pasando sin modificarse.
- [x] Un test nuevo prueba que con `LIWA_API_KEY` y `TWILIO_*` configurados,
      una falla de conectividad simulada en LIWA resulta en que el mensaje
      sí se envía vía el doble de Twilio, y quien llama ve éxito.
- [x] Un test nuevo prueba que con `LIWA_API_KEY` y `TWILIO_*`
      configurados, un rechazo explícito simulado de LIWA (p.ej.
      `success: false`) NO llama al doble de Twilio — la excepción se
      propaga en su lugar.
- [x] Tests de wiring nuevos/extendidos confirman: 0 configurados →
      Console/Dev; exactamente 1 configurado (cualquiera de los dos) → ese
      sender directo; 2 configurados → el wrapper de failover. Además, un
      test de regresión confirma que un Twilio a medio configurar (solo
      `TWILIO_ACCOUNT_SID`) no cuenta como configurado.
