# 05 — Formulario de credenciales en la pantalla + auditoría de campo cambiado

**What to build:** la parte de `/administracion/proveedores` donde Jesús realmente
escribe una credencial nueva (rotar un token, cargar una API key) — cierra el pedido
original completo: gestionar TODA la configuración de proveedores desde formularios,
sin editar `.env` a mano por SSH.

Ver `.scratch/administracion-proveedores/spec.md` (User Stories 6-11, 13, 14;
Implementation Decisions "Formulario de credenciales").

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [ ] Cada proveedor muestra un campo de texto por variable declarada en su catálogo
      (ticket 01), enmascarado (`type=password` o equivalente) para los marcados
      como secretos.
- [ ] Un campo de credencial ya configurada muestra un placeholder fijo (ej. "••••
      configurado") — NUNCA el valor real; la pantalla ni siquiera necesita poder
      leerlo, basta con saber que la variable está seteada (mismo criterio que
      `.configurado()` hoy).
- [ ] Dejar un campo vacío al guardar significa "no cambiar esa credencial" — solo
      los campos con contenido nuevo se incluyen en la llamada al mecanismo del
      ticket 04.
- [ ] Guardar espera la confirmación real (éxito/fallo) del mecanismo SSH antes de
      responder — nunca un "guardado" optimista. Si falla, se muestra el error tal
      cual y la credencial anterior sigue activa.
- [ ] Un cambio de credencial exitoso queda en el historial de auditoría con SOLO el
      nombre del campo que cambió (canal, proveedor, campo, quién, cuándo) — nunca el
      valor, ni antes ni después.
- [ ] Después de guardar, el botón "Enviar prueba" ya existente en
      `/administracion/notificaciones` sigue siendo la vía para confirmar en vivo que
      la credencial nueva funciona — no se construye un mecanismo de prueba aparte.
- [ ] Tests de ruta (extienden `tests/web/test_admin_proveedores.py`): guardar con el
      mecanismo SSH mockeado — éxito confirma y queda en el historial (solo el nombre
      del campo, nunca el valor); fallo muestra error visible sin cambios en el
      historial ni en el estado "configurado" percibido; campo vacío no dispara
      ninguna llamada al mecanismo SSH.
