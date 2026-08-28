# 02 — Enviar mensaje de prueba por SMS y Email

**What to build:** Desde cada modal de plantilla en `/administracion/notificaciones` (issue 203, `.scratch/pendientes-cliente`), las pestañas SMS y Email ganan un campo de destino + botón "Enviar prueba" que dispara un envío REAL de la plantilla ya guardada de ese canal, con las variables (`{recipient_name}`, `{access_code}`, `{motivo}`) resueltas a datos de ejemplo legibles. El destino llega pre-llenado con el teléfono/correo del propio admin logueado (editable antes de enviar). El envío es síncrono — la página espera la respuesta real del proveedor y recarga mostrando un toast de éxito o de error; nunca un envío best-effort silencioso como el de un evento real de Paquete.

**Blocked by:** 01 (el pre-llenado del destino de SMS usa el teléfono del admin, que recién existe tras ese ticket).

**Status:** ready-for-agent

- [ ] Cada pestaña SMS/Email de cada modal evento/motivo tiene un campo de destino (pre-llenado con el teléfono/correo del admin logueado, vacío si no lo tiene guardado) y un botón "Enviar prueba".
- [ ] El botón envía la plantilla TAL COMO QUEDÓ GUARDADA en ese canal (nunca un texto sin guardar en el textarea que se esté editando).
- [ ] Las variables de la plantilla se resuelven con datos de ejemplo (mismos que usaba el preview de Email ya retirado) — el mensaje de prueba llega legible, nunca con placeholders sin resolver.
- [ ] SMS envía de verdad a través de la cadena de proveedores ya existente (failover SNS→LIWA→Twilio); Email envía de verdad a través del SMTP ya existente, con el cuerpo envuelto en el mismo layout de marca que usaba el preview retirado — mismo transporte que ya usa recuperación de contraseña.
- [ ] Al enviar, la página espera la respuesta real y recarga mostrando un toast de éxito (con el destino) o de error — una falla real del proveedor SE MUESTRA como error, nunca se traga en silencio.
- [ ] Destino vacío al presionar "Enviar prueba" se rechaza con un error claro, sin intentar ningún envío.
- [ ] `evento`/`canal` inválidos (manipulación directa del form) se rechazan igual que ya lo hace "Guardar" en esta pantalla.
- [ ] Enviar una prueba no modifica el texto guardado de ningún canal ni deja rastro en el historial de auditoría de ediciones de plantillas.
- [ ] Solo ADMIN puede enviar pruebas; un OPERADOR sigue recibiendo 403 en toda la pantalla, incluida esta acción nueva.
- [ ] El botón de cada canal (SMS/Email) aparece habilitado solo si ese canal tiene al menos un proveedor configurado en el sistema; si no, aparece deshabilitado con una nota explicando por qué — este es el mismo patrón que reutilizará el ticket de WhatsApp.
- [ ] En `WEB_ENV=staging`, el envío de prueba sigue protegido por el override fail-closed ya existente (todo envío real se redirige al destino de override configurado, o no sale si falta) — no se crea un camino de envío paralelo que lo esquive.
