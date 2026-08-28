# 03 — Botón de WhatsApp deshabilitado + rechazo del servidor

**What to build:** La pestaña WhatsApp de cada modal muestra el mismo control de "Enviar prueba" que SMS/Email, pero deshabilitado con una nota explicando que el canal no está configurado todavía — visible siempre, nunca oculto, para que quede claro de un vistazo cuál canal está listo para producción y cuál no. Un intento de forzar el envío manipulando el form directamente se rechaza también del lado del servidor, no solo deshabilitando el botón en el HTML.

**Blocked by:** 02 (reusa la ruta de envío de prueba y el patrón de "canal configurado → botón habilitado/deshabilitado" que introduce ese ticket).

**Status:** ready-for-agent

- [ ] La pestaña WhatsApp de cada modal muestra el campo de destino + botón "Enviar prueba" deshabilitado, con una nota visible explicando que WhatsApp no tiene proveedor configurado todavía.
- [ ] El botón deshabilitado no impide seguir editando y guardando el texto de la pestaña WhatsApp normalmente — solo el envío real queda bloqueado.
- [ ] Un POST directo a la ruta de envío de prueba con `canal=WHATSAPP` se rechaza en el servidor con un error explícito de "canal no configurado", ANTES de intentar ningún envío — el servidor no confía en que el botón esté deshabilitado en el HTML (mismo criterio que ya aplica esta pantalla para `evento`/`canal` inválidos manipulados a mano).
- [ ] Ningún sender (SMS/Email) recibe nada como resultado de un intento de prueba por WhatsApp.
- [ ] El día que exista un proveedor real de WhatsApp, el único cambio esperado es que el chequeo de "configurado" empiece a devolver verdadero, sin tocar el resto del flujo — conectar ese proveedor queda fuera de alcance de este ticket.
