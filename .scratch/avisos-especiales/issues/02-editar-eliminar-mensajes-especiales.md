# 02 — Editar y eliminar mensajes especiales

**What to build:** El Admin puede actualizar un mensaje especial cuando hay información nueva (cambiar el nombre o el texto) y eliminar
los que ya no sirven, con confirmación. Cada cambio queda en el historial. Eliminar es lógico: el mensaje desaparece
de la lista (y luego del selector), pero sigue existiendo para que los envíos viejos conserven su nombre.

Ver spec: User Stories 58-61.

**Blocked by:** 01 — Crear mensajes especiales en Notificaciones

**Status:** ready-for-agent

- [ ] Editar nombre y/o texto desde un modal con la misma vista previa y conteo del ticket 01
- [ ] Las mismas validaciones del 01 al editar (nombre único, variables permitidas, texto obligatorio)
- [ ] Cada edición queda en el historial con usuario, fecha, nombre/texto anterior y nuevo
- [ ] Eliminar pide confirmación; el mensaje deja de aparecer en la lista y queda registrado en el historial
- [ ] La eliminación es lógica (no se borra la fila); un nombre eliminado puede volver a usarse en un mensaje nuevo
- [ ] Pruebas por HTTP
