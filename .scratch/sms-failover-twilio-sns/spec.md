# Spec — Twilio y AWS SNS como proveedores SMS alternativos a LIWA (failover automático)

**Fuente:** conversación 2026-07-31 (grilling), motivada por el bloqueo de LIWA
documentado en Grupo 8 de `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`
(la API de LIWA no responde por TCP 443 desde el servidor de staging —
probable whitelist de IP pendiente del lado de LIWA).

## Problem Statement

Hoy `NotificationSender` y `OtpSender` solo tienen una implementación real:
LIWA (`LiwaNotificationSender`/`LiwaOtpSender`). Si LIWA no responde —como
ocurre ahora mismo en staging— ningún SMS de evento de paquete ni ningún
código OTP puede entregarse de verdad; no hay forma de que el sistema se
recupere solo, y nada protege contra un futuro corte de LIWA en producción.

## Solution

Twilio y AWS SNS se agregan como proveedores SMS reales adicionales,
implementando los mismos puertos (`NotificationSender`, `OtpSender`) que ya
implementa LIWA. Los tres se encadenan como **respaldo automático en tiempo
de ejecución**: LIWA se intenta primero (proveedor preferido); si el envío
falla por una razón de conectividad (no por un rechazo explícito del
proveedor), el mismo mensaje se reintenta automáticamente con Twilio, y si
ese también falla por conectividad, con AWS SNS. Un residente o miembro del
staff nunca necesita saber ni notar cuál de los tres realmente entregó el
mensaje.

Cuando solo hay credenciales de un proveedor configuradas, el comportamiento
es idéntico al actual (ese proveedor, directo, sin envoltorio de failover).
Sin ningún proveedor configurado, sigue devolviendo `ConsoleNotificationSender`/
`DevOtpSender` (desarrollo/tests, sin red real) — sin cambios ahí.

## User Stories

1. Como residente esperando un paquete, quiero recibir mi SMS de estado
   aunque LIWA no esté disponible, para enterarme siempre de que mi paquete
   fue anunciado/recibido/entregado sin depender de revisar el portal web.
2. Como residente iniciando sesión, quiero recibir mi código OTP aunque LIWA
   esté caído, para nunca quedar bloqueado de `/mis-datos` o `/mis-paquetes`
   por la falla de un solo proveedor de SMS.
3. Como operador configurando el servidor, quiero poder agregar credenciales
   `TWILIO_*` o de AWS SNS junto a las de LIWA, para que el sistema gane un
   proveedor de respaldo automáticamente, sin ningún cambio de código.
4. Como operador, quiero que LIWA siga siendo el proveedor preferido mientras
   esté sano, para seguir aprovechando por defecto la relación/tarifa ya
   establecida para Colombia.
5. Como operador, quiero que un envío fallido en un proveedor reintente
   automáticamente con el siguiente proveedor configurado, para que un
   problema de conectividad como el bloqueo actual de LIWA no requiera
   intervención manual.
6. Como operador, quiero que el failover se dispare **solo** ante fallas de
   conectividad (timeouts, 5xx, fallas de auth, DNS/TCP como el bloqueo
   actual de LIWA) — **no** ante un rechazo explícito del proveedor (número
   inválido, saldo insuficiente) — para que un mensaje que un proveedor sí
   procesó nunca se duplique reintentándolo en otro.
7. Como operador, quiero poder configurar cero, uno, dos o los tres
   proveedores y que el sistema caiga con gracia a
   `ConsoleNotificationSender`/`DevOtpSender` cuando ninguno esté configurado,
   para que desarrollo local y la suite automatizada nunca manden SMS real.
8. Como operador en staging, quiero que `StagingOverrideSender` siga
   protegiendo a los residentes reales sin importar cuál proveedor subyacente
   (LIWA/Twilio/SNS o la cadena de failover entre ellos) termine enviando,
   para que ningún mensaje de prueba de staging llegue jamás a un teléfono
   real.
9. Como desarrollador, quiero que Twilio y AWS SNS implementen los mismos
   Protocols `NotificationSender`/`OtpSender` que ya implementa LIWA, para
   que sean intercambiables en cualquier punto donde esos Protocols se usan,
   sin condicionales nuevos en la capa web.
10. Como desarrollador, quiero que las llamadas HTTP a Twilio se hagan
    directo vía `httpx` (sin SDK nuevo), igual que `LiwaNotificationSender`
    ya lo hace.
