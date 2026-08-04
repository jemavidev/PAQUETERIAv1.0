# 03 — El principal gestiona sus Ocupantes desde `/mis-datos`

**What to build:** nueva sección en `/mis-datos` (visible solo si el cliente logueado es el Ocupante principal de un Apartamento) donde puede: crear un Ocupante nuevo (nombre + teléfono opcional, máximo **5 Ocupantes activos** por Apartamento); asociar teléfono a un Ocupante ya existente sin teléfono (función nueva `asociar_telefono_a_ocupante(session, ocupante, telefono)`, reutiliza `get_or_create_persona`, respeta el bloqueo de "un teléfono, un apartamento" del ticket 02); desvincular el teléfono de un Ocupante no-principal (función nueva `desvincular_telefono_ocupante`, el Ocupante sigue existiendo, solo pierde el teléfono); y dar de baja completo a un Ocupante no-principal (usa `dar_de_baja_ocupante` del ticket 02). El teléfono del Ocupante PRINCIPAL nunca puede desvincularse directamente — el principal siempre debe tener teléfono (ver ticket 04 para cómo cambia quién es principal).

**Blocked by:** 01, 02

**Status:** done

- [x] El principal ve una tarjeta "Mis Ocupantes" en `/mis-datos` listando los Ocupantes activos de su Apartamento (nombre, teléfono si tiene, quién es el principal).
- [x] Puede crear un Ocupante nuevo con nombre + teléfono opcional; al llegar a 5 Ocupantes activos, la creación se deshabilita con un mensaje claro.
- [x] Puede asociar teléfono a un Ocupante existente sin teléfono; si ese teléfono ya es Ocupante activo de OTRO apartamento, se rechaza con mensaje claro (reusa el bloqueo del ticket 02).
- [x] Puede desvincular el teléfono de un Ocupante no-principal (vuelve a ser un registro liviano, solo nombre).
- [x] Intentar desvincular el teléfono del Ocupante PRINCIPAL se rechaza explícitamente.
- [x] Puede dar de baja completo a un Ocupante no-principal (usa el marcado histórico del ticket 02, nunca borra).
- [x] Tests cubren cada acción y cada rechazo (límite de 5, teléfono ya activo en otro apartamento, intento de desvincular el teléfono del principal).

## Implementación

- Dominio: `ocupante_activo_de_persona`, `MAX_OCUPANTES_ACTIVOS=5` + guardia en `agregar_ocupante`, `asociar_telefono_a_ocupante`, `desvincular_telefono_ocupante` (rechaza sobre el principal).
- Rutas nuevas en `customer_verify.py`: `POST /mis-datos/ocupantes` (crear), `POST /mis-datos/ocupantes/{id}/telefono` (asociar), `POST /mis-datos/ocupantes/{id}/desvincular-telefono`, `POST /mis-datos/ocupantes/{id}/baja` — todas protegidas por `_ocupante_gestionable_por` (403 si la Persona no es principal del apartamento del Ocupante). Contexto de plantilla refactorizado a `_contexto_base`/`_render_con_error` para no duplicar entre GET y cada acción.
- Plantilla `customer/verify.html`: tarjeta "Mis Ocupantes" nueva, gateada por `es_principal_de_apartamento`.
- 15 tests nuevos en `test_customer_verify.py` (roster visible/oculto, crear con/sin teléfono, límite de 5, asociar/desvincular teléfono, dar de baja, rechazo de desvincular al principal, 403 entre apartamentos ajenos).
- Suite completa: 486 passed.
