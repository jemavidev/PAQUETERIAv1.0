# Enviar mensaje de prueba desde /administracion/notificaciones

Fuente: conversación en vivo 2026-08-28 (grilling), pedido directo de Jesús (quien opera este repo). Extiende `.scratch/plantillas-notificacion-multicanal` (sistema de plantillas multicanal) y `.scratch/pendientes-cliente` issues 203 (modal por fila) y 204 (se quitó el preview de Email de esta misma pantalla, en esta misma sesión, porque un envío de prueba real es "más realista").

**Status:** ready-for-agent

## Problem Statement

`/administracion/notificaciones` permite editar el texto de cada plantilla (SMS/Email/WhatsApp × evento/motivo), pero no hay forma de comprobar cómo llega ese mensaje de verdad — antes existía un preview estático de Email con datos de ejemplo (ya retirado, issue 204), y SMS/WhatsApp nunca tuvieron ni eso. El ADMIN edita a ciegas: guarda un texto y confía en que se vea/lea bien cuando un residente lo reciba, sin poder confirmarlo hasta que ocurra un evento real de Paquete. Además, de los 3 canales que hoy tienen contenido editable, solo SMS tiene envío real conectado a eventos de Paquete — Email tiene transporte verificado en producción pero sin cablear a este flujo, y WhatsApp no tiene ningún proveedor conectado — y hoy no hay ninguna señal en la pantalla de cuál de los 3 está realmente listo para enviar.

## Solution

Cada pestaña de canal (SMS/Email/WhatsApp), dentro del modal de cada fila evento/motivo, gana un control "Enviar prueba": un campo de destino (teléfono para SMS/WhatsApp, correo para Email) más un botón que dispara un envío REAL de la plantilla ya guardada de ese canal, con las variables (`{recipient_name}`, `{access_code}`, `{motivo}`) resueltas con datos de ejemplo — mismos datos que usaba el preview retirado. El campo de destino llega pre-llenado con el dato de contacto del propio ADMIN (nuevo: el perfil de Usuario en `/mi-sesion` gana teléfono y WhatsApp propios, junto al email que ya tiene), editable antes de enviar. Si el canal no tiene ningún proveedor de envío configurado en el sistema (WhatsApp, hoy) el control se ve igual pero deshabilitado, con una nota explicando que ese canal no está disponible todavía — nunca oculto, para que quede siempre visible cuál canal está listo y cuál no. El envío es el mismo patrón que ya usa "Guardar" en esta pantalla: un POST normal, la página espera la respuesta real del proveedor y recarga mostrando un toast de éxito o de error — a propósito SÍNCRONO y sin tragarse errores (a diferencia del envío best-effort/background de una notificación real de Paquete), porque el punto de una prueba es saber si de verdad llegó o no.

## User Stories

