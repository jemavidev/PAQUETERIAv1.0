# 287 — Seguimiento a [[286]]: "Enviar prueba" (SMS) reportaba éxito sin que el mensaje llegara

**Pedido original (cliente):** "dime si ya es posible enviar sms a
cualquier numero de telefono, si todo el sistema de sms esta listo
basado en aws" → confirmado el diagnóstico de infraestructura (SNS
fuera del sandbox en `us-east-1`, credenciales/región correctas en el
servidor) → "prueba desde la pagina y que sea al numero 3002596319" →
(vía `/otp/solicitar`, no llegó) → se promovió a `jveyes@gmail.com` a
ADMIN a pedido del cliente para poder usar "Enviar prueba" en
`/administracion/notificaciones` → el botón mostró "Mensaje de prueba
enviado a 3002596319" pero tampoco llegó.

**Status:** verificado — desplegado a test.papyrus.com.co y confirmado
por el cliente ("si llego") tras un envío real post-deploy.

## Investigación

1. Descartada la hipótesis de infraestructura AWS: un envío directo
   por `boto3.publish(PhoneNumber="+573002596319", ...)` desde el
   propio contenedor del servidor **sí llegó** — confirma que
   credenciales, región (`us-east-1`) y el estado fuera-de-sandbox
   (heredado del diagnóstico de [[286]]) están correctos.
2. La primera prueba "desde la página" fue vía `/otp/solicitar` (login
   de residente) — no llegó, pero resultó ser un no-envío esperado: ese
   endpoint responde IGUAL sin importar si el teléfono es elegible (no
   revela por diseño si un número está registrado), y `3002596319` no
   existe como `Persona` en la base de test.papyrus.com.co — nunca se
   encoló ningún envío. No es un bug.
3. Para probar el envío real de un ADMIN autenticado se necesitaba rol
   ADMIN — `jveyes@gmail.com` tenía `OPERADOR`; promovido a pedido
   explícito del cliente (`UPDATE usuarios SET rol='ADMIN' ...` en la
   base de test).
4. El botón "Enviar prueba" (`POST /administracion/notificaciones/probar`,
   SÍNCRONO a propósito, ver `admin.py`) reportó éxito
   ("Mensaje de prueba enviado a 3002596319") pero el SMS tampoco
   llegó. Reproducido directo por AWS CLI: `boto3.publish(PhoneNumber=
   "3002596319", ...)` (SIN el `+57`) también devuelve HTTP 200 +
   `MessageId` — AWS acepta el número mal formado como si fuera válido
   y el mensaje se pierde en la nada, sin ninguna excepción que la ruta
   pudiera mostrar como error.
5. **Causa raíz**: `admin_notificaciones_probar` (`app/web/routes/
   admin.py`) nunca normalizaba `destino` a E.164 antes de pasarlo al
   `NotificationSender` — a diferencia de `/otp/solicitar`
   (`customer_auth.py`), que sí llama `normalizar_telefono()`. Cualquier
   número escrito sin el `+57` (el caso normal si un admin lo escribe a
   mano, como acá) producía un "falso éxito".

## Corrección (implementada)

`app/web/routes/admin.py::admin_notificaciones_probar`: antes de
`notification_sender.enviar()` (rama no-EMAIL), se normaliza `destino`
con `normalizar_telefono()` (la misma función que ya usa el flujo de
OTP) — `ValueError` se traduce a un error de campo "Teléfono inválido."
en vez de un "éxito" falso.

`tests/web/test_admin_notificaciones.py`: actualizado
`test_probar_sms_envia_la_plantilla_ya_guardada_con_variables_resueltas`
para esperar el destino ya normalizado (`+573001234567` en vez de
`3001234567`) — el valor anterior documentaba el bug, no un requisito
deliberado.

## Verificación

- `tests/web/test_admin_notificaciones.py`: 34 passed.
- Suite completa: 1262 passed, sin regresiones.
- Pendiente: confirmación del cliente tras el deploy a
  test.papyrus.com.co (reintentar "Enviar prueba" al 3002596319).
