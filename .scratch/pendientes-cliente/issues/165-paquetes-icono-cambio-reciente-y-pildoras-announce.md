# 165 — `/paquetes`: ícono de cambio reciente de apartamento + píldoras de `/announce`

**Pedido original:** "de qué forma puedo identificar visualmente si un residente ha tenido en
algún momento un cambio de apartamento, esto sería fácil para saber porque es diferente un
apartamento de otro, de qué forma crees que podría visualizarlo desde la vista /paquetes?" →
propuesta de ícono junto al chip de dirección, confirmada con una condición extra: "solamente en
el caso que esta acción de cambio/desvinculación de un apartamento haya sido reciente, digamos los
últimos 30 días." En el mismo mensaje, pedido aparte: "en la vista /announce, las píldoras fueran
un poco más grandes, similares a las que ya hemos venido usando, adicional que esas mismas
píldoras fueran en esta vista las que permiten Recibir o Entregar, de esta forma nos ahorramos los
enlaces que se puedan generar."

**Status:** implementado

## Parte 1 — Ícono 🔄 en `/paquetes` (elegido entre 3 opciones mostradas: 🚚/🔄/↔️)

- `ocupante_service.cambios_recientes_de_apartamento(session, persona_ids, dias=30)`: batch --
  para cada Persona, si dio de baja un Ocupante (cambió o dejó una unidad) en los últimos 30 días,
  la unidad que DEJÓ (la vieja, no la actual -- eso es lo que explica la diferencia). Con más de
  una baja reciente, la más reciente gana.
- `packages.py` (`_listar`): segundo loop después del existente (necesario porque
  `persona_destino_id` recién se resuelve dentro del loop principal) -- una sola consulta batch
  para toda la página, no una por fila (mismo criterio que el resto de esta lista, verificado con
  el test de guardia N+1 ya existente, ajustado de 12 a 13 queries fijas).
- Ícono en 2 lugares: la columna Dirección de la lista, y la línea de dirección del modal "Ver" --
  tooltip con la unidad vieja ("Vivía antes en TORRE X · Apto Y (cambio reciente, últimos 30
  días)").

## Parte 2 — Píldoras de `/announce`

- `components/_persona_resuelta.html`: el código de acceso de cada paquete "en curso" pasa de
  `text-xs` a `text-sm` (mismo tamaño que ya usa `/paquetes` en todos lados) y de link a
  `/consultar` + link de texto aparte ("Recibir →"/"Entregar →") a UN solo elemento -- la propia
  píldora enlaza directo a `/paquetes?recibir=<id>` o `?entregar=<id>` según el estado.

## Verificación

- Dominio: 5 tests nuevos (`cambios_recientes_de_apartamento`: encuentra baja reciente, ignora
  bajas de +30 días, sin baja no aparece, usa la más reciente si hay varias, lista vacía sin ids).
- Ruta: 3 tests nuevos en `/paquetes` (ícono aparece con mudanza reciente, no aparece sin
  historial, no aparece si la mudanza fue hace +30 días).
- Suite completa: 1067/1067.
- Verificado en vivo contra `localhost:8010`: mudanza de prueba entre 2 unidades, confirmado el
  ícono con tooltip correcto en lista y modal Ver; confirmado que la píldora de `/announce` abre
  directo el modal Recibir/Entregar sin enlace aparte. Datos de prueba limpiados.
