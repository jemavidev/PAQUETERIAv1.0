# 314 — Bandera "primera entrega" en el modal Entregar (por teléfono)

**Pedido original (cliente):** en el modal "Entregar" de `/paquetes`, cuando sea la primera vez
que se entrega un paquete a un residente, mostrar una bandera/prueba visual de eso. El criterio
es el NÚMERO DE TELÉFONO específico (`recipient_phone`), independientemente de que ese teléfono
viva con otros residentes en la misma unidad.

**Status:** implementado -- pendiente verificar visualmente en vivo (extensión de Chrome no
disponible en esta sesión). El modal se confirmó ubicado en `/paquetes` (no `/residentes`, el
pedido original lo mencionaba ahí por error del cliente, aclarado con AskUserQuestion). Verificado
contra datos reales (`localhost:8010`): 3 paquetes RECIBIDO reales, ninguno pinta la bandera
(2 ya tenían entrega previa a ese teléfono, 1 no tiene teléfono) -- consistente con lo esperado.
4 tests nuevos cubriendo primera vez / no-primera-vez / sin teléfono / mismo teléfono con
destinatarios distintos, 393 tests en verde
(`test_packages.py`/`test_layout.py`/`test_customers_manage.py`).

## Regla

`primera_entrega_a_telefono` = `True` cuando el paquete está en RECIBIDO, tiene
`recipient_phone` propio, y NINGÚN otro paquete de TODA la historia (cualquier destinatario,
cualquier unidad) fue entregado (`ENTREGADO`) con ese mismo `recipient_phone`. Sin teléfono en el
snapshot, no se puede afirmar "primera vez" -- no se pinta la bandera en ese caso (ni "primera"
ni "no primera").

## Piezas reusables

Mismo patrón de batch query "un puñado fijo de consultas por página" que ya usa el resto de
`_listar()` (`app/web/routes/packages.py`) -- una sola consulta agrupando los teléfonos de los
paquetes RECIBIDO de la página contra el historial de ENTREGADO, no una consulta por fila.