1. Como ADMIN, quiero un botón "Enviar prueba" en cada pestaña de canal de cada evento/motivo, para confirmar cómo llega un mensaje antes de confiar en que un residente lo reciba bien.
2. Como ADMIN, quiero que la prueba envíe la plantilla TAL COMO QUEDÓ GUARDADA (no un borrador sin guardar que tenga a medio escribir en el textarea), para que la prueba refleje exactamente lo que un residente recibiría hoy.
3. Como ADMIN, quiero que las variables de la plantilla (`{recipient_name}`, `{access_code}`, `{motivo}`) se resuelvan con datos de ejemplo legibles en el mensaje de prueba, para no recibir un mensaje con placeholders sin resolver que no me diga nada sobre cómo se ve de verdad.
4. Como ADMIN, quiero un campo para indicar a qué teléfono/correo mandar la prueba, para poder probar con cualquier destino, no solo el mío.
5. Como ADMIN, quiero que ese campo venga pre-llenado con mi propio teléfono/WhatsApp/correo, para no tener que escribirlo cada vez que pruebo.
6. Como ADMIN, quiero poder guardar mi propio teléfono y WhatsApp en `/mi-sesion` (junto al correo que ya puedo editar ahí), para que ese pre-llenado tenga de dónde salir.
7. Como ADMIN, si no he guardado mi teléfono/WhatsApp todavía, quiero que el campo de destino simplemente aparezca vacío (no un error), para poder escribirlo a mano igual la primera vez.
8. Como ADMIN, quiero que el botón de prueba de un canal sin proveedor configurado (WhatsApp hoy) se vea deshabilitado con una nota explicando por qué, para saber de un vistazo cuáles canales están realmente listos para producción y cuáles no, sin tener que adivinar ni preguntar.
9. Como ADMIN, quiero que ese mismo botón deshabilitado NO oculte la pestaña de WhatsApp ni impida seguir editando y guardando su texto, para poder dejar el contenido listo de antemano aunque el envío todavía no exista.
10. Como ADMIN, quiero que al enviar una prueba la página espere la respuesta real del proveedor (no una confirmación optimista), para saber de verdad si el mensaje salió o falló.
11. Como ADMIN, quiero un toast de éxito claro (con el destino al que se envió) cuando la prueba sale bien.
12. Como ADMIN, quiero un toast de error claro cuando la prueba falla (proveedor caído, destino inválido, canal sin configurar), para saber que NO llegó en vez de asumir que sí.
13. Como ADMIN, quiero que un destino vacío al presionar "Enviar prueba" se rechace con un error claro, para no descubrir el problema recién en el proveedor.
14. Como ADMIN, quiero que enviar una prueba de un canal no afecte ni el texto guardado de ese canal ni el de los otros 2 canales del mismo evento, porque una prueba es una lectura, no una edición.
15. Como ADMIN, quiero que solo el rol ADMIN pueda enviar pruebas, igual que hoy solo ADMIN edita plantillas.
16. Como OPERADOR (no-ADMIN), al intentar acceder a `/administracion/notificaciones` (incluida cualquier acción de prueba) sigo recibiendo 403, sin cambios sobre el comportamiento actual.
17. Como desarrollador, quiero que el envío de prueba de Email reutilice el `SmtpEmailSender`/`get_email_sender()` ya verificado en producción (recuperación de contraseña), para no mantener una segunda integración SMTP redundante.
18. Como desarrollador, quiero que el envío de prueba de SMS reutilice `get_notification_sender()` (la cadena de failover SNS→LIWA→Twilio) tal cual existe hoy, sin una ruta de envío paralela.
19. Como desarrollador, quiero que en `WEB_ENV=staging` el envío de prueba SIGA protegido por el override fail-closed existente (`StagingOverrideSender`/`StagingOverrideEmailSender` — todo mensaje real sale hacia `SMS_OVERRIDE_NUMBER`/`EMAIL_OVERRIDE_ADDRESS`, o no sale si esa variable falta), para no crear un segundo camino de envío que se salte esa protección — aunque eso signifique que en staging la prueba no llega literalmente al destino que el ADMIN escribió, sino al override, igual que cualquier otro envío real de esa pantalla.
20. Como desarrollador, quiero que un intento de probar el canal WhatsApp se rechace también del lado del servidor (no solo deshabilitando el botón en el HTML), porque el servidor no confía en la forma del POST — mismo criterio que ya aplica esta pantalla para `evento`/`canal` inválidos manipulados a mano.
21. Como desarrollador, quiero que enviar una prueba NO dispare ningún envío real de evento de Paquete ni deje rastro en `plantillas_notificacion_historial` (esa tabla es del historial de EDICIONES, no de envíos), para no mezclar dos conceptos distintos.
22. Como cliente final (fuera de alcance, pero relevante a futuro), no me ve afectado por esta rebanada de ninguna forma — es una herramienta interna de ADMIN, ningún mensaje de prueba llega jamás a un residente real.

## Implementation Decisions

