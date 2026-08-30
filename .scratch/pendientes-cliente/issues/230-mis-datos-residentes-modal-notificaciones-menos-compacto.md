# 230 — `/mis-datos` tab Residentes: modal de Notificaciones menos compacto

**Pedido original (cliente):** "Ya que se tienen los espacios mejorados,
necesito que la sección/modal de Notificaciones sea menos compacta."
(seguimiento de [[229-mis-datos-residentes-editar-notif-como-modal-y-bug-canal-doble]]).

**Status:** implementado

## Implementación

`verify.html`: el modal de Notificaciones por residente pasa de una fila
comprimida de una sola línea por evento (texto `text-xs`, canales en línea
con su etiqueta) al mismo patrón de encabezado+filas espaciadas que ya usa
el tab "Notificaciones" principal de esta página (`sm:grid` de 5 columnas,
encabezado de canales visible, `py-3` por fila). Modal ancho `lg`
(`max-w-2xl`) en vez de `md`, para que la grilla tenga espacio en desktop.

También corregido de paso (encontrado en la misma revisión, issue 229): los
inputs de Teléfono/WhatsApp del modal "Editar" mostraban el texto literal
"None" en vez de quedar vacíos con su placeholder -- `dict.get(key, '')`
solo usa el default si la LLAVE falta, no si el VALOR ya es `None`
(`personas_telefono`/`personas_whatsapp` sí tienen la llave con `None`
cuando el residente no tiene ese canal). Corregido con `or ''` en las dos
variables.
