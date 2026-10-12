# 04 — Selector de mensaje y botón de WhatsApp

**What to build:** Arriba de la lista, el Admin elige cuál mensaje especial va a mandar y ve su vista previa. Cada fila gana un botón
de WhatsApp que abre el chat del cliente con ese mensaje ya escrito, con `{nombre}` y `{codigos}` resueltos para ese
cliente. La elección se conserva en la URL. Si no hay mensajes creados, la vista lo dice y enlaza a Notificaciones.

Ver spec: User Stories 25-29, 46, 48-51.

**Blocked by:** 01 — Crear mensajes especiales en Notificaciones; 03 — Vista "Avisos especiales": la lista de clientes

**Status:** ready-for-agent

- [ ] Selector con los mensajes no eliminados; sin elección, se usa el primero alfabéticamente
- [ ] La elección va en la URL (`?mensaje=<id>`) y se conserva al recargar
- [ ] Vista previa del mensaje elegido con datos de ejemplo y conteo de caracteres
- [ ] Botón WhatsApp por fila con los mismos enlaces celular/escritorio del resto de la app y `text=` con el mensaje resuelto para ese cliente (`{codigos}` = sus códigos en la lista, separados por coma)
- [ ] Cliente sin teléfono ni usuario de WhatsApp: botón apagado con el motivo
- [ ] Sin mensajes creados: aviso con enlace a "Mensajes especiales" y botones de envío apagados
- [ ] Tocar WhatsApp no llama al servidor ni deja registro
- [ ] Pruebas por HTTP