- **`Usuario` (dominio, `usuario.py`) gana dos columnas nuevas**: `telefono` (`String`, nullable) y `whatsapp` (`String`, nullable) — contacto propio del staff, SIN relación con el modelo de identidad de Persona (Teléfono/WhatsApp como llave, ADR-0003/ADR-0007): no hay unicidad, no habilitan login/OTP, no son la "identidad" del Usuario (eso sigue siendo el `email`). Migración Alembic nueva que agrega ambas columnas nullable — sin backfill (todo Usuario existente arranca con ambas en `NULL`).
- **`editar_mi_perfil` (`staff_service.py`) gana `telefono`/`whatsapp` como parámetros opcionales**, junto al `nombre` que ya edita — mismo criterio de autoservicio ya documentado ahí (cualquier staff edita SOLO lo suyo, sin campo de rol). Sin validación de formato más allá de lo que ya haga `nombre` (trim; vacío se guarda como `NULL`, no como cadena vacía) — no se exige que el teléfono tenga un formato E.164 ni que el WhatsApp sea distinto del teléfono.
- **`POST /mi-sesion/editar` (`auth.py`) gana los mismos dos campos de form**, pasándolos tal cual a `editar_mi_perfil`. `auth/me.html` gana dos inputs de texto (teléfono, WhatsApp) junto al de nombre que ya existe, mismo patrón visual.
- **Nueva función en `notificacion_service.py`** (nombre sugerido: `mensaje_de_prueba(session, evento, motivo, canal) -> tuple[str, str | None]`, cuerpo/asunto): reutiliza `obtener_texto_actual` + `obtener_asunto_actual` (plantilla YA GUARDADA, nunca un texto sin persistir) y resuelve las variables con `variables_ejemplo(motivo)` + `resolver_plantilla` — mismas piezas que usaba `_preview_html_de` (retirada en issue 204), pero ahora vive en el dominio en vez de la capa web, porque el envío real también la necesita, no solo una vista.
- **Nueva ruta `POST /administracion/notificaciones/probar`** (`admin.py`, `require_admin`, endpoint separado de `POST /administracion/notificaciones` que usa "Guardar" — evita mezclar dos acciones con distintos campos requeridos en un mismo handler). Recibe `evento`, `motivo`, `canal` (hidden, mismos valores que ya viajan en el form de Guardar de esa pestaña) y `destino` (el input nuevo). Validaciones servidor (mismo criterio que la validación existente de `evento`/`canal` en esta ruta — "el servidor no confía en la forma del POST"):
  - `evento`/`canal` inválidos → error genérico, igual que hoy.
  - `destino` vacío → error, sin marcar fila (mismo patrón que ya existe para "texto no puede quedar vacío").
  - `canal == WHATSAPP` (o cualquier canal sin proveedor configurado) → error explícito de "canal no configurado", ANTES de intentar ningún envío.
  - Éxito de validación → resuelve el mensaje con `mensaje_de_prueba`, y envía SÍNCRONAMENTE (nunca vía `BackgroundTask`/`enviar_en_segundo_plano` — a propósito distinto del envío best-effort de un evento real de Paquete):
    - `SMS`/`WHATSAPP`-cuando-exista: `sender: NotificationSender = Depends(get_notification_sender)`, `sender.enviar(destino, texto)`.
    - `EMAIL`: `sender: EmailSender = Depends(get_email_sender)`, cuerpo HTML vía `envolver_html(asunto, texto, public_base_url())` (misma función que usaba el preview retirado), `sender.enviar(destino, asunto, texto, cuerpo_html)`.
  - Una excepción real del `sender.enviar` (proveedor caído, destino rechazado) SE PROPAGA a un toast de error — a diferencia de `notificar_evento`, que la traga (best-effort). Esta ruta necesita saber si falló para poder avisarle al ADMIN.
  - Respuesta (éxito o error): re-renderiza `admin/notificaciones.html` con `_filas_plantillas(db)` + un toast, reabriendo el modal/pestaña de la fila probada (mismo mecanismo ya usado para reabrir tras Guardar/error, extendido para distinguir "resultado de una prueba" de "resultado de un guardado").
