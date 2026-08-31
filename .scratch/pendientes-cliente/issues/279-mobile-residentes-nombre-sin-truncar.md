# 279 — Seguimiento a [[278]]: nombre ya no se trunca en mobile

**Pedido original (cliente):** "perfecto, ahora no cortes el nombre de
los cliente so residentes con los '...', ya exciste mas espacio"

**Status:** implementado (con una advertencia -- ver Verificación)

## Alcance

`customers_manage/_resultados.html`, columna Nombre de la tabla plana
(mismo elemento de [[277]]/[[278]]): se retira el truncado con "…"
(`truncate` + `max-w-[clamp(85px,26vw,180px)]` + `title=`) -- el nombre
vuelve a mostrarse completo en una sola línea (`whitespace-nowrap`),
igual que siempre en desktop.

## Verificación

Medido en vivo (mismo método de iframe que [[277]]/[[278]]) en los
mismos 4 anchos de referencia:

| Ancho viewport | Overflow (scroll lateral) |
|---|---|
| 360px | 32px |
| 375px | 20px |
| 390px | 10px |
| 414px | 0px |

El pedido asumía que ya había espacio suficiente tras [[278]] (bajar
Auto/Principal a su propia fila) -- en la práctica, con nombres reales
del set de prueba (ej. "ANGELICA ARRAZOLA", ~150px sin truncar), SOLO
deja de haber scroll lateral desde ~414px de ancho (iPhone 12/13/14
Pro Max y similares). En los anchos más comunes hoy (360-390px --
Android estándar, iPhone SE/12 mini) vuelve a aparecer scroll lateral,
proporcional al largo del nombre.

Implementado tal como se pidió (no se revirtió por cuenta propia) --
Suite completa (`pytest tests/web/test_customers_manage.py`): 151
passed, sin regresiones (ningún test dependía de las clases de
truncado que se quitaron). Reportado al cliente con estos números para
que decida si el trade-off es aceptable o si prefiere retomar el
truncado (posiblemente con un límite más generoso que antes).
