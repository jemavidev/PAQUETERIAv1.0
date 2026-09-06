# 321 — Píldora con el total de paquetes de un residente en `/residentes`

**Pedido original (cliente):** "Tanto para la vista del mobil como para la vista del desktop, que
posibilidad existe en tener una pildora adiciona con un numero asociado, la idea es poder tener
un boton con el numero total de paquetes asociados a un cliente especifico, digamos que 'CLiente
1' tiene 1 paquete recibido, 2 anunciados, 1 cancelado y 3 entregados, esta pildora deberia decir
el numero 7, esta pildora deberia ser cliqueable y deberia redirigir a la vista con uno de los
siguentes datos en la busqueda 'telefono, email o usuario de whatsapp' mostrando todos estos 7
paquetes de este cliente, como ya esta funcionando actualmente. Esta pildora debe ser similar a
las existentes 'Auto, Principal y Torre/Apt'."

**Status:** implementado (color fucsia, ver amendment abajo), desplegado a test.papyrus.com.co
(2026-09-05, commit `bcac30d`) -- pendiente que el cliente lo confirme visualmente (extensión de
Chrome no disponible en esta sesión). Verificado contra el servidor real de desarrollo (residente
real "JESUS VILLALOBOS", +573002596319: píldora mostró "6", `/paquetes?q=%2B573002596319` devolvió
exactamente 6 paquetes) y 6 tests nuevos, suite completa (`test_packages.py`, `test_layout.py`,
`test_customers_manage.py`, `test_search.py`) en verde. En producción (test.papyrus.com.co) se
confirmó sin login que el CSS correcto (`?v=91`, con las clases fucsia) ya se sirve -- la
verificación de comportamiento (login + ver la píldora en un residente real) la hará el cliente.

## Diseño

Misma familia visual que Auto (esmeralda)/Principal (azul)/Torre-Apt (ámbar) -- píldora redonda
`text-[11px]`, color CYAN nuevo (no pisa ninguno de los 3 ya usados), sin `sm:hidden`: a diferencia
de Torre/Apto (que en mobile pasa a píldora aparte de su columna de desktop), el cliente pidió
explícitamente que esta se vea igual en ambas vistas -- vive en el mismo wrapper
`flex items-center gap-1.5 flex-wrap max-w-[150px] sm:contents` que ya comparten Auto/Principal, así
que es una sola marca en el DOM, visible en las dos.

**Principio de consistencia conteo/link:** una píldora que promete "N paquetes, clic para verlos"
tiene que usar la MISMA condición para contar que para armar el link -- si no, puede prometer de
más o de menos. Se resolvió con UN solo término identificador por prioridad (teléfono > usuario de
WhatsApp > email, ninguno se une con los otros 2) en vez de una unión de los 3 campos: un residente
con más de un dato de contacto podría en teoría tener paquetes bajo el que NO se eligió (raro, caso
borde de teléfono prestado ya documentado en issue 163/308), pero se prefirió aceptar ese
sub-conteo posible antes que arriesgar una píldora que muestre "7" y el clic traiga menos o más de
7 -- "una píldora que promete de más es peor que una que cuenta de menos".

## Implementación

- `condiciones_busqueda_paquetes` (antes `_condiciones_busqueda`, privada de `packages.py`) se
  relocó a `paquete_service.py` como función pública -- ahora la comparten `packages.py` (búsqueda
  de `/paquetes`, issue 308) y la nueva `contar_paquetes_de_persona` (misma regla "exacta" que ya
  usa `/paquetes`, `conectados=False`), evitando que la definición de "paquetes propios de un
  cliente" viva duplicada en 2 rutas.
- `contar_paquetes_de_persona(session, persona) -> (total, termino)` (`paquete_service.py`):
  cuenta TODOS los estados (Anunciado/Recibido/Entregado/Cancelado suman), resuelve el término con
  la prioridad de arriba; `termino=None` si la Persona no tiene ninguno de los 3 (no debería
  ocurrir en la práctica -- `ck_personas_telefono_o_whatsapp`, ADR-0007, garantiza teléfono O
  whatsapp).
- `_adjuntar_conteo_paquetes` (`customers_manage.py`): 1 consulta por fila (tolerado, mismo
  criterio ya usado por `_adjuntar_ocupante`/`_agrupar_por_apartamento` -- acotado por
  `_POR_PAGINA`, vista de staff de bajo tráfico). Wireado SOLO en el camino `resultados` (búsqueda
  normal/"Principales"/"Sin apartamento"), NO en "Agrupar por apartamento" -- esa vista ya organiza
  por unidad, no por persona individual.
- `_resultados.html`: píldora cyan agregada junto a Auto/Principal, antes de Torre/Apto; el
  `<a>` enlaza a `/paquetes?q=<termino urlencoded>`. La condición del wrapper de badges se amplió
  con `or p.total_paquetes` para que la fila muestre el bloque de badges aunque no tenga ninguno de
  los otros 3 (Auto/Principal/Apartamento).

## Verificación en vivo (servidor real, dev)

- `GET /residentes?q=jesus` -> píldora renderizada:
  `<a href="/paquetes?q=%2B573002596319" ... title="Ver los 6 paquetes de JESUS VILLALOBOS">6</a>`
- `GET /paquetes?q=%2B573002596319` -> exactamente 6 códigos de acceso distintos en la respuesta,
  coincide con el "6" prometido por la píldora.

## Amendment 2026-09-05 — color cambiado de cian a fucsia (más contraste)

Pedido explícito del cliente tras ver la primera versión: "que otro color que haga mas contraste
puedes usar". Se calcularon los ratios WCAG de contraste (texto-700 sobre fondo-100) de varias
opciones antes de elegir:

| Color | Contraste |
|---|---|
| Cian (original) | 4.79:1 |
| Fucsia | **5.43:1** |
| Rosa | 5.24:1 |
| Violeta | 5.98:1 |

Violeta tiene el contraste más alto de los 3, pero ya se usa en la app para el glow de los botones
CTA principales (issue 306) -- pisarlo confundiría "acción primaria" con "total de paquetes". Rosa
queda visualmente cerca del rojo que la app ya usa para advertencias (Torre/Apto de un paquete
cerrado que se mudó, issue 307) -- riesgo de leerse como "algo anda mal". Se preguntó al cliente
por preferencia explícita (sin respuesta puntual, "sin preferencia") y se eligió **fucsia**: mejora
el contraste sobre cian sin colisionar con ningún significado ya establecido en la paleta
(esmeralda=Auto, azul=Principal, ámbar=Torre/Apto, slate=Sin apartamento, rojo=advertencias,
violeta=CTA, índigo=Comparte apartamento).

Cambio puramente de color -- mismo layout/comportamiento, mismos 6 tests (actualizados para
esperar `bg-fuchsia-100`/`text-fuchsia-700`/`border-fuchsia-200` en vez de cian), Tailwind
recompilado (`?v=91`), verificado en vivo contra el mismo residente real (JESUS VILLALOBOS: píldora
ahora en fucsia, sigue mostrando "6").
