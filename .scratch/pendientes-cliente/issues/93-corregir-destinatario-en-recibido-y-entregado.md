# 93 — "Corregir destinatario" ahora también en RECIBIDO y ENTREGADO

**Pedido original (cliente):**
"hagamos un modificacion, quiero poder cambiar o corregir cuando el nombre
del anunciado no coincide, pero quiero poder hacer esto en el estado de
recibido tambien" — seguido, sobre la marcha, de: "y en el estado de
entregado tambien".

**Status:** verificado

## Implementación

`corregir_destinatario` (`paquete_lifecycle.py`) era una excepción acotada y
auditada a ADR-0001 (snapshot inmutable), pero restringida solo a
`ANUNCIADO` — con el razonamiento explícito de que "una vez RECIBIDO el
contexto de entrega es tan inmutable como siempre, sin excepción". El
cliente pidió ampliar esa restricción: el error de tipeo en el nombre
anunciado no siempre se nota mientras el paquete sigue `ANUNCIADO`.

- Nueva constante `ESTADOS_CORREGIBLES = (ANUNCIADO, RECIBIDO, ENTREGADO)`
  en `paquete_lifecycle.py` — único punto de la verdad, reusado por el
  guard de `corregir_destinatario` Y por `packages.py` para decidir a qué
  paquetes precargarles `candidatos_correccion` (antes solo `ANUNCIADO`).
  `CANCELADO` queda deliberadamente afuera — no fue parte del pedido, y no
  tiene sentido de negocio corregir a quién le iba a llegar un paquete que
  nunca se entregó.
- `docs/adr/0001-paquete-snapshot-inmutable.md` actualizada: cada función
  de "excepciones conocidas" documenta su propio guard de estado
  (`corregir_destinatario` ahora `ESTADOS_CORREGIBLES`, `corregir_apartamento`
  sigue solo `ANUNCIADO` -- no se tocó, no fue parte de este pedido).
- `_resultados.html`: el ícono de advertencia (nombre no coincide) es
  clickeable en ANUNCIADO/RECIBIDO/ENTREGADO; el modal "Corregir
  destinatario" existe en el DOM para esos 3 estados (antes solo
  ANUNCIADO).
- `_acciones.html`: el ícono "Modificar" de la columna Acciones sigue el
  mismo criterio — activo en los 3 estados, apagado (gris) solo en
  CANCELADO.

## Verificación

- `tests/data_model/test_corregir_destinatario.py`: los tests que antes
  esperaban `TransicionInvalida` en RECIBIDO/ENTREGADO ahora verifican que
  la corrección SÍ se aplica (y no cambia `estado`); el test de CANCELADO
  se mantiene sin cambios (sigue siendo el único estado que rechaza).
- `tests/web/test_packages.py`: tests renombrados/reescritos para el ícono
  de advertencia y el botón "Modificar" (clickeable en los 3 estados, no en
  CANCELADO) + flujo completo de corrección vía HTTP en RECIBIDO y
  ENTREGADO (candidato seleccionado, 303, nombre persistido).
- Playwright contra el servidor local real: corregido un paquete RECIBIDO
  y uno ENTREGADO de punta a punta (clic en advertencia → modal → elegir
  candidato → nombre actualizado, visible en la lista).
- Suite completa: ver commit para el conteo final.
- Desplegado a test.papyrus.com.co (2026-08-17), confirmado en el contenedor real (`docker exec paquetex-app-1`).
