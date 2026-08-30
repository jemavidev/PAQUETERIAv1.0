# 221 — `/mis-datos` tab Notificaciones: activar columna WhatsApp, a la derecha de SMS

**Pedido original (cliente):** "necesito que en el tab de notificaciones la
columna de whatsapp esté activada, y a la derecha de sms, todas las
opciones deben estar activadas."

**Status:** implementado

## Implementación

Alcance: solo `/mis-datos` (cliente) -- `/residentes/{id}` (staff) tiene su
propia copia de `_CANALES_SIN_PROVEEDOR` y se dejó intacta a propósito, sin
que se haya pedido.

- `customer_verify.py`: `_CANALES_SIN_PROVEEDOR` pierde `WHATSAPP` (columna
  ya no deshabilitada/"próximamente"); `canales` en `_contexto_base` pasa de
  `list(CanalNotificacion)` (orden SMS/EMAIL/LLAMADA/WHATSAPP) a una lista
  explícita `[SMS, WHATSAPP, EMAIL, LLAMADA]` -- WhatsApp inmediatamente a
  la derecha de SMS.
- `preferencia_notificacion_service.py::_default_activo` (compartido):
  WhatsApp activo por default en los 4 eventos (antes solo SMS×ANUNCIADO).
  Como es domain-level, aplica también a `/residentes/{id}`, pero ahí la
  columna sigue deshabilitada así que no cambia nada visible -- el checkbox
  deshabilitado de "próximamente" no lee `matriz` para su estado.
- `tests/data_model/test_preferencia_notificacion.py`: 3 tests actualizados
  para el nuevo default (codificaban la política vieja "todo inactivo salvo
  SMS×ANUNCIADO").

