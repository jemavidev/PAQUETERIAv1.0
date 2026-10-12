# 05 — Enviar SMS y "Último SMS"

**What to build:** Cada fila gana un botón "Enviar SMS" que manda el mensaje elegido a ese cliente solo cuando el Admin lo toca. Sale
por la misma cadena de proveedores que los avisos automáticos (AWS SNS primero). La página espera la respuesta real
sin recargar: si sale, la fila muestra el nuevo "Último SMS: <nombre del mensaje> · <fecha y hora>"; si falla, un aviso
rojo y no cuenta. Cada fila muestra su último aviso especial enviado (cualquier mensaje), o "Sin avisos enviados". No
hay confirmación ni bloqueo de reenvío.

Ver spec: Implementation Decisions (EnvioAvisoEspecial, Registro de envíos SMS, Envío síncrono, Interacción sin
recarga, Texto del SMS) y User Stories 16-19, 30-40.

**Blocked by:** 04 — Selector de mensaje y botón de WhatsApp

**Status:** ready-for-agent

- [ ] POST por fila que envía de forma síncrona con el `NotificationSender` de la app; el texto lleva `{nombre}` y `{codigos}` resueltos y la normalización sin tildes de los SMS
- [ ] Envío exitoso: se crea el registro de envío (persona, mensaje, nombre del mensaje copiado, Admin, fecha) y la fila actualizada muestra el nuevo Último SMS
- [ ] Envío fallido: aviso rojo en la fila, sin registro de envío nuevo
- [ ] Cada intento (exitoso o fallido) se registra en `registros_sms` con el tipo nuevo `AVISO_ESPECIAL`
- [ ] Con JS, el botón hace fetch y reemplaza el fragmento de la fila ("Enviando…" mientras espera); sin JS, POST normal con redirección a la vista (Post/Redirect/Get)
- [ ] "Último SMS" por cliente con el envío más reciente de cualquier mensaje, en hora de Colombia y formato amigable; "Sin avisos enviados" si no hay
- [ ] Un mensaje eliminado después de enviarse sigue mostrando su nombre en el Último SMS
- [ ] Enviar con un mensaje eliminado o inexistente responde un error claro y no envía nada
- [ ] Reenviar a un cliente con envío reciente funciona sin confirmación
- [ ] Pruebas por HTTP reemplazando `get_notification_sender` por un sender falso (éxito y falla)
