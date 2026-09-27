# 241 — `/mis-datos`: modal "Mudarse" — "TORRE" como texto fijo, no "el "

**Pedido original (cliente):** "Cambia este texto 'Tus datos quedarán
solo de consulta relacionados con el <Torre> APT <Apartamento>.' a 'Tus
datos quedarán solo de consulta relacionados con TORRE <Torre> APT
<Apartamento>.'"

**Status:** desplegado en test (código revisado idéntico a `3ea732f`, 2026-09-26), pendiente confirmar en vivo

## Alcance

Seguimiento directo de issue 240 (mismo modal "Mudarse de este
apartamento", `customer/verify.html`). "TORRE" pasa a ser palabra fija
del texto (en vez de "el " genérico) -- como `apartamento.torre` ya
guarda la palabra "TORRE" como parte del valor, se le aplica el filtro
`torre_sin_prefijo` (ya existente, mismo que usa `/consultar`) para que
solo aporte el número y no quede "TORRE TORRE 1".

## Limpieza del registro (2026-09-26)

Estado anterior: "implementado". El código de la app en MATT (`CODE/src/app`, `CODE/alembic`) es idéntico al desplegado en test (`jemavidev/PaqueteX` `3ea732f`), así que este cambio ya está en test.
