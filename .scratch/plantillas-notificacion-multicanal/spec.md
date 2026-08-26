# Plantillas de notificación multicanal (SMS / Email / WhatsApp)

Fuente: conversación en vivo 2026-08-26 (grilling), pedido directo del cliente vía Jesús. Extiende `.scratch/notificaciones-anunciado-plantillas` (Grupo 8) y `.scratch/preferencia-notificacion-matriz` (Grupo 13).

## Problem Statement

Hoy solo existe edición de contenido de mensaje para **un canal**: SMS, desde `/administracion/notificaciones` (tabla `plantillas_notificacion`, única por `evento`+`motivo`). El cliente quiere poder editar el texto de los avisos también para **Email** y **WhatsApp**, aunque hoy ninguno de los dos tenga envío real conectado — `CanalNotificacion` (dominio `preferencia_notificacion.py`) ya modela `EMAIL` y `WHATSAPP` como opciones de preferencia por Persona, pero seleccionarlas hoy no dispara nada porque no existe contenido ni envío para ellas. El cliente decidirá más adelante cuáles canales activar de verdad; por ahora quiere tener el contenido de **todos los mensajes posibles** listo y editable.

## Solution

Se extiende el sistema de plantillas existente para cubrir 3 canales (SMS, Email, WhatsApp) sobre las mismas 7 combinaciones evento/motivo que ya existen hoy (`ANUNCIADO·Cliente`, `ANUNCIADO·Staff`, `RECIBIDO`, `ENTREGADO`, `CANCELADO` × cada `MotivoCancelacion`) — 21 plantillas en total. Email agrega un campo de asunto y una vista previa en vivo que muestra el texto ya envuelto en un layout de marca (logo Papyrus + enlaces del sitio); WhatsApp reutiliza el mismo formato de texto libre con placeholders con nombre que SMS, sin adoptar todavía el formato de plantilla pre-aprobada que exigirá un proveedor real de WhatsApp Business. Cada guardado queda registrado en un historial de auditoría (quién, cuándo, texto anterior/nuevo), sin botón de revertir. Sigue siendo exclusivo de `ADMIN`. **No se conecta ningún envío real de Email ni WhatsApp en esta rebanada** — es solo el sistema de contenido; conectar el envío real es una decisión y un trabajo aparte que el cliente indicará cuándo hacer.

## User Stories

