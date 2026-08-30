# 211 — `/mis-datos` tab Datos: gestionar el WhatsApp propio

**Pedido original (cliente):** "En este Tab de datos también debería ser
posible gestionar el usuario de whatsapp." (tab de "Editar datos propios",
hoy solo gestiona teléfono propio).

**Status:** implementado

## Implementación

`update_datos_personales` (domain) ya soportaba `whatsapp_usuario` con
semántica de 3 estados -- hasta ahora solo lo pasaba `/residentes/{id}`
(staff). `customer_verify.py::customer_verify_submit` ahora también lo
pasa (mismo patrón que el staff: el form siempre manda el campo, `""`
borra a propósito), y `verify.html` gana el input WhatsApp en "Datos
personales", con su propio `error_whatsapp`.

