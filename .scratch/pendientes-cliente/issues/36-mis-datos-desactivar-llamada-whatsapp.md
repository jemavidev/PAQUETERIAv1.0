# 36 — `/mis-datos`: desactivar canales Llamada y WhatsApp en preferencias

**Pedido original (cliente):** "Para las notificaciones, lo relacionado a
Llamada y WhatsApp, debe estar desactivado, ya que no tiene implementacion
para estas."

**Status:** verificado

## Implementación

- `customer_verify.py`: `_CANALES_SIN_PROVEEDOR = {LLAMADA, WHATSAPP}`, pasado
  al template como `canales_sin_proveedor`. El servidor tampoco confía solo
  en el HTML deshabilitado -- el cálculo de `activos` en el POST excluye
  esos 2 canales aunque alguien fuerce el request crudo.
- `customer/verify.html`: esas 2 columnas se renderizan con checkboxes
  `disabled` (sin `name`, así que nunca se envían) y una etiqueta
  "(próximamente)" bajo el nombre del canal.
- Test nuevo `test_llamada_y_whatsapp_no_se_pueden_activar` confirma que ni
  forzando el POST se activan. `test_marcar_un_canal_lo_activa_para_ese_evento`
  (existente) se movió de WhatsApp a Email, que sigue editable.
