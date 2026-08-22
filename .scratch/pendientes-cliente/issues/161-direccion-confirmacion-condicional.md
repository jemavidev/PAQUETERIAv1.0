# 161 — `/residentes` tab Dirección: confirmación automática solo con unidad vacía

**Pedido original:** "La idea es que cuando el personal de staff asigne un residente a un
apartamento, en caso que esté vacío, automáticamente lo debería confirmar como principal, y si no
está vacío quedará como pendiente para que el principal lo confirme, por otro lado si estos
residentes no cuentan con un principal, entonces se esperará a que alguno de ellos reciba un
paquete y el primero de ellos será el principal." Confirmado el entendimiento antes de tocar
código: 2 de las 3 reglas ya estaban implementadas (unidad vacía → confirma y promueve; sin
Principal → gana el primero en recibir un paquete, `promover_al_recibir`) -- la única que faltaba
era la del medio.

**Status:** implementado

## Diagnóstico

`ocupante_service.reasignar_apartamento` (única función detrás de tab Dirección) confirmaba
SIEMPRE al nuevo Ocupante, sin importar si la unidad ya tenía gente -- porque `confirmar_ocupante`
permite a CUALQUIER staff confirmar sin restricción (`_puede_confirmar`, `isinstance(actor,
Usuario): return True`). Esto quedó reforzado sin querer por [[158]] ("staff con control total"):
al dejar de bloquear la asignación a unidades ocupadas, el auto-confirm que solo tenía sentido
para unidades vacías empezó a aplicar también ahí, saltándose el paso de que el Principal (o
staff) confirme a la nueva persona.

## Cambio

`reasignar_apartamento`: antes de agregar al nuevo Ocupante, se evalúa si la unidad YA tenía algún
Ocupante activo (`hay_otro_ocupante_activo`, evaluado ANTES de agregar -- si no, el propio nuevo
Ocupante ya cuenta como "otro" y el chequeo siempre daría `True`).
- Unidad vacía: se agrega Y se confirma en el mismo acto (como antes) -- promueve a principal
  automáticamente (`confirmar_ocupante`, sin cambios en esa función).
- Unidad ya ocupada: se agrega y se deja PENDING -- sin llamar a `confirmar_ocupante`. Mismo
  criterio que ya usa tab Residentes (`agregar_ocupante` nunca auto-confirma).

Sin cambios en `agregar_ocupante` (nunca auto-confirmó, ya cumplía) ni en `promover_al_recibir`
(ya implementaba la regla 3 tal cual se pidió).

## Verificación

- 1 test existente corregido (`test_reasignar_apartamento_a_unidad_con_principal_no_promueve` →
  ahora verifica PENDING) + 1 test nuevo (unidad con solo pendientes, sin Principal, también queda
  PENDING -- no se auto-promueve por llegar primero, solo por confirmarse primero).
- 2 tests de ruta reescritos (`test_direccion_permite_agregar_a_unidad_con_principal_ya_confirmado`,
  `test_direccion_permite_agregar_a_unidad_con_solo_pendientes_queda_pending`).
- Suite completa: 1046/1046.
- Verificado en vivo contra `localhost:8010`: unidad vacía sigue confirmando+promoviendo; unidad
  ya ocupada ahora deja al nuevo Residente "Pendiente de confirmar". Datos de prueba limpiados.