1. Como ADMIN, quiero ver las 7 combinaciones evento/motivo agrupadas (una por fila), para no tener que buscar entre 21 filas sueltas.
2. Como ADMIN, quiero cambiar entre pestañas SMS / Email / WhatsApp dentro de cada fila de evento, para editar los 3 canales de un mismo evento sin perder el contexto de cuál evento estoy viendo.
3. Como ADMIN, quiero que cada canal de cada evento tenga su propio texto independiente, para poder decir algo distinto por SMS que por Email si el tono o el detalle lo amerita.
4. Como ADMIN, quiero que si no he personalizado un canal para un evento, se muestre un texto por defecto razonable (no vacío), para no encontrarme una pestaña en blanco que parezca un error.
5. Como ADMIN, quiero que el texto por defecto de Email/WhatsApp tenga el mismo contenido informativo que el de SMS para ese evento, para no partir de cero redactando algo que ya existe.
6. Como ADMIN, quiero un campo de Asunto separado para la plantilla de Email de cada evento, porque un correo sin asunto claro se ve poco profesional y puede perderse entre spam.
7. Como ADMIN, quiero ver una vista previa en vivo del correo mientras edito (asunto + cuerpo ya resuelto con datos de ejemplo, dentro del layout con logo y enlaces), para saber cómo se va a ver de verdad antes de guardar.
8. Como ADMIN, quiero que la vista previa de Email use datos de ejemplo (nombre, código de acceso, motivo) en vez de placeholders sin resolver, para juzgar el mensaje tal como lo verá un cliente real.
9. Como ADMIN, quiero que el layout con logo de Papyrus y enlaces del sitio se aplique automáticamente a cualquier texto que escriba, para no tener que maquetar HTML yo mismo cada vez.
10. Como ADMIN, quiero ver la lista de variables disponibles (`{recipient_name}`, `{access_code}`, `{motivo}` según el evento) en las pestañas de SMS y WhatsApp, igual que hoy, para saber qué puedo insertar en el texto.
11. Como ADMIN, quiero que WhatsApp use el mismo tipo de placeholder con nombre que SMS (no variables numeradas de proveedor), para poder editarlo sin entender todavía la sintaxis que exigirá un proveedor de WhatsApp Business.
12. Como desarrollador, quiero que el formato real de plantilla de WhatsApp (variables numeradas, categoría, aprobación de Meta) quede fuera de esta rebanada, para no diseñar a ciegas un formato atado a un proveedor que el cliente todavía no eligió.
13. Como ADMIN, quiero que las 7 filas de evento/motivo sean exactamente las mismas para los 3 canales (sin canal con menos variantes que otro), para que la pantalla sea predecible y no tenga que recordar excepciones por canal.
14. Como ADMIN, quiero que guardar el texto de un canal de un evento no afecte el texto de los otros 2 canales del mismo evento, para poder editar uno sin arriesgar los demás.
15. Como desarrollador, quiero que las plantillas SMS existentes (ya personalizadas por el cliente) se preserven exactamente igual tras la migración, para no perder contenido que el cliente ya configuró.
16. Como ADMIN, quiero que cada vez que guardo un cambio quede un registro de quién lo hizo y cuándo, para poder responder "quién cambió esto y cuándo" si alguna vez hace falta.
17. Como ADMIN, quiero que el historial guarde el texto anterior y el nuevo (y el asunto anterior/nuevo para Email), para poder ver qué decía antes sin tener que adivinar.
18. Como ADMIN, no necesito un botón para revertir un cambio desde el historial en esta rebanada, porque alcanza con poder consultar qué pasó; revertir se puede hacer manualmente reescribiendo el texto.
19. Como ADMIN, quiero que solo el rol ADMIN pueda ver y editar las plantillas de los 3 canales, igual que hoy, para que el contenido oficial de cara al cliente final no lo pueda tocar cualquier miembro del staff.
20. Como OPERADOR (no-ADMIN), al intentar entrar a la pantalla de plantillas debo recibir 403, igual que hoy, para que quede claro que esta pantalla es exclusiva de ADMIN.
21. Como desarrollador, quiero que ningún envío real (Email o WhatsApp) se dispare como efecto de este trabajo, para no sorprender al cliente final con mensajes que nadie decidió activar todavía.
22. Como desarrollador, quiero que el texto y asunto de Email queden guardados en la misma tabla `plantillas_notificacion` (con columna `canal` nueva), para no duplicar la lógica de unicidad y fallback que ya existe para SMS.
23. Como cliente final (fuera de alcance de envío hoy, pero relevante a futuro), quiero que cuando se conecte el envío real de Email, el contenido ya estará listo y con la marca aplicada, para que activar el canal no requiera rediseñar nada de contenido.
24. Como desarrollador, quiero que la función que envuelve el texto en el layout de marca sea la misma que usará el envío real de Email el día que se conecte, para no mantener dos versiones del layout que puedan divergir.

## Implementation Decisions

- **Tabla `plantillas_notificacion` (extender, no crear una nueva):**
  - Nueva columna `canal` (`String(20)`, `NOT NULL`) — valores restringidos a `CanalNotificacion.SMS` / `EMAIL` / `WHATSAPP` (reutiliza el enum ya existente en `preferencia_notificacion.py`; `LLAMADA` queda fuera, no se pide ni se modela aquí).
  - Nueva columna `asunto` (`String`, nullable) — solo se usa cuando `canal == EMAIL`; queda `NULL` para SMS/WhatsApp.
  - `UniqueConstraint("evento", "motivo", "canal")` reemplaza la actual `UniqueConstraint("evento", "motivo")`; el índice único parcial `uq_plantillas_notificacion_evento_motivo_nulo` (para `motivo IS NULL`) se extiende para incluir `canal` en sus columnas, mismo mecanismo (Postgres trata cada `NULL` como distinto, así que el índice parcial sigue siendo necesario con la columna nueva).
  - **Migración de datos:** las filas SMS existentes (creadas antes de esta rebanada, sin columna `canal`) se backfillean con `canal='SMS'` — preserva exactamente el contenido que el cliente ya personalizó, sin pérdida.

