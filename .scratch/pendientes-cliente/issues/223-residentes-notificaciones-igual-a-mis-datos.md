# 223 — `/residentes` tab Notificaciones: igualar a `/mis-datos` (WhatsApp activo, orden de columnas)

**Pedido original (cliente):** "necesito que para la vista de /residentes
en el Tab de notificaciones hagas que se vea similar a la vista de
/mis-datos en el tab de notificaciones, esto con el fin de gestionar mejor
las notificaciones." (seguimiento de
[[221-mis-datos-notificaciones-activar-whatsapp]] -- ambas vistas se
diseñaron para reflejarse, quedó desactualizada tras ese cambio).

**Status:** implementado

## Implementación

`customers_manage.py`: mismos dos cambios ya hechos en `customer_verify.py`
para el issue 221 -- `_CANALES_SIN_PROVEEDOR` pierde `WHATSAPP` (columna ya
editable para ADMIN y OPERADOR, `canal_evento_editable` no la restringía) y
`canales` pasa a orden explícito `[SMS, WHATSAPP, EMAIL, LLAMADA]`. El texto
"SMS solo se puede activar para Anuncio..." se dejó intacto a propósito --
solo lo ve un OPERADOR (nunca un ADMIN, `eventos_bloqueados_para(es_admin=True)`
vacío) y sigue siendo información real para ese rol, distinto del caso
cliente donde se quitó por pedido explícito.

Verificado en vivo: columna WhatsApp habilitada y en el orden correcto en
`/residentes/{id}`. 128 tests de `test_customers_manage.py` pasan.

