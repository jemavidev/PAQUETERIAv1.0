# 313 — Ícono "Mostrar conexiones" muestra badge con la cantidad de conexiones

**Pedido original (cliente):** "necesito que el icono de 'Mostrar conexiones' cuando este
activado muestre un badge con la cantidad de conexiones". Corrección inmediata en vivo: "pero la
idea es que se muestre antes de hacer click, y debe ser de color rojo" -- el badge NO debía
depender de que el toggle ya estuviera activado (es un adelanto de lo que hay, no una
confirmación de lo que se está viendo), y el color se corrigió de índigo a rojo para que
coincida con el resto de badges de conteo de la app (issue 126).

**Status:** implementado -- pendiente verificar visualmente en vivo (extensión de Chrome no
disponible en esta sesión). Verificado end-to-end contra el servidor real (`localhost:8010`,
caso "JESUS VILLALOBOS"): `q=jesus` (SIN `conectados`) -> header `X-Conteo-Conectados: 2` + badge
rojo "2" visible con el toggle todavía apagado; sin conexiones -> header vacío, sin badge. 3
tests (2 nuevos, 1 renombrado), 389 tests en verde
(`test_packages.py`/`test_layout.py`/`test_customers_manage.py`). Ronda 3 (retroalimentación en
vivo: "acerca el badge al icono"): el badge estaba anclado al `<button>` completo (que tiene
`px-3` de relleno alrededor del ícono), dejándolo flotando lejos del glifo -- se movió el
`relative` a un `<span>` que envuelve SOLO el ícono, así el badge queda pegado a su esquina sin
importar el relleno del botón. Sin cambios de comportamiento (mismos 389 tests en verde).

Ronda 4 ("necesito que el badge sea un poquito mas grande"): `min-w-[14px]`/`h-[14px]`/
`text-[9px]` -> `min-w-[18px]`/`h-[18px]`/`text-[10px]` (mismo tamaño que el badge de conteo de
Estado, issue 126), offsets ajustados a `-top-2 -right-2` para que siga centrado en la esquina
del ícono con el nuevo tamaño.

## Diseño final

Badge circular rojo (`bg-red-600`), mismo patrón visual y color que los badges de conteo de
Estado (issue 126) -- visible SIEMPRE que haya al menos 1 conexión para la búsqueda actual, sin
importar si el toggle está activado. Nunca pinta "0" -- sin conexiones, simplemente no aparece
(no hay nada que "0" le aporte a un adelanto).

## Implementación

Nueva `_contar_conexiones(db, q)` (reemplaza a la `_hay_conexiones` de issue 310, que usaba
`.exists()`) -- corre el conteo del lado "conectado" de la consulta SIEMPRE, sin importar el
`conectados` que trajo la petición actual (a diferencia del primer intento, que reusaba el
`total` de `_listar`, solo válido cuando `conectados=True` ya venía activado). `hay_conexiones`
(issue 310, gate de deshabilitado) pasa a derivarse de este mismo conteo (`> 0`) en vez de una
consulta aparte. Viaja como header de respuesta (`X-Conteo-Conectados`) porque la barra de
búsqueda vive fuera de `#resultados-paquetes` y no se vuelve a renderizar en cada fetch de
búsqueda en vivo -- el JS de `_busqueda_filtros.html` crea/actualiza/quita el `<span>` del badge
a mano tras cada fetch.
