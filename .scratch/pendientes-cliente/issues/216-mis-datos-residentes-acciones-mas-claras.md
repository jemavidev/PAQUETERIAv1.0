# 216 — `/mis-datos` tab Residentes: acciones de fila más claras

**Pedido original (cliente):** "En la vista de /mis-datos el tab de
Residentes debería poder tener una mejor forma de mostrar esta información
'Eliminar WhatsApp, Convertir en residente principal, Eliminar teléfono y
Eliminar', la idea es que muestres algunas alternativas, podrían ser
iconos, emojis o palabras más concisas."

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

Enlaces de texto reemplazados por chips ícono/emoji+palabra corta:
✅ Confirmar, 🗑️ Rechazar/Eliminar, ⭐ Principal, ✕ Teléfono, ✕ WhatsApp.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
