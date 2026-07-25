---
status: accepted
---

# "Eliminar cliente" es anonimización, nunca un DELETE de la fila Persona

`paquetes.announced_by_persona_id` es una FK **real y `NOT NULL`** hacia `personas.id` (`fk_paquetes_anunciante`). Cualquier Persona que haya anunciado al menos un Paquete queda referenciada permanentemente por ese historial. Por eso "eliminar un cliente" (`/customers/manage`, brief §7) se implementa como **anonimización de campos personales**, manteniendo la fila y su `id` intactos — nunca un `DELETE` real.

## Considered Options

- **`DELETE` real de la fila `Persona`.** Rechazado: rompe la FK de cualquier Paquete que haya anunciado (violación de integridad referencial), o exigiría un `ON DELETE CASCADE` que borraría paquetes históricos — contradice el invariante de snapshot inmutable (ADR-0001, "los datos permanecen de principio a fin en cada paquete").
- **Anonimización (elegida):** se conserva la fila `Persona` (y su `id`, para que la FK nunca se rompa); se limpian los campos personales (`nombre`, `email`, `documento`, `tipo_documento`, `segundo_contacto`) y se **reemplaza `telefono`** por un valor sintético no enrutable y único (nunca un número real reciclable) — así, si la persona real vuelve a anunciar con su número real, el sistema crea una **Persona nueva** (la identidad "olvidada" no resucita). Se desvincula del Apartamento (`apartamento_actual_id = NULL`, mismo efecto que `move_resident(..., None)`).
- Se agrega un timestamp `eliminado_en` (nullable) para marcar el estado y excluir/distinguir estas Personas en búsquedas de staff.

## Consequences

- Los **snapshots de Paquetes ya anunciados** (`recipient_name`, `recipient_phone`, `announced_by_phone` — columnas de texto copiadas, no FK) **no se tocan**: siguen mostrando los datos de entonces, coherente con ADR-0001.
- El **teléfono deja de ser buscable/reutilizable** para esa identidad tras la anonimización — es la forma en que "olvidar" a alguien es real y no solo cosmética.
- Esta es la única vía de "borrado" del rebuild; no existe (ni se prevé) un `DELETE` real de `Persona` mientras la FK `fk_paquetes_anunciante` exista.
