# 326 — `/announce`: la bandera "Auto" gatea el botón Recibir (WhatsApp para pedir autorización)

**Pedido original (cliente):**

> "3 - [...] lo que se quiere para el proceso de 'ANUNCIAR' es que si la bandera que acabas de
> identificar está desactivada, aparezca la posibilidad de mandar un mensaje de whatsapp por medio
> de un ícono que funcione como link de whatsapp, este podrá ser enviado al número del cliente que
> está solicitando anunciar el paquete, este mensaje que se pretende mandar le estará solicitando
> al cliente autorización para poder recibir un paquete en su nombre (es necesario crear en la
> plantilla de notificaciones este mensaje que se utilizará) este es el contenido del mensaje
> '¡Buen dia veci! Le saludamos desde la papelería Papyrus. Un domiciliario está aquí en nuestras
> instalaciones con un paquete a su nombre. ¿Nos autoriza recibirlo por usted?'. En caso que sí
> esté habilitada esta bandera de auto recepción, la idea es que no aparezca el enlace a WhatsApp,
> solo aparecerá algo que indique que este cliente ya tiene la opción de recibir paquetes
> automáticamente (puede ser una píldora que solo diga 'Auto').
>
> 4 - Con relación al flujo de recibir paquetes [...] 1. Bandera desactivada, se utiliza el proceso
> de notificar por WhatsApp al cliente [...] 2. Si esta bandera está activada, solo se debe
> presionar el botón de recibir y este internamente deberá anunciar el paquete y paralelo después
> de anunciarlo abrir el modal de recepción de paquetes para continuar con este flujo."

**Status:** implementado, pendiente desplegar a test.papyrus.com.co y que el cliente lo confirme.

## Decisiones de alcance (confirmadas con el cliente antes de implementar)

1. Con la bandera ACTIVADA, la tarjeta de identificación de `/announce` muestra Anunciar Y Recibir
   (no solo Anunciar) -- Recibir sigue siendo `accion=recibir` tal cual (ticket 06: anuncia y abre
   el modal de recepción ya abierto). La píldora "Auto" es solo indicador, no reemplaza ningún
   botón.
2. El mensaje de autorización queda en una plantilla editable a futuro (mismo mecanismo de
   `PlantillaNotificacion` que ya usan los 4 eventos del Paquete), pero SIN pantalla de admin
   dedicada todavía -- eso es un follow-up, no parte de este issue.
3. Cuando el destinatario es un Ocupante sin Persona propia, la bandera/número a quien se le pide
   autorización se resuelve igual que el Anunciante (`anunciante_para_ocupante`: cae al Principal
   de la unidad) -- sin inventar una segunda resolución.

## Diseño

La bandera (`Persona.autoriza_recepcion_automatica`, hasta ahora puramente informativa -- ver
`persona.py`) empieza a gatear comportamiento real por primera vez:

- **ON** -- píldora "Auto" junto al nombre; Anunciar + Recibir como siempre (sin cambios en el
  mecanismo de `accion=recibir`).
- **OFF** (default) -- sin píldora; el botón Recibir se reemplaza por un link de WhatsApp
  (`wa.me`/`web.whatsapp.com`, mismo patrón mobile/desktop que el resto de la app) con el mensaje
  de autorización pre-cargado (`?text=`). Solo Anunciar queda como acción del formulario -- recibir
  de verdad ocurre después (una vez autorizado fuera del sistema) desde la píldora ANUNCIADO de
  "Ya tiene paquetes en curso" ([[325]]), que ya abre `/paquetes?recibir=<id>`.

El mensaje NO es uno de los 4 eventos del Paquete que dispara `NotificationSender`
(ANUNCIADO/RECIBIDO/ENTREGADO/CANCELADO) -- se dispara manualmente por clic del staff, ANTES de que
exista ningún Paquete. Reusa la tabla `PlantillaNotificacion` (columna `evento` es `String(20)`
libre, no un enum a nivel de BD) con un valor de evento propio (`PEDIR_AUTORIZACION`), para que
quede editable a futuro con el mismo mecanismo de "tabla como override" sin tocar el sistema de
admin existente (atado a `EstadoPaquete`).

## Implementación

- `app/domain/notificacion_service.py`: `EVENTO_SOLICITUD_AUTORIZACION` ("PEDIR_AUTORIZACION"),
  `TEXTO_SOLICITUD_AUTORIZACION_DEFECTO` (texto literal del cliente) y
  `texto_solicitud_autorizacion(session)` -- busca override en `PlantillaNotificacion`, si no el
  default. Deliberadamente NO reusa `construir_mensaje`/`_buscar_plantilla` (ambos exigen un
  `EstadoPaquete` real vía `evento.value`).
- `app/domain/persona_service.py`: `url_whatsapp`/`url_whatsapp_desktop` ganan un `texto: str = None`
  opcional -- agrega `?text=`/`&text=` percent-encoded cuando viene, retrocompatible con los
  callers existentes.
- `app/web/routes/announce_new.py`: `_info_autorizacion(session, persona)` -- decide
  `(autoriza_auto, whatsapp_url_mobile, whatsapp_url_desktop)`; cableado en los 3 lugares que
  renderizan la tarjeta compartida (`announce_identificar` directo, su rama de co-residentes
  preseleccionada, y `announce_identificar_ocupante`, este último resolviendo el contacto vía
  `anunciante_para_ocupante`).
- `app/web/templates/components/_persona_resuelta.html`: nuevos parámetros
  `autoriza_auto`/`whatsapp_solicitud_url(_desktop)` -- píldora "Auto" junto al nombre; botón
  Recibir SOLO si `autoriza_auto`, si no un link de WhatsApp armado a mano (mismo motivo que
  `persona.py` ya documentaba para Usuario de WhatsApp: `iconos_nav.whatsapp` es un ícono SOLID,
  `boton()` solo sabe renderizar íconos outline).

## Verificación

- 14 tests nuevos: 3 en `tests/data_model/test_notificacion_service.py` (default/override/canal
  ignorado), 4 en `tests/data_model/test_persona_service.py` (`texto=` en ambas variantes), 8 en
  `tests/web/test_announce_new.py` (los 3 caminos de identificación × bandera ON/OFF, más el
  fallback a Principal y el caso sin identidad resoluble).
- Suite completa `tests/web/test_announce_new.py`: 81/81 en verde.
- `tests/data_model/test_persona_service.py` + `tests/data_model/test_notificacion_service.py`:
  78/78 en verde.
