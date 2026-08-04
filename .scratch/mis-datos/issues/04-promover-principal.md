# 04 — Promover a un Ocupante-con-teléfono como nuevo principal

**What to build:** botón "Promover a principal" junto a cada Ocupante-con-teléfono (que no sea ya el principal) en la sección de gestión del ticket 03. Reutiliza `ocupante_service.promover_a_principal`, que YA existe y ya implementa la regla completa (exige teléfono en el promovido, degrada al anterior principal en la misma transacción, sin borrarlo ni darlo de baja) — este ticket es solo wiring de ruta/UI, sin cambios de lógica de dominio.

**Blocked by:** 03

**Status:** done

- [x] El principal ve un botón "Promover a principal" en cada Ocupante-con-teléfono de su Apartamento que no sea ya el principal.
- [x] Al usarlo, el Ocupante seleccionado pasa a ser principal; el anterior principal queda como Ocupante activo normal (no se da de baja, sigue en el roster).
- [x] El botón no aparece (o está deshabilitado) en Ocupantes sin teléfono.
- [x] Test cubre el flujo end-to-end vía la ruta/UI nueva (el dominio ya tiene tests propios).

## Implementación

- `POST /mis-datos/ocupantes/{id}/promover` en `customer_verify.py`, protegida por `_ocupante_gestionable_por`, wrapping `promover_a_principal`.
- Botón "Promover a principal" en `customer/verify.html`, solo para Ocupantes no-principales CON teléfono.
- 2 tests nuevos en `test_customer_verify.py`. Suite completa: 488 passed.