- **"¿Está configurado este canal?" por fila/pestaña** (para pintar el botón habilitado o no): SMS → `sns_sender.sns_habilitado() or liwa_sender.configurado() or twilio_sender.configurado()` (mismos checks que ya usa `_sender_base()` en `web/notifications.py`); EMAIL → `smtp_email_sender.configurado()`; WHATSAPP → `False` siempre, hasta que exista un proveedor real (no hay ningún módulo `whatsapp_sender.py` hoy). Este chequeo se calcula en `admin.py` al armar `_canales_de` (un booleano nuevo por canal, ej. `"configurado": ...`) y el template lo usa para deshabilitar el botón + mostrar la nota.
- **Campo de destino pre-llenado**: `admin.py` pasa el `usuario.telefono`/`usuario.whatsapp`/`usuario.email` del admin en sesión (`require_admin`) al template, y cada input de destino nace con ese `value` (vacío si el campo del perfil es `NULL`) — el ADMIN puede sobreescribirlo libremente antes de enviar.
- **Sin cambios en `notificar_evento`/`preparar_notificacion`/`plantillas_notificacion_historial`**: el envío de prueba es una acción de LECTURA sobre la plantilla ya guardada, nunca dispara el flujo de eventos de Paquete ni escribe en el historial de ediciones.

## Testing Decisions

Los tests solo verifican comportamiento observable (qué devuelve una función pública, qué responde una ruta HTTP), no implementación interna — mismo criterio que el resto del repo.

- **Seam de dominio** — extender `tests/data_model/test_notificacion_service.py`:
  - `mensaje_de_prueba` devuelve el texto (y asunto, para EMAIL) de la plantilla ya guardada para `(evento, motivo, canal)`, con variables resueltas a datos de ejemplo (`Juan Pérez`, `AB12CD`, motivo legible) — nunca placeholders sin resolver.
  - Sin plantilla personalizada, devuelve el default de ese canal (mismo criterio que `obtener_texto_actual`).
  - Para SMS/WhatsApp, el asunto devuelto es `None`.
- **Seam web — envío de prueba** — extender `tests/web/test_admin_notificaciones.py`, reusando el patrón de `dependency_overrides` que ya usa `tests/web/test_password_reset.py` (`client.app.dependency_overrides[get_notification_sender] = lambda: sender_falso`, ídem `get_email_sender`, y assert sobre `sender_falso.enviados` — nunca red real):
  - Gate: sin sesión redirige a `/ingresar`; `OPERADOR` recibe 403 (mismas aserciones que ya existen para esta pantalla, repetidas contra la ruta nueva).
  - Probar SMS con un `NotificationSender` falso: `enviados` recibe `(destino, texto_resuelto)`; el texto coincide con la plantilla YA GUARDADA (no un texto distinto pasado a mano sin guardar antes).
  - Probar Email con un `EmailSender` falso: `enviados` recibe destino/asunto/cuerpo resueltos + el cuerpo HTML contiene el logo/enlaces de marca (`envolver_html`).
  - Probar WhatsApp devuelve error (canal no configurado) SIN que ningún sender reciba nada — verificable incluso sin proveedor real: el mock de `NotificationSender` debe quedar con `enviados == []`.
  - Destino vacío → error, sin llamar al sender.
  - `evento`/`canal` inválidos (manipulación directa del form) → error, mismo patrón que ya existe para Guardar.
  - Una excepción del sender (simulada con un `NotificationSender` falso que lanza) se traduce en un toast de error observable en la respuesta — a diferencia de `notificar_evento`, NO se traga en silencio.
  - El botón de "Enviar prueba" de WhatsApp aparece deshabilitado en el HTML (verificable por un atributo `disabled` o equivalente) cuando no hay proveedor configurado; SMS/Email lo tienen habilitado en el entorno de test SI se fuerza su `configurado()`/`sns_habilitado()` a verdadero (o se documenta que en el entorno de test, sin esas env vars, TAMBIÉN aparecen deshabilitados — a decidir por quien implemente, consistente con que el entorno de test nunca tiene esas credenciales configuradas).
  - El campo de destino viene pre-llenado con `usuario.telefono`/`usuario.whatsapp`/`usuario.email` cuando el admin logueado los tiene guardados, vacío si no.
