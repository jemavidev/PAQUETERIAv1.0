# 158 — `/residentes` tab Dirección: staff con control total sobre unidades ocupadas

**Pedido original:** "estoy intentando mover a un residente que yo ya sé que vive en ese
apartamento pero no me lo permite, me aparece 'Ya tiene residentes -- para sumar a alguien más,
hacelo desde la ficha de ANGELICA ARRAZOLA'... la idea es que yo como staff sea quien controle el
lugar donde viven los residentes y ellos a su vez por medio del flujo de residentes al ingresar
por OTP también puedan hacer cambios pero con restricción". Confirmado el entendimiento antes de
tocar código (ver turno anterior): staff sin restricciones artificiales, autoservicio del
residente sin cambios. Respuesta del cliente: "En el punto 1 me parece bien todo, solo quiero que
tengas presente que la integridad debe ser real... Para el punto 2 me parece bien, solo verifica
que nada se rompa y todo se lo más íntegro, lógico y transparente posible."

**Status:** implementado

## Diagnóstico

El bloqueo NO era una regla de negocio real -- `agregar_ocupante`/`confirmar_ocupante` ya
soportaban sumar a alguien a una unidad ocupada sin romper nada (tab Residentes lo hace a diario).
Era un guard exclusivo de la ruta `customers_manage_asignar_apartamento` (tab Dirección, ticket 13
de `.scratch/ocupante-principal-escenarios`), no del dominio.

## Cambio

- `customers_manage.py`: se elimina el guard `ya_tiene_residentes` (y el `hay_otro_ocupante_activo`
  que lo alimentaba) de esa ruta -- ahora cae directo en `reasignar_apartamento`/`mover_ocupante`,
  que ya manejan correctamente una unidad ocupada:
  - Asignación directa (sin conflicto): `agregar_ocupante` + `confirmar_ocupante` -- si la unidad
    ya tiene principal confirmado, el nuevo Residente queda confirmado pero NO principal (no pisa
    a quien ya lo es). Si la unidad solo tiene pendientes (sin principal confirmado todavía), el
    nuevo Residente puede quedar promovido -- mismo comportamiento YA existente de
    `confirmar_ocupante` ("el primero en confirmarse, no en llegar, es quien queda de principal"),
    solo que ahora también alcanzable desde acá.
  - "Mover" (`mover_de_otra_unidad`): `mover_ocupante` tampoco chequeaba ocupación del destino --
    ahora también puede aterrizar en una unidad con gente, llega pending (no auto-confirma, mismo
    criterio que cualquier alta nueva sin promover).
  - Se evaluó explícitamente el riesgo de integridad que señaló el cliente: ¿puede
    `agregar_ocupante` crear un Ocupante desconectado de la Persona de esta ficha (sin
    `persona_id`) si no tiene contacto? No -- `ck_personas_telefono_o_whatsapp` (constraint real de
    Postgres, ADR-0007) garantiza que TODA Persona tiene Teléfono o WhatsApp, así que
    `agregar_ocupante` siempre puede resolver la Persona correcta. No hizo falta ningún guard
    nuevo para este caso porque la base de datos ya lo hace estructuralmente imposible.
  - El picker de la tab (`components/_picker_apartamento.html`, issue 147) ya mostraba
    informativamente quién vive en cada unidad ANTES de elegirla -- eso no cambió, sigue siendo la
    transparencia real (no un bloqueo) que pedía el cliente.
- Autoservicio del residente (`/mis-datos`, `customer_verify.py`): **sin cambios de código**.
  Torre/Apartamento sigue siendo de solo lectura para el residente (staff-exclusivo); un residente
  que es Principal confirmado de su unidad sigue pudiendo gestionar (agregar/editar/dar de
  baja/promover) a los otros Ocupantes de esa MISMA unidad -- ya cumplía lo pedido, verificado que
  sigue intacto.

## Verificación

- Reescritos 3 tests que dependían del bloqueo viejo (ahora verifican el permiso + los datos
  resultantes: quién queda confirmado, quién principal, `apartamento_actual_id` correcto) + 1 sin
  cambios (picker informativo).
- Suite completa: 1044/1044. `test_customer_verify.py` (autoservicio del residente): 52/52 sin
  tocar ese archivo -- confirma que el punto 2 sigue intacto.
- Verificado en vivo contra `localhost:8010`: JESUS (sin unidad) asignado directo, vía tab
  Dirección, a la unidad de ANGELICA (T 01 · Apto 302, ya con Angelica como principal) -- éxito,
  Angelica se queda de principal, Jesus queda confirmado y NO principal, ambos con el ícono 👫 de
  [[156]]. Dato de prueba limpiado al terminar.