11. Como desarrollador, quiero que las llamadas a AWS SNS se hagan vía
    `boto3` (dependencia que ya existe por `S3FotoStorage`), reutilizando las
    MISMAS `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_REGION` ya
    configuradas, para que el operador no tenga que aprovisionar un segundo
    juego de credenciales AWS.
12. Como operador, quiero que AWS SNS solo se active en la cadena de
    failover si lo habilito explícitamente (una bandera dedicada), no solo
    porque ya existan credenciales AWS por S3, para que agregar `sns:Publish`
    a la política IAM existente no empiece a mandar SMS real por SNS sin
    querer.
13. Como operador, quiero que los mensajes de AWS SNS se manden con
    `SMSType=Transactional`, para que los códigos OTP y las notificaciones de
    estado tengan prioridad de entrega sobre el nivel promocional.
14. Como residente, quiero que un SMS que sí recibo se vea igual (mismo
    texto/plantilla) sin importar qué proveedor lo entregó al final, para que
    los distintos proveedores sean invisibles para mí.
15. Como desarrollador, quiero que la plantilla del mensaje OTP ("Tu código
    de verificación PAQUETEX es: {codigo}") se construya en un solo lugar, no
    duplicada por proveedor, para que un futuro cambio de copy toque un solo
    sitio, no tres.
16. Como desarrollador/tester, quiero que los senders de Twilio y AWS SNS
    tengan tests que simulan `httpx`/`boto3` exactamente como ya lo hacen
    `test_liwa_sender.py` y `test_s3_foto_storage.py`, para que la suite
    nunca toque red real ni cueste dinero al correr.
17. Como desarrollador/tester, quiero que la cadena de failover en sí tenga
    tests que simulan un primer proveedor lanzando un error de conectividad y
    verifican que el segundo proveedor es el que realmente "envía", para que
    el comportamiento de reintento quede verificado independiente de
    cualquier proveedor específico.
18. Como desarrollador/tester, quiero un test que confirme que un rechazo
    explícito de un proveedor (p.ej. `success: false`) NO dispara failover al
    siguiente, para que un cliente nunca reciba el mismo código/mensaje dos
    veces desde dos números distintos.
19. Como operador, quiero que el orden de precedencia (LIWA → Twilio → SNS)
    sea una constante simple y documentada, para poder leer el código (o este
    spec) y saber exactamente qué pasa cuando hay varios proveedores
    configurados a la vez.
20. Como desarrollador, quiero que `get_notification_sender`/`get_otp_sender`
    (y `StagingOverrideSender`) mantengan su firma y comportamiento actual
    para quien los llama, para que el código de rutas y los tests existentes
    (`test_notifications.py`, `test_customer_auth.py`, etc.) no necesiten
    cambiar más allá de lo necesario para ejercitar la cadena nueva.

## Implementation Decisions

- **Módulos nuevos:**
  - `app/domain/twilio_sender.py` — `TwilioNotificationSender` y
    `TwilioOtpSender`, llamadas REST directas vía `httpx` a la Messages API
    de Twilio (Basic Auth con Account SID/Auth Token), mismo estilo que
    `liwa_sender.py`.
  - `app/domain/sns_sender.py` — `SnsNotificationSender` y `SnsOtpSender`,
    vía `boto3.client("sns").publish(...)`, mismo estilo que
    `s3_foto_storage.py`.
  - Un wrapper genérico de failover (nuevo módulo o agregado a
    `notification_sender.py`/`otp_sender.py`) que implementa el mismo shape
    `(destino, mensaje) -> None` — reutilizable por ambos Protocols dado que,
    una vez construido el mensaje de OTP, la forma de envío es idéntica; los
    dos Protocols (`NotificationSender`/`OtpSender`) se mantienen separados
    como hoy (YAGNI documentado en `notification_sender.py`), pero comparten
    esta única pieza de control de reintento.

- **Mensaje OTP compartido:** extraer la construcción del texto ("Tu código
  de verificación PAQUETEX es: {codigo}") a un solo lugar en
  `otp_sender.py`, usado por `LiwaOtpSender`, `TwilioOtpSender` y
  `SnsOtpSender` — elimina la duplicación de copy entre los tres.

- **Clasificación de errores reintentables (dispara failover):**
  - `httpx`: `ConnectError`, `ConnectTimeout`, `ReadTimeout`,
    `TransportError`; también un `HTTPStatusError` cuyo `status_code` sea
    5xx, 401 o 403 (fallo de red/infra/auth, no de contenido del mensaje).
  - `boto3`/`botocore`: errores de conexión (`EndpointConnectionError`,
    timeouts) y `ClientError` con códigos tipo `Throttling`/`InternalError`.
  - **No reintentable** (falla el envío completo, sin probar el siguiente
    proveedor): un `RuntimeError` explícito que ya representa un rechazo del
    proveedor que sí recibió la solicitud — LIWA `success: false`, un 4xx de
    Twilio que no sea 401/403 (número inválido, etc.), o una respuesta de
    SNS sin `MessageId`. Estos ya son `RuntimeError` hoy en `liwa_sender.py`
    y se mantienen así; el wrapper de failover distingue por tipo/atributo de
    excepción, no reintenta sobre estos.

- **Precedencia de proveedores:** constante fija `LIWA → Twilio → SNS`.
  `_sender_base()` (en `app/web/notifications.py`) y `get_otp_sender()` (en
  `app/web/otp.py`) recorren esa lista, incluyen cada proveedor cuya
  configuración esté completa:
  - LIWA: `LIWA_API_KEY` (comportamiento actual, sin cambios).
  - Twilio: `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` + `TWILIO_FROM_NUMBER`
    (los tres).
  - SNS: `AWS_SNS_SMS_ENABLED=true` (bandera explícita — ver más abajo por
    qué no basta con que ya existan credenciales AWS de S3).
  - 0 proveedores → `ConsoleNotificationSender`/`DevOtpSender` (sin cambios).
  - 1 proveedor → ese sender directo, sin envolver en failover (igual que
    hoy con solo LIWA — no se agrega indirección innecesaria).
  - 2+ proveedores → envueltos en el wrapper de failover, en el orden de la
    lista.
  - `StagingOverrideSender` no cambia: sigue envolviendo lo que
    `_sender_base()` devuelva, sea un sender único o la cadena de failover.

- **Twilio — config y llamada:** `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
  `TWILIO_FROM_NUMBER` (los tres obligatorios o `_config()` lanza
  `RuntimeError`, igual que LIWA). `POST
  https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`,
  Basic Auth `(AccountSid, AuthToken)`, body form-encoded `{"To": destino,
  "From": TWILIO_FROM_NUMBER, "Body": mensaje}`. El `destino` ya llega en
  E.164 con `"+"` (forma canónica de `telefono.py`) — se pasa tal cual, a
  diferencia de LIWA que le quita el `"+"`.

- **AWS SNS — config y llamada:** reutiliza
  `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_REGION` (cadena estándar
  de credenciales de `boto3`, igual que `S3FotoStorage`), habilitado por la
  bandera explícita nueva `AWS_SNS_SMS_ENABLED=true` — necesaria porque esas
  credenciales AWS ya pueden existir hoy solo para S3, y activar SNS por su
  sola presencia rompería el patrón de "flag explícito" que ya usa
  `S3FotoStorage` (gateado por `AWS_S3_BUCKET_NAME`, no por credenciales
  genéricas). Llamada: `boto3.client("sns",
  region_name=...).publish(PhoneNumber=destino, Message=mensaje,
  MessageAttributes={"AWS.SNS.SMS.SMSType": {"DataType": "String",
  "StringValue": "Transactional"}})`.

- No existe hoy un `env.example`/`.env.staging.example` propio del rebuild
  (los archivos existentes son del sistema legacy) — no se crea uno nuevo en
  este slice; las variables nuevas quedan documentadas aquí y en los
  docstrings de los módulos nuevos, mismo patrón que se usó para introducir
  `LIWA_*`.

## Testing Decisions

Un buen test aquí ejercita solo el comportamiento externo — el límite
HTTP/boto3 — nunca detalles internos del proveedor. Mismo criterio que
`test_liwa_sender.py`/`test_s3_foto_storage.py`: se reemplaza `httpx.post` /
`boto3.client` por un doble de prueba vía `monkeypatch`, nunca red real ni
costo real.

- `tests/data_model/test_twilio_sender.py` (nuevo) — espejo de
  `test_liwa_sender.py`: `monkeypatch` sobre `httpx.post`, verifica Basic
  Auth y payload form-encoded; test de "sin credenciales" → `RuntimeError`;
  tests de envío para `TwilioNotificationSender` y `TwilioOtpSender` (el
  mensaje OTP contiene el código).
- `tests/data_model/test_sns_sender.py` (nuevo) — espejo de
  `test_s3_foto_storage.py`: `monkeypatch` sobre `boto3.client` con un doble
  que graba las llamadas a `.publish(**kwargs)`; verifica `PhoneNumber`,
  `Message` y el `MessageAttributes` de tipo Transactional; test de "bandera
  no habilitada" → el sender no se construye/usa.
- `tests/data_model/test_sms_failover.py` (nuevo) — tests unitarios del
  wrapper de failover en sí, con senders falsos (mismo patrón
  `_SenderEspia`/`_SenderQueFalla` ya usado en `test_notifications.py`/
  `test_customer_auth.py`):
  - el primero responde bien → el segundo nunca se llama.
  - el primero lanza un error reintentable → se prueba el segundo y
    responde bien.
  - el primero lanza un rechazo explícito (no reintentable) → el segundo NO
    se prueba, la excepción se propaga.
  - todos los configurados lanzan errores reintentables → se propaga la
    última excepción.
- `tests/web/test_notifications.py` y el equivalente de `otp.py` (extender,
  no reemplazar): un test donde `LIWA_API_KEY` y `TWILIO_*` están
  configurados a la vez → `get_notification_sender()`/`get_otp_sender()`
  devuelve el wrapper de failover envolviendo ambos, en ese orden; un test
  donde solo un proveedor está configurado → se devuelve ese sender directo,
  sin envoltorio (mismo espíritu que
  `test_sin_web_env_devuelve_console_sender_directo`).
- El test fail-closed existente,
  `test_staging_sin_override_number_cero_llamadas_tras_transicion_real`,
  debe seguir pasando sin alterar su intención — agregar una variante con
  varios proveedores configurados a la vez, para dejar fijo que la garantía
  fail-closed sobrevive a la cadena nueva.
- Prior art: `tests/data_model/test_liwa_sender.py` (patrón `monkeypatch` de
  `httpx`), `tests/data_model/test_s3_foto_storage.py` (patrón `monkeypatch`
  de `boto3`), `tests/web/test_notifications.py` (patrón de wiring +
  fail-closed), `tests/web/test_customer_auth.py` (patrón `_SenderQueFalla`
  para falla de proveedor a nivel de ruta).

## Out of Scope

- Soporte de `TWILIO_MESSAGING_SERVICE_SID` — solo un `TWILIO_FROM_NUMBER`
  por ahora ("solo SMS por ahora", decisión del usuario en el grilling).
  Puede agregarse después como alternativa de configuración sin tocar el
  Protocol.
- Orden de precedencia configurable por el operador (variable de entorno
  para reordenar proveedores) — `LIWA → Twilio → SNS` es una constante fija
  en este slice.
- Plantillas de mensaje distintas por proveedor — los tres mandan
  exactamente el mismo texto; no hay copy A/B ni por proveedor.
- Despliegue real (credenciales verdaderas de Twilio/AWS SNS, permiso IAM
  `sns:Publish`, verificar entrega real) — misma categoría que el whitelist
  de IP de LIWA (Grupo 8) y el bucket S3 (Grupo 15) aún pendientes: el
  código y los tests quedan 100% listos, la activación es un cambio de
  configuración en el servidor, no de código.
- WhatsApp, voz, o cualquier canal no-SMS vía Twilio o SNS.
- Límites de tasa o tope de costo entre proveedores (p.ej. alertar tras N
  usos de SNS) — no existe ese control para LIWA hoy tampoco; no se
  introduce aquí.
- Migrar fuera de LIWA — LIWA sigue siendo el proveedor preferido; esto es
  resiliencia aditiva, no un reemplazo de proveedor.

## Further Notes

- **Motivación real:** la API de LIWA no completa el handshake TCP 443
  desde el servidor de staging (`52.6.204.211` → `api.liwa.co`) — LIWA
  probablemente restringe su API por IP y no ha autorizado esta IP todavía
  (ver Grupo 8, `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`).
  Este spec no resuelve ese whitelist — LIWA sigue como proveedor preferido
  y se asume que eventualmente se autoriza— pero evita que staging/producción
  dependan únicamente de LIWA mientras tanto.
- Las credenciales reales de Twilio y AWS SNS
  (`TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN`/`TWILIO_FROM_NUMBER`, habilitar
  `AWS_SNS_SMS_ENABLED` + agregar `sns:Publish` a la política IAM existente)
  no están provistas todavía — mismo patrón "bloqueado en confirmación
  externa, código listo de todas formas" ya usado con LIWA (Grupo 8) y S3
  (Grupo 15). Los tickets de este slice se entregan completamente probados
  con proveedores simulados; salir a producción es un cambio de
  configuración en el servidor, no de código.
