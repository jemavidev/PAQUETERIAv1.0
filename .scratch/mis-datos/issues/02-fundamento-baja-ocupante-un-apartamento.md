# 02 — Fundamento: marcado de baja en Ocupante + un teléfono = un apartamento activo a la vez

**What to build:** este es el prefactor que todos los tickets siguientes necesitan — sin UI propia todavía, pero completamente verificable a nivel de dominio. Agregar un marcador de baja a `Ocupante` (histórico, ej. `desvinculado_en: datetime` nullable — nunca se borra una fila real, mismo espíritu que `anonimizar_persona`/ADR-0001). Nueva función `dar_de_baja_ocupante(session, ocupante)` que marca la fila (nunca DELETE). `listar_ocupantes` (y cualquier función que arme un roster/lista de candidatos) debe filtrar solo Ocupantes ACTIVOS por defecto — debe existir también una forma de consultar los dados de baja (de solo lectura, para historial). Nueva regla: una Persona (por teléfono) solo puede ser Ocupante ACTIVO de un Apartamento a la vez — intentar asociarla (crear o asociar teléfono) a un segundo Apartamento mientras ya es activa en otro debe rechazarse con un mensaje claro.

**Blocked by:** 01

**Status:** done

- [x] `Ocupante` tiene un campo de baja histórico (migración Alembic); una fila dada de baja NUNCA se borra.
- [x] `dar_de_baja_ocupante(session, ocupante)` marca la fila como inactiva/dada de baja.
- [x] `listar_ocupantes` (u homólogo) por defecto solo trae Ocupantes activos.
- [x] Existe una forma de consultar también los Ocupantes dados de baja de un Apartamento (de solo lectura, para historial — "los datos permanecen pero solo para consulta").
- [x] Intentar que una Persona (por teléfono) sea Ocupante activo de un segundo Apartamento mientras ya es activa en otro lanza un error claro (`ValueError`) en el punto de creación/asociación de teléfono.
- [x] Tests de dominio cubren: dar de baja no borra la fila; el roster activo excluye dados de baja; el historial de dados de baja sigue consultable; el bloqueo de doble apartamento activo se dispara correctamente.

## Implementación

- `alembic/versions/0018_ocupante_desvinculado_en.py` — nueva columna `desvinculado_en` (nullable) en `ocupantes`.
- `Ocupante.desvinculado_en` en el modelo.
- `ocupante_service.py`: `listar_ocupantes(..., incluir_baja=False)`, `ocupante_de_persona` ahora solo activos, `_persona_activa_en_otro_apartamento` + guardia en `agregar_ocupante`, `dar_de_baja_ocupante` (idempotente, exige que el principal sea el último activo para poder irse), `promover_a_principal` ahora rechaza un Ocupante dado de baja.
- 8 tests nuevos en `tests/data_model/test_ocupante_service.py`.
- Suite completa: 464 passed (456 + 8 nuevos), sin regresiones — ningún test existente tenía el mismo teléfono activo en dos apartamentos a la vez.

## Corrección post-implementación

Al empezar el ticket 03 se detectó que esta nueva invariante rompía el flujo YA EXISTENTE de "cambiar de Torre/Apartamento" en `/mis-datos` (ticket 01 llama `agregar_ocupante`, que ahora rechaza con `ValueError` sin capturar -- 500 sin manejar). Corregido en `customer_verify.py`: al declarar un Apartamento nuevo, si la Persona ya es Ocupante activo de OTRO, se le da de baja automáticamente ahí primero (`dar_de_baja_ocupante` -- falla limpiamente, capturado como error de formulario, si todavía quedan otros Ocupantes activos dependiendo de ella como principal). 2 tests nuevos en `test_customer_verify.py` cubren el cambio exitoso y el rechazo. Suite completa: 466 passed.