- **Nueva tabla `plantillas_notificacion_historial`** (append-only, sin UPDATE ni DELETE):
  `id`, `plantilla_id` (FK a `plantillas_notificacion.id`), `evento`, `motivo` (nullable), `canal` — denormalizados desde la plantilla para poder consultar el historial sin join, igual espíritu que el resto del dominio (evento/motivo ya se guardan como `String` plano, no FK a enum); `usuario_id` (FK a `Usuario`, quién hizo el cambio); `texto_anterior` (nullable — `NULL` en la primera personalización de una fila); `texto_nuevo`; `asunto_anterior` / `asunto_nuevo` (nullable, solo relevantes para `EMAIL`); `creado_en`. Se inserta una fila en cada `guardar_plantilla` exitoso, nunca se edita ni se borra. Sin ruta ni UI para consultarlo en esta rebanada más allá de lo que pida el cliente después (queda disponible para consulta directa a BD o un trabajo futuro de UI).

- **`notificacion_service.py` — firmas que ganan un parámetro `canal`:**
  - `obtener_texto_actual(session, evento, motivo=None, canal=CanalNotificacion.SMS)` — gana `canal` como parámetro con default `SMS`, pero SIGUE devolviendo solo `texto` (`str`), nunca una tupla — personalizado si existe fila para `(evento, motivo, canal)`, si no el default de código. El asunto de Email se consulta aparte con `obtener_asunto_actual(session, evento, motivo=None)` (implícitamente `canal=EMAIL`).
  - `guardar_plantilla(session, evento, motivo, texto, canal=CanalNotificacion.SMS, asunto=None)` — `canal`/`asunto` van DESPUÉS de `texto`, no antes, para preservar la llamada posicional que ya hace `admin.py`. Crea o actualiza la fila `(evento, motivo, canal)` (mismo patrón de reintento ante `IntegrityError` de carrera que ya existe), y además inserta la fila correspondiente en `plantillas_notificacion_historial` con el texto/asunto anterior (de la fila si existía, o `None` si es la primera vez) y el nuevo.
  - `construir_mensaje(session, evento, paquete)` (usado por el envío real de SMS vía `preparar_notificacion`) se actualiza para buscar explícitamente `canal=CanalNotificacion.SMS` — el comportamiento del envío real de SMS no cambia en absoluto.
  - `plantilla_por_defecto` / `PLANTILLAS_DEFAULT` / `_ANUNCIADO_DEFAULT` se reestructuran para tener un texto por `(evento, motivo, canal)` — el default de Email y WhatsApp para cada evento **reutiliza el mismo contenido informativo que el default actual de SMS** (mismo mensaje, sin re-redactar desde cero); se agrega un diccionario paralelo de asuntos por defecto para Email (ej. "Tu paquete está en portería", "Tu paquete fue entregado", etc., uno por evento/motivo).

- **Nuevo módulo de layout de Email** (ej. `app/domain/plantilla_email_html.py`): una función pura `envolver_html(asunto, cuerpo_texto) -> str` que produce el HTML con el layout de marca fijo (logo de Papyrus, enlaces a los sitios de la empresa) alrededor del cuerpo ya resuelto. Esta misma función es la que usará el envío real de Email el día que se conecte (reutiliza `SmtpEmailSender`, ya verificado funcionando en producción) — no se duplica el layout entre "vista previa" y "envío real".

- **`/administracion/notificaciones` (misma ruta, misma dependencia `require_admin`):** el template se rediseña para mostrar 7 grupos (uno por evento/motivo) con 3 pestañas cada uno (SMS / Email / WhatsApp). La pestaña de Email incluye el campo Asunto y una vista previa en vivo (actualizada del lado del cliente o vía submit parcial — decisión de implementación libre para quien construya, mientras el resultado visual sea "veo el correo ya armado con datos de ejemplo antes de guardar"). Las pestañas de SMS y WhatsApp mantienen el formato actual: textarea + lista de variables disponibles, sin resolver.

## Testing Decisions

