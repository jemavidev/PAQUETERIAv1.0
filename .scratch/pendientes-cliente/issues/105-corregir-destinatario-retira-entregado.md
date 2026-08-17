# 105 — "Corregir destinatario" retira ENTREGADO de los estados corregibles

**Pedido original (cliente):**
"Necesito que el boton que abre el modal 'modal-correct-<id>'... en caso
que ya el paquete este en estado 'Entregado o Cancelado' no aparezca el
boton. Confirmado que se veria mejor."

**Status:** implementado

## Contexto -- reversión parcial del mismo día

`ESTADOS_CORREGIBLES` había incluido `ENTREGADO` desde issue 93 (mismo
día, 2026-08-17 por la mañana), a pedido explícito del cliente: "quiero
poder cambiar o corregir cuando el nombre del anunciado no coincide...
tambien en el estado de entregado". Ahora, tras ver el resultado en vivo,
el cliente pidió lo contrario: que el botón no aparezca para paquetes
Entregados. `CANCELADO` nunca estuvo incluido -- ya cumplía el pedido sin
cambios.

## Implementación

- `paquete_lifecycle.py`: `ESTADOS_CORREGIBLES = (ANUNCIADO, RECIBIDO)` --
  se retira `ENTREGADO`. Docstrings de la constante y de
  `corregir_destinatario` actualizados documentando la historia completa
  (ANUNCIADO solo → +RECIBIDO/ENTREGADO → -ENTREGADO), para que quien lea
  el código no se confunda viendo commits que se contradicen en el mismo
  día.
- `ADR-0001`, `paquete_correccion_service.py`, `packages.py`: docstrings
  actualizados al mismo criterio.
- `_resultados.html` (advertencia clickeable, botón "Corregir" dentro del
  modal "Ver", existencia del modal "Corregir" en el DOM) y
  `_acciones.html` ("Modificar" de Acciones): las 4 condiciones
  `p.estado.value in ("ANUNCIADO", "RECIBIDO", "ENTREGADO")` vuelven a
  `("ANUNCIADO", "RECIBIDO")`.

## Verificación

- `tests/data_model/test_corregir_destinatario.py` y
  `tests/web/test_packages.py`: los 4 tests que issue 93 había escrito
  para probar que ENTREGADO SÍ se puede corregir se revirtieron a probar
  que NO se puede (mismo patrón que el test de CANCELADO, que ya existía
  y no cambió) -- 131 tests entre ambos archivos, todos pasan.
- Playwright contra el servidor local real, sobre un paquete ENTREGADO
  con advertencia de nombre real: confirmado que el ícono de advertencia
  sigue mostrándose (informativo, ya no clickeable), cero botones
  `data-open="modal-correct-..."` en toda la fila, y el modal "Ver" ya no
  muestra el botón naranja "Corregir" junto al de estado.
- Suite completa: ver commit para el conteo final.
- Pendiente: deploy a test.papyrus.com.co.
