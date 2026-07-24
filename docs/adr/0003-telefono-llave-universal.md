---
status: accepted
---

# El Teléfono es la llave universal de la Persona

La identidad estable de una **Persona** se ancla en su **Teléfono** (forma canónica normalizada, único), no en un id opaco con teléfono nullable. Un **Destinatario sin teléfono** se representa como un **nombre bajo el Teléfono del Anunciante**, no como una Persona con llave propia. Así ninguna identidad del sistema carece de Teléfono.

## Considered Options

- **Surrogate-id con teléfono nullable** (Persona con id propio y teléfono opcional). Rechazado: reintroduce "personas sin llave" y revive el `display_name` huérfano del modelo viejo — nombres que no llevan a ninguna identidad, apartamento ni historia.
- **Cliente = Teléfono, rígido** (el modelo viejo: `phone unique` *es* el cliente). Rechazado: impide que una identidad estable amplíe sus datos o cambie de Apartamento; confunde la llave con la entidad.

## Consequences

- La Persona **es** una entidad (con surrogate key propia para FKs), pero su **identidad de dominio** y su unicidad viven en el Teléfono canónico.
- El registro es **implícito**: la Persona se crea al anunciar (teléfono + nombre) y amplía datos desde `/customer/verify`.
- Un "nombre sin teléfono" no tiene existencia fuera del snapshot del Paquete (ver [ADR-0001](0001-paquete-snapshot-inmutable.md) y `CONTEXT.md`).
