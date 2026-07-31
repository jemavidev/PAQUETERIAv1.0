# 03 — AWS SNS como proveedor SMS real + tercer eslabón (LIWA → Twilio → SNS)

**What to build:** Un operador que además configura
`AWS_SNS_SMS_ENABLED=true` (reutilizando las
`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_REGION` ya configuradas
para S3) obtiene un tercer respaldo automático: si LIWA y Twilio no
responden, el mismo mensaje sale por AWS SNS como SMS Transactional, sin
ningún paso manual. AWS SNS nunca se activa solo porque ya existan
credenciales AWS por S3 — exige la bandera explícita.

**Blocked by:** 02 — Twilio como proveedor SMS real + selección
multi-proveedor (LIWA → Twilio)

**Status:** ready-for-agent

- [x] `SnsNotificationSender` y `SnsOtpSender` existen en
      `app/domain/sns_sender.py`, implementan
      `NotificationSender`/`OtpSender` vía
      `boto3.client("sns").publish(PhoneNumber=destino, Message=mensaje,
      MessageAttributes={"AWS.SNS.SMS.SMSType": {"DataType": "String",
      "StringValue": "Transactional"}})`, reutilizando la cadena estándar
      de credenciales de `boto3` (mismas `AWS_ACCESS_KEY_ID`/
      `AWS_SECRET_ACCESS_KEY`/`AWS_REGION` que `S3FotoStorage`). Además
      (revisión de code-review, gap real del spec): una respuesta sin
      `MessageId` se trata como rechazo no reintentable, no como éxito
      silencioso.
- [x] SNS solo se incluye en la lista de precedencia de proveedores cuando
      `AWS_SNS_SMS_ENABLED=true` está presente — tener credenciales AWS
      configuradas (p.ej. por S3) no lo activa por sí solo.
- [x] `app/web/notifications.py::_sender_base()` y
      `app/web/otp.py::get_otp_sender()` extienden la lista de precedencia a
      LIWA → Twilio → SNS, envolviendo el subconjunto que esté configurado
      (0, 1, 2 o 3) con las mismas reglas del ticket 02 (0 → Console/Dev, 1
      → directo, 2+ → cadena de failover en ese orden). Dispatch extraído a
      `sms_failover.construir_sender()`, compartido entre ambos archivos
      (hallazgo de code-review de duplicación).
- [x] Un test nuevo prueba que con los tres proveedores configurados, fallas
      de conectividad simuladas en LIWA y Twilio resultan en que el mensaje
      se envía vía el doble de SNS.
- [x] El test fail-closed de staging gana una variante con los tres
      proveedores configurados a la vez, confirmando cero llamadas a
      cualquier sender envuelto cuando `SMS_OVERRIDE_NUMBER` no está
      definido.
- [x] La suite completa de tests (`pytest`) pasa — 435/435 (incluye
      `boto3==1.34.0` agregado a `requirements-ci.txt`, gap preexistente de
      CI para que Grupo 15/S3 y este ticket corran en el pipeline real).
