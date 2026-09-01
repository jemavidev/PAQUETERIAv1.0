# 288 — Seguimiento a [[287]]: SMS multi-segmento por tildes, 14-20 min de demora

**Pedido original (cliente):** "revisa si la plantilla real cae en 3
segmentos, la idea es que los sms se reciban en el menor tiempo posible"
— tras activar logging de entrega de AWS SNS ([[287]]) para diagnosticar
por qué dos envíos de prueba no mostraban rastro en CloudWatch.

**Status:** implementado y desplegado.

## Investigación

1. Activado logging de estado de entrega de SNS (rol IAM
   `paquetex-sns-delivery-logging` + `DeliveryStatusIAMRole`/
   `DeliveryStatusSuccessSamplingRate=100` a nivel de cuenta) para dejar
   de adivinar por qué algunos envíos de prueba no llegaban.
2. Dos envíos desde `/administracion/notificaciones/probar` que parecían
   "perdidos" (sin rastro en CloudWatch tras varios minutos) en realidad
   SÍ se entregaron -- el log tardó en aparecer porque el `dwellTimeMs
   UntilDeviceAck` fue de **20.7 min y 14.2 min** respectivamente, contra
   ~1-2 SEGUNDOS de los envíos de una sola parte.
3. Causa: esos dos mensajes eran de **3 segmentos SMS**
   (`numberOfMessageParts: 3`) contra 1 de los otros. La plantilla
   RECIBIDO por defecto ("Hola {recipient_name}, tu paquete con código
   {access_code} está {estado}. Consulta más detalles aquí: {link}"),
   con valores reales, mide ~135 caracteres -- pero las tildes agudas
   (á, í, ó -- "código", "está", "más", "aquí") NO existen en el alfabeto
   GSM-7 (ver GSM 03.38: sólo à/è/é/ì/ò/ù/ä/ö/ñ/ü/å están, las agudas no),
   así que el mensaje ENTERO cae a codificación UCS-2 -- que recorta el
   límite por segmento de 160/153 a 70/67 caracteres, empujando un
   mensaje de 135 caracteres a 3 partes en vez de 1.
4. La plantilla de ENTREGADO/SMS (personalizada, con la marca "Los
   Robles") tenía el mismo problema por "portería" (í) y un em-dash "—"
   (tampoco GSM-7) -- 99 caracteres, 2 partes UCS-2.
5. De paso: la plantilla RECIBIDO/SMS en la base de test tenía un " 123"
   colado (artefacto de una prueba manual guardada sin querer durante
   este mismo diagnóstico) -- se retiró junto con el fix de tildes.
6. Verificado que el problema NO se resolvía del todo con solo limpiar la
   plantilla: `{recipient_name}` es dato libre -- un nombre real como
   "María"/"Andrés" (comunísimos) reintroduce el mismo carácter fuera de
   GSM-7 y vuelve a forzar UCS-2/3 segmentos, aunque la plantilla en sí ya
   esté limpia. `normalizar_nombre()` (`texto.py`) solo mayúscula, no
   retira tildes.

## Corrección (implementada)

- `app/domain/notificacion_service.py::PLANTILLAS_DEFAULT`: tildes
  agudas retiradas de los 4 textos por defecto (á→a, í→i, ó→o -- "esta",
  "codigo", "mas", "aqui"). Mismo cuerpo compartido por SMS/Email/
  WhatsApp (decisión ya existente) -- sin tildes se lee perfectamente
  bien en un mensaje informal, y la prioridad explícita del cliente es
  la velocidad de entrega del SMS.
- Plantilla RECIBIDO/SMS en la base de test.papyrus.com.co: corregida
  vía la propia UI de admin (mismo texto que el nuevo default, sin
  tildes, sin el " 123" accidental).
- Plantilla ENTREGADO/SMS (personalizada) en la base de test: corregida
  vía la UI de admin -- "portería"→"porteria", em-dash "—"→"-", se
  mantiene la marca "Los Robles" intacta.
- Con esto, el mensaje de RECIBIDO cae en **1 solo segmento GSM-7**
  (135 caracteres, bajo el límite de 160) en vez de 3 UCS-2 -- de
  minutos de demora a la entrega casi instantánea que ya se veía en los
  mensajes de una sola parte.
- `app/domain/notificacion_service.py::_sin_tildes()` + aplicada al
  final de `construir_mensaje()`: retira diacríticos (NFKD + encode/
  decode ascii) del mensaje YA armado -- cubre `{recipient_name}` (dato
  libre) además de la plantilla estática. Solo toca el SMS real
  (`construir_mensaje` es exclusivo de ese canal, Email/WhatsApp usan su
  propio camino y conservan tildes donde no hay límite de segmento).

## Verificación

- `tests/web/test_admin_notificaciones.py`,
  `tests/data_model/test_plantilla_notificacion_multicanal.py`,
  `tests/data_model/test_notificacion_service.py`: 72 passed (asserts de
  texto default actualizados de `"está {estado}"` a `"esta {estado}"`;
  nuevo test `test_mensaje_sin_tildes_aunque_el_nombre_del_destinatario_
  las_tenga` fija el caso de `{recipient_name}` con tilde real).
- Suite completa: 1263 passed, sin regresiones.
- Desplegado a test.papyrus.com.co. Pendiente que el cliente confirme
  con una prueba real que el próximo SMS de RECIBIDO llega casi al
  instante (verificado).
