# 235 — `/mis-paquetes`: un residente NO Principal solo ve sus propios paquetes

**Pedido original (cliente):** "Para la vista de /mis-paquetes en caso de
ser un residente 'No Principal' sería bueno que solo se permita visualizar
paquetes que estén a nombre de quien entró en la cuenta, no de otros
residentes -- la idea es que solo el residente principal sea el que pueda
visualizar los paquetes de todos los demás residentes de ese mismo
apartamento."

**Status:** implementado

## Alcance acordado con el cliente

`/mis-paquetes` (`customer_paquetes.py`) hoy amplía el alcance a TODO el
Apartamento para cualquier Ocupante activo (`.scratch/mis-paquetes-vista-
apartamento/issues/01`, vía `telefonos_activos_del_apartamento_de`). Ese
comportamiento se queda igual SOLO para el Principal -- un no-Principal
vuelve a ver solamente lo propio (su Teléfono como Anunciante o
Destinatario), incluidos los contadores por estado.

No se toca `telefonos_activos_del_apartamento_de` (helper de dominio de
propósito general, con sus propios tests que asumen "toda la unidad sin
importar quién pregunta") -- el gate va en la ruta, resolviendo
`ocupante_activo_de_persona` (mismo helper que ya usa `/mis-datos`) para
decidir si la sesión actual es la del Principal antes de decidir qué
Teléfonos consultar.

## Implementación

`customer_paquetes.py::mis_paquetes` -- antes de resolver `telefonos`,
consulta `mi_ocupante = ocupante_activo_de_persona(db, persona.id)`; solo
si `mi_ocupante.es_principal` usa `telefonos_activos_del_apartamento_de`
(toda la unidad), si no usa `[persona.telefono]` (solo lo propio) --
mismo fallback que ya aplicaba a quien no tiene Apartamento asignado.

3 tests nuevos en `test_mis_paquetes.py`: no-Principal no ve paquetes de
otro Ocupante de su misma unidad (ni en la lista ni en los conteos por
pestaña), y el gate mira `es_principal` en el momento de la consulta, no
el orden de login (quien se promueve DESPUÉS también ve el conjunto
completo). Los 18 tests preexistentes de este archivo siguen en verde sin
cambios -- todos los que ya asumían "ve el conjunto combinado" resultan
tener como sesión al Ocupante que la promoción automática de `receive()`
(`promover_al_recibir`) ya vuelve Principal.

Verificado en vivo (curl, dev DB real): un no-Principal con paquetes
propios + de otros 3 Ocupantes de su unidad (6 en total) ahora solo ve
sus 4 propios; el Principal de esa misma unidad sigue viendo los 6.