- **Seam web — perfil del admin** — extender `tests/web/test_auth.py`:
  - `POST /mi-sesion/editar` con `telefono`/`whatsapp` los persiste junto al `nombre`.
  - Dejar `telefono`/`whatsapp` vacíos al editar no rompe nada y los guarda como `NULL`.
  - Un OPERADOR (no solo ADMIN) puede editar su propio teléfono/WhatsApp, igual que ya puede editar su nombre (autoservicio, sin gate de rol).

## Out of Scope

- Conectar un proveedor real de envío de WhatsApp — esta rebanada solo dispone la UI (botón deshabilitado + validación servidor) para cuando exista; elegir/integrar un proveedor (Twilio, Meta Cloud API, 360dialog, etc.) es trabajo aparte, ya marcado fuera de alcance también en `.scratch/plantillas-notificacion-multicanal`.
- Cablear `notificar_evento` (el envío real de un evento de Paquete) a Email o WhatsApp — esta rebanada es SOLO la herramienta de prueba manual del ADMIN, no activa envío real de eventos. Sigue siendo trabajo aparte, tal como ya lo dejó fuera de alcance la spec anterior.
- Historial/auditoría de envíos de prueba (quién probó qué, cuándo) — no se pidió; a diferencia de `plantillas_notificacion_historial` (que audita EDICIONES), un envío de prueba no persiste ningún rastro.
- Rate limiting o límite de cuántas pruebas puede mandar un ADMIN — pantalla exclusiva de `ADMIN` autenticado, mismo nivel de confianza que el resto de `/administracion/`.
- Validación de formato de teléfono/WhatsApp en el perfil del admin (E.164, unicidad, etc.) — se guardan como texto libre, igual de permisivo que el resto de este perfil de autoservicio.
- Cualquier UI para que el ADMIN vea/gestione el estado de configuración de los proveedores (ej. una pantalla de "estado de canales") — el único lugar donde se refleja "configurado o no" en esta rebanada es el botón deshabilitado por canal dentro de cada modal.

## Further Notes

- Precedente directo: `.scratch/plantillas-notificacion-multicanal` construyó el contenido de los 3 canales sin envío real conectado, y explícitamente dejó anotado que Email "ya fue verificado extremo a extremo contra test.papyrus.com.co... correo de prueba real entregado vía SmtpEmailSender/MXroute" — esta rebanada es, en cierto sentido, exponer esa misma capacidad ya probada como una herramienta del ADMIN en vez de un experimento aislado.
- `ADR-0007` sigue sin construir un canal de envío de WhatsApp para Persona ("no puede recibir avisos automáticos todavía... depende de un canal de envío por WhatsApp que este rebuild no construye todavía") — esta rebanada no la contradice: el botón deshabilitado de WhatsApp es, de hecho, la manifestación visible en UI de esa misma ADR.
- Los nuevos campos `telefono`/`whatsapp` en `Usuario` son contacto propio del STAFF (para recibir sus propias pruebas), completamente distintos del Teléfono/WhatsApp de Persona que gobiernan ADR-0003/ADR-0007 (identidad de residente, login/OTP) — vale la pena que quien implemente elija el nombre de estas columnas de forma que no se confundan en el código con las de `Persona` (ej. evitar que un futuro lector piense que un Usuario ahora participa del modelo de identidad de Persona).
- El comportamiento fail-closed de `StagingOverrideSender`/`StagingOverrideEmailSender` en `WEB_ENV=staging` (invariante 6 de `CONTEXT.md`) se hereda gratis al reusar `get_notification_sender()`/`get_email_sender()` tal cual — nadie necesita reimplementarlo, pero vale la pena que el ADMIN sepa (documentado en la UI o no, a criterio de quien implemente) que en staging una prueba no llega al destino que escribió, sino al número/correo de override configurado.
