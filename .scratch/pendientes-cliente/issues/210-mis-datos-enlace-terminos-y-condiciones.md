# 210 — `/mis-datos`: agregar enlace a términos y condiciones

**Pedido original (cliente):** "también agrega un enlace a los términos y
condiciones" (junto al texto de autorización, ver [[209-mis-datos-texto-autorizacion]]).

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Implementación

Enlace a `/terminos` (ruta ya existente, `terms.py`) agregado junto al
texto de autorización, mismo `<label>`.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
