# 240 — `/mis-datos`: el modal "Mudarse" nombra la Torre/Apartamento que se deja

**Pedido original (cliente):** "Cambia este texto 'Tus datos quedarán
solo de consulta.' a 'Tus datos quedarán solo de consulta relacionados
con el TORRE <Torre> APT <Apartamento>.'"

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

Modal "Mudarse de este apartamento" (issue 237, `customer/verify.html`,
mensaje del `modal_confirmacion`). Interpola `apartamento.torre` +
`apartamento.apartamento`. `apartamento` está siempre poblado en este
punto: la sección solo renderiza cuando `es_ocupante_no_principal` es
verdadero, que exige `mi_ocupante` con Apartamento activo.

## Seguimiento (issue 241)

Pedido de ajuste: "TORRE" pasa a ser texto fijo antes del valor en vez de
"el " + el valor completo. Como `apartamento.torre` YA incluye la palabra
"TORRE" (se guarda así, ej. "TORRE 1"), usar el valor completo tal cual
hubiera quedado "TORRE TORRE 1" -- se aplica el filtro `torre_sin_prefijo`
ya existente (mismo que usa `/consultar`, issues 79/152, hecho
exactamente para este caso) para quedarse solo con el número.

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
