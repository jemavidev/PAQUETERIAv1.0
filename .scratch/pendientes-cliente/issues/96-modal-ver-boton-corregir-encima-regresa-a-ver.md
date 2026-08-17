# 96 — Modal "Ver": botón "Corregir" al lado del de estado, se abre encima y regresa a Ver

**Pedido original (cliente):**
"ahora al aldo de ese boton, en caso que el paquete anunciado necesite que
se corrija el nombre del anunciantes se tenga tambien este boton presente,
solo si existe la posibilidad de corregir, abriendo encima el moda y
despues de corregir que regrese al modal 'Ver', dime si es posible y como
lo haras" -- confirmado factible y explicado el enfoque antes de
implementar.

**Status:** verificado

## Implementación

- `packages/_resultados.html`, modal "Ver": nuevo botón circular (48px,
  naranja) al lado del botón de siguiente estado -- visible SOLO si
  `p.advertencia_nombre` Y el estado está en `ESTADOS_CORREGIBLES`
  (`ANUNCIADO`/`RECIBIDO`/`ENTREGADO`, issue 93), mismo criterio que la
  advertencia de la columna Cliente y "Modificar" de Acciones.
- "Encima", sin JS nuevo: el botón usa `data-open="modal-correct-<id>"`
  SIN `data-close="modal-ver-<id>"` -- el toggle genérico ya soporta dos
  modales visibles a la vez (issue 80 lo documenta), y como "Corregir" se
  define DESPUÉS de "Ver" en el DOM, pinta encima por orden natural
  (mismo z-50 para ambos).
- "Regresa a Ver": un campo oculto `origen` dentro del form de "Corregir"
  -- el nuevo botón lo pone en `"ver"` vía `onclick` antes de que el click
  llegue al handler delegado que abre el modal. El servidor
  (`correct_recipient_action`, `packages.py`) redirige a
  `/paquetes?ver=<id>` en vez de `/paquetes` cuando `origen == "ver"`. El
  GET de `/paquetes` (`ver_paquete_id`, mismo patrón que `error_paquete_id`
  ya usaba para reabrir "Corregir" en un error) reabre el modal "Ver" de
  ese paquete.
- Las OTRAS dos entradas al mismo modal "Corregir" (advertencia de la
  columna Cliente, "Modificar" de Acciones) ponen `origen` en `""`
  explícitamente al abrir -- así el redirect de siempre (a `/paquetes`
  sola) no cambia para ellas, sin importar el orden en que se haya
  clickeado algo antes en la misma carga de página.

## Verificación

- `tests/web/test_packages.py`: 3 tests nuevos (botón visible solo con
  advertencia, `origen=ver` redirige a `?ver=<id>` y reabre Ver, sin
  `origen` mantiene el redirect de siempre) -- 100 tests, todos pasan.
- Playwright contra el servidor local real: confirmado que "Ver" queda
  SIN el atributo `hidden` mientras "Corregir" está abierto (layering real,
  no un swap), screenshot mostrando ambos modales superpuestos, corrección
  completa de punta a punta terminando con "Ver" reabierto mostrando el
  nombre ya corregido -- y confirmado por separado que abrir "Corregir"
  desde la tabla (no desde Ver) sigue devolviendo al `/paquetes` de
  siempre, sin `?ver=`.
- Suite completa: ver commit para el conteo final.
- Desplegado a test.papyrus.com.co (2026-08-17), confirmado en el contenedor real (`docker exec paquetex-app-1`).
