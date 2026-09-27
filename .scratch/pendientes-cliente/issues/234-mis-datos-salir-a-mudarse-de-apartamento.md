# 234 — `/mis-datos`: "Salir de este apartamento" → "Mudarse de este apartamento"

**Pedido original (cliente):** "Cambia este texto 'Salir de este
apartamento' por 'Mudarse de este apartamento'"

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

Vista de un Ocupante NO principal (`customer/verify.html`, roster de solo
lectura) -- botón de autodescarte de la unidad y el texto de confirmación
nativa (`confirm()`) que lo acompaña. Cambia solo el texto visible, ningún
comportamiento.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
