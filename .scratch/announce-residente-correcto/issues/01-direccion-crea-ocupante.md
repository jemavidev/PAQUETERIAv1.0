# 01 — Tab "Dirección" de `/residentes` crea/liga un Ocupante confirmado

**What to build:** asignar Torre+Apartamento a un cliente desde la tab "Dirección" de la ficha de cliente (`/residentes/{id}`) deja de escribir `Persona.apartamento_actual_id` de forma aislada. En su lugar, da de alta (o liga, si ya existe una Persona con ese Teléfono/WhatsApp) un `Ocupante` **confirmado automáticamente** para esa Persona en la unidad elegida -- reusando el mecanismo ya existente de alta de Ocupante (`agregar_ocupante`) seguido de confirmación (`confirmar_ocupante`, staff actor = quien hace la asignación), no un camino nuevo. Si la unidad estaba vacía, esa Persona queda promovida a Principal en el mismo acto (comportamiento ya existente de `confirmar_ocupante`, sin necesidad de reimplementarlo). Si la Persona ya es Ocupante activo de otra unidad, la asignación se bloquea con el mismo mensaje de error que existe hoy. Quitar la Torre/Apartamento (enviando el formulario con ambos campos vacíos) da de baja (`dar_de_baja_ocupante`) al Ocupante correspondiente, en vez de solo limpiar `apartamento_actual_id`.

Con esto, `Persona.apartamento_actual_id` queda siempre derivado del padrón de `Ocupante`, sin ningún camino de escritura que lo desincronice -- cualquier Persona con apartamento asignado por esta vía queda visible para cualquier otra parte del sistema que consulte el padrón de Ocupantes (incluido el camino Torre+Apartamento de `/announce`).

**Blocked by:** None — puede arrancar de inmediato.

**Status:** ready-for-agent

- [ ] Asignar Torre+Apartamento desde "Dirección" a una unidad vacía crea un Ocupante confirmado y lo promueve a Principal.
- [ ] Asignar Torre+Apartamento desde "Dirección" a una unidad que ya tiene Principal crea un Ocupante confirmado, no-principal.
- [ ] Asignar Torre+Apartamento desde "Dirección" a una Persona que ya es Ocupante activo de OTRA unidad se bloquea, mismo mensaje de error que hoy.
- [ ] Quitar la Torre/Apartamento desde "Dirección" (campos vacíos) da de baja al Ocupante correspondiente (`desvinculado_en` queda con fecha).
- [ ] El Ocupante creado por esta vía es consultable inmediatamente desde la tab "Residentes" de la misma ficha, y desde el camino Torre+Apartamento de `/announce`.
- [ ] Los tests existentes de `/residentes` (búsqueda, ficha, tab Dirección) siguen pasando sin romperse.
- [ ] Verificación manual en navegador real (skill `run`): asignar y quitar una unidad desde "Dirección", confirmar que se refleja correctamente en la tab "Residentes" y en `/announce` (Torre+Apto), sin errores de consola.