- Los tests solo verifican comportamiento observable (qué devuelve una función pública, qué responde una ruta HTTP), no implementación interna — mismo criterio que el resto del repo.
- **Seam de dominio** — extender `tests/data_model/test_notificacion_service.py` (o agregar `test_plantilla_notificacion_multicanal.py` junto a él, prior art más cercano: `tests/data_model/test_preferencia_notificacion.py`):
  - Guardar una plantilla de `canal=EMAIL` para un evento no afecta el texto vigente de `canal=SMS` del mismo evento/motivo (y viceversa).
  - Sin plantilla personalizada para un `(evento, motivo, canal)`, `obtener_texto_actual` devuelve el default de ese canal — y el default de Email/WhatsApp coincide en contenido con el default de SMS del mismo evento.
  - `guardar_plantilla` inserta una fila en el historial en cada llamada, con `texto_anterior=None` la primera vez y con el valor previo real en la segunda.
  - `construir_mensaje` (usado por el envío real de SMS) sigue devolviendo exactamente lo mismo que antes de esta rebanada — no se rompe el comportamiento de envío ya verificado en producción.
  - `envolver_html(asunto, cuerpo_texto)` incluye el asunto, el cuerpo con sus placeholders ya resueltos, y contiene el logo y los enlaces esperados (aserción sobre presencia de esos elementos en el HTML, no sobre el markup exacto).
- **Seam web** — extender `tests/web/test_admin_notificaciones.py` (mismo patrón de `_login_admin`/`_login_operador` ya presente en el archivo):
  - Gate sin cambios: sin sesión redirige a `/ingresar`; `OPERADOR` recibe 403; solo `ADMIN` accede — mismas aserciones que ya existen, repetidas contra la pantalla rediseñada.
  - La pantalla muestra las 3 pestañas por cada uno de los 7 eventos/motivos.
  - Guardar el texto de la pestaña Email de un evento persiste asunto + texto, y no altera lo guardado en la pestaña SMS del mismo evento.
  - La vista previa de Email refleja el texto recién escrito ya resuelto con datos de ejemplo (no placeholders sin resolver).

## Out of Scope

- Conectar el envío real de Email o WhatsApp para eventos de paquete — esta rebanada es solo el sistema de contenido/plantillas. El cliente indicará más adelante cuáles canales activar; ese trabajo es aparte.
- Elegir o integrar un proveedor de WhatsApp Business (Twilio, Meta Cloud API, 360dialog, etc.).
- Adoptar el formato real de plantilla de WhatsApp que exigirá Meta (variables numeradas `{{1}}`, `{{2}}`, categoría `UTILITY`/`MARKETING`, aprobación) — se reevalúa cuando haya proveedor elegido.
- El canal `LLAMADA` (ya existe en `CanalNotificacion` como preferencia, pero no se pidió ni se modela en este sistema de plantillas).
- Cualquier flag de "activo"/habilitación por canal a nivel de plantilla — es una decisión de negocio que el cliente tomará después; no se modela nada de eso ahora.
- UI para revertir un cambio desde el historial — el historial es solo de consulta en esta rebanada.
- Ampliar quién puede editar plantillas más allá de `ADMIN`.
- Backfill de contenido personalizado: no se auto-generan versiones de Email/WhatsApp basadas en las personalizaciones SMS que el cliente ya haya guardado — el default de código es el mismo texto para los 3 canales, pero si el cliente ya personalizó el SMS de un evento, esa personalización NO se copia automáticamente a Email/WhatsApp (seguirían mostrando el default hasta que se editen explícitamente).

## Further Notes

- Precedentes directos en este repo: `.scratch/notificaciones-anunciado-plantillas` (creó `plantillas_notificacion` y la pantalla admin original) y `.scratch/preferencia-notificacion-matriz` (introdujo `CanalNotificacion` con SMS/EMAIL/LLAMADA/WHATSAPP como preferencia de Persona, aunque solo SMS envía de verdad). Este trabajo es el punto donde el resto de esos canales empieza a tener contenido real, sin todavía tener envío.
- `ADR-0007` (persona-telefono-o-whatsapp) ya reconoce WhatsApp como identidad de primera clase en el dominio ("una Persona solo-WhatsApp... no puede recibir avisos automáticos todavía... depende de un canal de envío por WhatsApp que este rebuild no construye todavía") — este trabajo no contradice esa ADR: sigue sin construir el canal de envío, solo el contenido que ese canal usará el día que exista.
- El envío de Email ya fue verificado extremo a extremo contra `test.papyrus.com.co` el 2026-08-26 (correo de prueba real entregado vía `SmtpEmailSender`/MXroute) — cuando el cliente decida activar Email para eventos de paquete, la infraestructura de envío ya está probada; solo falta cablear `notificar_evento` a un segundo `NotificationSender`-equivalente para Email, fuera de esta rebanada.
