# 01 — Tab "Dirección" de `/residentes` crea/liga un Ocupante confirmado

**What to build:** asignar Torre+Apartamento a un cliente desde la tab "Dirección" de la ficha de cliente (`/residentes/{id}`) deja de escribir `Persona.apartamento_actual_id` de forma aislada. En su lugar, da de alta (o liga, si ya existe una Persona con ese Teléfono/WhatsApp) un `Ocupante` **confirmado automáticamente** para esa Persona en la unidad elegida -- reusando el mecanismo ya existente de alta de Ocupante (`agregar_ocupante`) seguido de confirmación (`confirmar_ocupante`, staff actor = quien hace la asignación), no un camino nuevo. Si la unidad estaba vacía, esa Persona queda promovida a Principal en el mismo acto (comportamiento ya existente de `confirmar_ocupante`, sin necesidad de reimplementarlo). Si la Persona ya es Ocupante activo de otra unidad, la asignación se bloquea con el mismo mensaje de error que existe hoy. Quitar la Torre/Apartamento (enviando el formulario con ambos campos vacíos) da de baja (`dar_de_baja_ocupante`) al Ocupante correspondiente, en vez de solo limpiar `apartamento_actual_id`.

Con esto, `Persona.apartamento_actual_id` queda siempre derivado del padrón de `Ocupante`, sin ningún camino de escritura que lo desincronice -- cualquier Persona con apartamento asignado por esta vía queda visible para cualquier otra parte del sistema que consulte el padrón de Ocupantes (incluido el camino Torre+Apartamento de `/announce`).

**Blocked by:** None — puede arrancar de inmediato.

**Status:** implementado

## Hallazgos de code-review (corregidos antes de desplegar)

- **Comentario desactualizado (Standards):** `_aviso_reasignacion_bloqueada` seguía apuntando a "el guard real en `customers_manage_asignar_apartamento`" -- ese guard ya no vive ahí, se movió a `ocupante_service.reasignar_apartamento`. Corregido.
- **Decisión de producto no documentada (Spec):** el criterio de abajo decía "mismo mensaje de error que hoy" para el bloqueo por Ocupante activo en otra unidad -- la implementación reusa deliberadamente `_MENSAJE_YA_OCUPANTE_ACTIVO` (el mensaje que ya usa `agregar_ocupante` para este mismo caso) en vez de mantener el texto viejo del guard manual, para tener una sola fuente de verdad. Es una decisión mejor que la letra original del ticket, pero ningún test lo dejaba explícito -- corregido: los tests ahora verifican el contenido del mensaje, y este ticket documenta la decisión.
- **Test faltante (Spec):** el criterio de "consultable desde la tab Residentes" solo tenía cobertura para `/announce`, no para la propia ficha de `/residentes`. Agregado `test_direccion_asigna_visible_de_inmediato_en_la_tab_residentes`.

- [x] Asignar Torre+Apartamento desde "Dirección" a una unidad vacía crea un Ocupante confirmado y lo promueve a Principal.
- [x] Asignar Torre+Apartamento desde "Dirección" a una unidad que ya tiene Principal crea un Ocupante confirmado, no-principal.
- [x] Asignar Torre+Apartamento desde "Dirección" a una Persona que ya es Ocupante activo de OTRA unidad se bloquea (mensaje reusado de `agregar_ocupante`, ver nota de code-review arriba).
- [x] Quitar la Torre/Apartamento desde "Dirección" (campos vacíos) da de baja al Ocupante correspondiente (`desvinculado_en` queda con fecha).
- [x] El Ocupante creado por esta vía es consultable inmediatamente desde la tab "Residentes" de la misma ficha, y desde el camino Torre+Apartamento de `/announce`.
- [x] Los tests existentes de `/residentes` (búsqueda, ficha, tab Dirección) siguen pasando sin romperse.
- [x] Verificación manual en navegador real (contra el ambiente local persistente, `scripts/paquetex_dev_up.sh` + Playwright): asignar Torre 6/101 desde "Dirección" -- queda "Residente principal", visible de inmediato en `/announce` con el código Torre+Apto (`06101`); quitar la dirección -- vuelve a "Sin apartamento asignado". Sin errores de consola en ningún paso.
