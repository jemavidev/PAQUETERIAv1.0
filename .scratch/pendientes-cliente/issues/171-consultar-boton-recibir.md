# 171 — `/consultar`: botón "Recibir" para staff, igual que "Entregar"

**Pedido original:** "En la vista de /consultar, sería bueno tener una opción de un botón similar
a 'Entregar paquete', pero para 'Recibir paquete', que te parece, que se comporte igual, pero solo
para recibir un paquete y si estás logueado como staff, dime que piensas" → confirmado: "si,
intenta que sea reutilizando lo que se tiene que ya sabemos que funciona, los modales, dime que te
parece."

**Status:** verificado

## Cambio

- `search.py`: cuando hay sesión de staff y el paquete está ANUNCIADO, ahora también arma el
  mismo contexto que ya calcula `packages.py` para `modal_recibir` (`tipos`, `condiciones`,
  `catalogo_torres`, `residentes_por_unidad`, `candidatos_correccion`) — solo en ese caso, para no
  cargar de más la inmensa mayoría de consultas anónimas.
- `search/form.html`: nuevo botón "Recibir" (staff + ANUNCIADO), mismo criterio de gate por
  template que ya tenía "Entregar" (staff + RECIBIDO). Reusa el modal compartido `modal_recibir`
  (el mismo de `/paquetes` y `/announce`) en vez de reimplementar el flujo. `recursos_recibir()`
  (JS del picker, escaneo de guía, vista previa "+ Nuevo residente") ahora también se incluye en
  estado ANUNCIADO, no solo RECIBIDO.
- `components/_recibir_paquete.html` (`modal_recibir`): 2 parámetros nuevos, opcionales, `origen`
  y `q` — inyectan los mismos hidden fields `origen`/`q` que ya usa el modal "Entregar" de
  `/consultar`, para que el POST redirija de vuelta a `/consultar?q=...` en vez de a `/paquetes`.
  Con ambos en `None` (default) el comportamiento es idéntico al de siempre — los callers
  existentes en `/paquetes` y `/announce` no cambiaron.
- `packages.py` (`receive_action`): mismo mecanismo que ya tenía `deliver_action` — nuevos
  parámetros `origen`/`q` (`Form(None)`), `destino` calculado una sola vez al inicio y aplicado en
  los 4 puntos de retorno (3 de error + el redirect final de éxito).

## Verificación

- 5 tests nuevos en `test_search.py` (aparición condicional del botón, action/hidden fields del
  form, y el POST completo con redirect de vuelta a `/consultar`, incluyendo el camino de error).
- Suite completa: 1076/1076.
- Verificado en vivo contra `localhost:8010`: anunciado un paquete de prueba, confirmado que el
  botón "Recibir" aparece en `/consultar` con el modal correcto (`data-open`, `action`, hidden
  `origen`/`q`), POST recibido correctamente, redirige a `/consultar?q=<código>`, el paquete queda
  RECIBIDO y el botón cambia a "Entregar". Datos de prueba (paquete + persona) eliminados después.
