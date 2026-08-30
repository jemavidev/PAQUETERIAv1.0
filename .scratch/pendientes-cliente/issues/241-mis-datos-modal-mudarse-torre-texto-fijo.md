# 241 — `/mis-datos`: modal "Mudarse" — "TORRE" como texto fijo, no "el "

**Pedido original (cliente):** "Cambia este texto 'Tus datos quedarán
solo de consulta relacionados con el <Torre> APT <Apartamento>.' a 'Tus
datos quedarán solo de consulta relacionados con TORRE <Torre> APT
<Apartamento>.'"

**Status:** implementado

## Alcance

Seguimiento directo de issue 240 (mismo modal "Mudarse de este
apartamento", `customer/verify.html`). "TORRE" pasa a ser palabra fija
del texto (en vez de "el " genérico) -- como `apartamento.torre` ya
guarda la palabra "TORRE" como parte del valor, se le aplica el filtro
`torre_sin_prefijo` (ya existente, mismo que usa `/consultar`) para que
solo aporte el número y no quede "TORRE TORRE 1".
