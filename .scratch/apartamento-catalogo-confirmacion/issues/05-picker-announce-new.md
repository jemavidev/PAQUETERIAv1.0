# 05 — Picker Torre/Apartamento en `/announce-new` (staff)

**What to build:** el bloque "Apartamento" de `/announce-new` (`announce_new.py`), donde hoy el staff escribe Conjunto + Torre + Apartamento a mano, pasa a ofrecer selección de las 804 unidades del catálogo sembrado (ticket 02) para Torre + Apartamento — el campo de Conjunto se retira del formulario por completo (ya no lo escribe nadie, es implícito).

**Blocked by:** 03.

**Status:** done

- [x] El formulario de `/announce-new` ofrece Torre + Apartamento como selección de las 804 unidades reales (mismo picker con `<select>` + JS del ticket 04, reutilizando `listar_catalogo_por_torre`).
- [x] El input de Conjunto desaparece del formulario por completo — ni se lee del POST ni se muestra.
- [x] Declarar la unidad (con sus residentes) sigue funcionando igual que hoy vía `declare_unit`, incluida la guardia de idempotencia (no duplica un residente ya activo en la unidad) — sin cambios de esa lógica, solo de cómo llegan Torre/Apartamento.
- [x] La validación se ajusta a "Completa Torre y Apartamento, o deja los dos vacíos" (ya no menciona Conjunto).
- [x] Tests web de `announce_new` actualizados: sin `conjunto` en `_CAMPOS_MARCABLES` ni en las aserciones de formulario visible.

## Implementación

- **Web:** `announce_new.py` deja de leer `conjunto` del formulario; `_CAMPOS_MARCABLES`/`partes_apto` pasan a solo `torre`/`apartamento`; los 3 `TemplateResponse` (GET, error, éxito) agregan `catalogo_torres` vía `listar_catalogo_por_torre` (reutilizada del ticket 04, sin duplicar lógica).
- **Template:** `announce_new/form.html` reemplaza los 3 `input_texto` (Conjunto/Torre/Apartamento) por 2 `input_select` (Torre/Apartamento); mismo bloque de JS cascada Torre→Apartamento que `customer/verify.html` (ticket 04), con sus propios ids (`announce-new-torre`/`announce-new-apartamento`) para no chocar si ambas páginas compartieran contexto.
- **Design system:** `input_select` gana soporte de `autofocus` (paridad con `input_texto`) — el ticket 04 no lo había necesitado.
- **Suite completa:** 583 passed (mismos 6 fallos preexistentes de `test_layout.py`).
- **Nota de verificación:** igual que el ticket 04, validado por HTML-assertion en tests automatizados, no se probó clic a clic en navegador real.
