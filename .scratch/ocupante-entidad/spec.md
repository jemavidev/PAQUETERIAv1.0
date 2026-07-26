# Entidad Ocupante (implementación de ADR-0006)

Fuente: `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 4. `docs/adr/0006-ocupante-residentes-sin-persona-propia.md` y `CONTEXT.md` (sección Ocupante) ya resolvieron el modelo conceptual — esta spec implementa la entidad real que faltaba.

## Problem Statement

El modelo conceptual de Ocupante ya está resuelto (ADR-0006): un Apartamento puede tener varios residentes reconocidos, exactamente uno "principal" (con Teléfono obligatorio, respaldado por una Persona real), y el resto opcionalmente con Teléfono. Hoy no existe ninguna tabla ni función de dominio para esto — es prerrequisito de la rebanada de `/announce` (Grupo 6), que necesita declarar/editar Ocupantes de un Apartamento en el mismo flujo que anuncia un paquete.

## Solution

Nueva entidad `Ocupante`, ligada a un Apartamento. Funciones de dominio para: crear/reutilizar un Ocupante, promoverlo a principal, degradar al principal actual (reemplazándolo por otro), y listar los Ocupantes de un Apartamento. Cada Apartamento con al menos un Ocupante siempre tiene exactamente uno marcado principal.

## User Stories

1. Como desarrollador, quiero una tabla `ocupantes` ligada a `apartamentos`, para persistir el padrón de residentes de una unidad.
2. Como desarrollador, quiero que un Ocupante con Teléfono esté respaldado por una Persona real (mismo Teléfono canónico), para que ADR-0003 se mantenga intacto.
3. Como desarrollador, quiero que la base de datos garantice que nunca haya más de un Ocupante principal por Apartamento, para no depender solo de disciplina a nivel de aplicación.
4. Como miembro del staff, quiero poder marcar un Ocupante sin teléfono como principal SOLO si primero se le asocia un Teléfono válido, para respetar la regla de que el principal siempre tiene Teléfono.
5. Como miembro del staff, quiero poder promover a cualquier Ocupante-con-teléfono de un Apartamento a principal, degradando automáticamente al que lo era, para corregir quién es el contacto por defecto de la unidad.
6. Como miembro del staff, quiero poder agregar un Ocupante sin teléfono (solo nombre) a un Apartamento, para reconocer residentes que no tienen celular propio.
7. Como miembro del staff, quiero poder agregar un Ocupante con teléfono a un Apartamento — reutilizando la Persona si el teléfono ya existe, o creándola si no —, para no duplicar identidades.
8. Como desarrollador, quiero poder listar todos los Ocupantes de un Apartamento (para que la vista de `/announce`, Grupo 6, los muestre y edite), para tener la base lista antes de esa rebanada.

## Implementation Decisions

- **Tabla `ocupantes`** (nueva, migración Alembic tras `0009`): `id` (UUID PK), `apartamento_id` (FK a `apartamentos`, NOT NULL), `persona_id` (FK a `personas`, NULLABLE — presente cuando el Ocupante tiene Teléfono), `nombre` (String, NOT NULL), `es_principal` (Boolean, NOT NULL, default False), `created_at`/`updated_at`.
- **Único principal por apartamento**: índice único parcial (`WHERE es_principal`) sobre `apartamento_id` — a nivel de base de datos, no solo de aplicación.
- **`nombre` se mantiene en el Ocupante** aunque tenga `persona_id` (no se deriva solo del join) — evita depender de un join para listar/mostrar, y permite que el nombre del Ocupante y el de la Persona diverjan momentáneamente si se editan por separado (caso normal: el staff corrige uno sin tocar el otro).
- **Funciones de dominio nuevas** (`ocupante_service.py`):
  - `agregar_ocupante(session, apartamento, nombre, telefono=None) -> Ocupante`: si `telefono` viene, hace `get_or_create_persona` y liga `persona_id`; si no, crea un Ocupante liviano sin Persona. Si el Apartamento no tiene NINGÚN Ocupante todavía, este primer Ocupante debe tener teléfono y se marca principal automáticamente (invariante: un Apartamento con Ocupantes siempre tiene un principal). Si ya hay Ocupantes y este es el primero CON teléfono, no se auto-promueve (el principal ya existe) — la promoción es un acto explícito aparte.
  - `promover_a_principal(session, ocupante) -> Ocupante`: exige que el Ocupante tenga `persona_id` (Teléfono válido) — si no, `ValueError`. Degrada al principal anterior del mismo Apartamento (le pone `es_principal=False`) y marca a este como principal. Debe ejecutarse de forma que nunca haya un instante con 0 o 2 principales visibles (misma transacción).
  - `listar_ocupantes(session, apartamento) -> list[Ocupante]`: todos los Ocupantes de un Apartamento, principal primero.
- **Relación con `declare_unit`/`get_or_create_apartamento` existentes** (usadas hoy por `/announce` para "declarar unidad en lote"): quedan SIN CAMBIOS en esta rebanada — son la base sobre la que el Grupo 6 va a construir la integración completa (declarar unidad + Ocupantes en un mismo formulario). Esta rebanada solo entrega la entidad y sus funciones; cablearla en la UI de `/announce` es el Grupo 6.
- **No se toca** `Persona.apartamento_actual_id` (el mecanismo existente de "apartamento actual" de una Persona) — un Ocupante-con-Persona normalmente comparte el mismo Apartamento en ambos lados, pero esta rebanada no fuerza esa sincronización automáticamente; queda como nota para el Grupo 6, que sí conecta ambos flujos.

## Testing Decisions

- Seam de dominio (`tests/data_model/test_ocupante_service.py`, nuevo): agregar Ocupante sin teléfono; agregar Ocupante con teléfono (reutiliza o crea Persona); el primer Ocupante de un Apartamento queda principal automáticamente; agregar un segundo Ocupante NO lo hace principal; promover un Ocupante sin teléfono falla con `ValueError`; promover un Ocupante con teléfono degrada al principal anterior (queda exactamente 1 principal, nunca 0 ni 2); listar Ocupantes de un Apartamento.
- Migración: extender `test_parity_esquema_orm` y `test_migration_graph` (ya genéricos) — deben seguir pasando sin cambios, confirmando que la tabla nueva no diverge del ORM.
- Prior art: mismo patrón de seam que `test_apartamento_service.py` y `test_declarar_unidad.py` (fixtures de Postgres efímero, sin mocks).

## Out of Scope

- Cablear Ocupante en la UI de `/announce` (declarar unidad + anunciar en el mismo formulario) — Grupo 6, spec aparte, depende de esta.
- Editar/desasociar un Ocupante desde `/mis-datos` (mencionado en el Grupo 4 original pero es UI de cliente, no de esta rebanada de dominio) — se revisará junto con el Grupo 6 o una rebanada de UI de cliente aparte si hace falta.
- Sincronizar automáticamente `Persona.apartamento_actual_id` al agregar/promover un Ocupante — anotado como nota para el Grupo 6.

## Further Notes

Esta rebanada bloquea al Grupo 6 (`/announce` completo). El Grupo 7 (Residentes) también depende de esto para mostrar el teléfono del Ocupante en la ficha de un cliente.
