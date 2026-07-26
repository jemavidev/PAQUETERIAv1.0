# Residentes: mostrar Ocupantes del apartamento

Fuente: `.scratch/ajustes-post-referencia-funcional/REQUERIMIENTOS.md`, Grupo 7. La mayoría de las notas de este grupo confirmaron el comportamiento **actual** sin cambios (editar ya abierto a cualquier rol; eliminar sigue exclusivo de `ADMIN`, ADR-0005; auditoría ya existe a nivel de BD). El único cambio real es mostrar el teléfono/padrón de Ocupantes de la unidad.

## Problem Statement

El staff, al ver la ficha de un residente en `/residentes/{id}`, no tiene forma de ver quién más vive en el mismo apartamento (los Ocupantes, ADR-0006) ni sus teléfonos — tendría que ir a `/announce` y volver a declarar la unidad para verlo.

## Solution

La ficha de `/residentes/{id}` muestra, si la Persona tiene un Apartamento actual, la lista de Ocupantes de esa unidad (nombre + teléfono si tiene + si es el principal) — de solo lectura desde aquí. La edición de Ocupantes (agregar, promover) sigue siendo responsabilidad de `/announce` (Grupo 6) — no se duplica esa UI.

## User Stories

1. Como miembro del staff, quiero ver los Ocupantes del apartamento de un residente al ver su ficha, para saber quién más vive ahí sin ir a otra pantalla.
2. Como miembro del staff, quiero ver cuál Ocupante es el principal, para saber a quién le llega la notificación por defecto de esa unidad.
3. Como miembro del staff, quiero ver el teléfono de los Ocupantes que lo tienen, para poder contactarlos si hace falta.

## Implementation Decisions

- `customers_manage_detail` (ruta `/residentes/{id}`) agrega al contexto la lista de `listar_ocupantes(db, apartamento)` cuando la Persona tiene `apartamento_actual_id`.
- La plantilla `customers_manage/detail.html` muestra esa lista (nombre, teléfono si tiene, badge "Principal" en el que corresponda) — de solo lectura, sin formularios de edición aquí.
- Sin cambios en permisos: editar sigue abierto a cualquier rol de staff, eliminar sigue exclusivo de `ADMIN` (confirmado, no se toca `require_admin`).

## Testing Decisions

- Seam web (`tests/web/test_customers_manage.py`, extender): la ficha muestra los Ocupantes del apartamento cuando la Persona tiene uno asignado, incluyendo el badge de principal; no muestra nada si no tiene apartamento.

## Out of Scope

- Editar/agregar/promover Ocupantes desde `/residentes` — sigue siendo `/announce` (Grupo 6).
- Cambios de permisos de edición/eliminación — confirmado sin cambios.
