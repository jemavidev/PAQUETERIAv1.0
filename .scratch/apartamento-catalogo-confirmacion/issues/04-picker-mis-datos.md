# 04 — Picker Torre/Apartamento en `/mis-datos` (residente)

**What to build:** el bloque "declarar apartamento" de `/mis-datos` (`customer_verify.py`) reemplaza los dos inputs de texto libre (Torre, Apartamento) por selección de las 804 unidades del catálogo sembrado (ticket 02) — ya no se le pide Conjunto al residente en ningún momento. Se retira el candado actual "Tu conjunto todavía no ha sido asignado por el staff — avísales en portería..." (`customer_verify.py:228-247`): quedó obsoleto, con catálogo cerrado y Conjunto único cualquier residente puede declarar su unidad directamente sin que staff "asigne" nada antes.

**Blocked by:** 03.

**Status:** done

- [x] El formulario de `/mis-datos` ofrece Torre + Apartamento como selección de las 804 unidades reales (dos `<select>`, Apartamento repoblado por JS vanilla según la Torre elegida), no como texto libre.
- [x] Ya no existe ningún campo ni mención de Conjunto en el bloque editable (el principal).
- [x] El mensaje/candado "conjunto todavía no ha sido asignado por el staff" se retiró junto con la lógica que lo generaba — ya no existe el estado "sin apartamento → mensaje muerto"; ahora siempre se ve el picker, vacío o con la selección actual.
- [x] Declarar una unidad válida sigue funcionando igual que hoy (actualiza `apartamento_actual_id`, crea/reusa el Ocupante vía `declare_unit`, idempotente en reenvíos) — la ruta ya recibía `torre`/`apartamento` como texto plano del `<form>`, un `<select>` manda el mismo tipo de valor, cero cambios de backend adicionales sobre lo que dejó el ticket 03.
- [x] Un Ocupante no-principal sigue viendo Torre/Apartamento/Conjunto de solo lectura, sin cambios (rama aparte del template, no tocada).
- [x] Tests web (`test_customer_verify.py`) actualizados: casos que hoy prueban texto libre pasan a seleccionar del catálogo; los 2 tests del candado de conjunto ya obsoleto se reescribieron para probar el comportamiento nuevo (picker siempre visible; sin campo de Conjunto).

## Implementación

- **Dominio:** `apartamento_service.listar_catalogo_por_torre(session) -> dict[str, list[str]]` — el catálogo agrupado por Torre (orden numérico real, no alfabético: `TORRE 10` no cae entre `TORRE 1` y `TORRE 2`), Apartamentos de cada Torre en orden numérico. Reutilizable por el ticket 05 (mismo picker, lado staff).
- **Design system:** macro nuevo `input_select` en `components/_inputs.html` — mismo lenguaje visual que `input_texto` (ícono + subrayado, sin label visible, placeholder como primera opción), genérico para cualquier lista cerrada de opciones.
- **Web:** `customer_verify.py` agrega `catalogo_torres` a `_contexto_base` (single source, cubre GET y cualquier re-render de error). `customer/verify.html`: el bloque "apto" ya no depende de `{% if apartamento %}` para decidir candado vs. formulario — el principal siempre ve el picker (pre-llenado si ya tiene unidad); JS vanilla al final del archivo repuebla el `<select>` de Apartamento según la Torre elegida, embebiendo `catalogo_torres` vía `|tojson`.
- **Tests:** 3 nuevos de dominio (`test_catalogo_por_torre.py`) + 2 reescritos en `test_customer_verify.py` (los del candado obsoleto).
- **Suite completa:** 583 passed (mismos 6 fallos preexistentes de `test_layout.py`).
- **Nota de verificación:** validado por HTML-assertion en los tests automatizados (incluye el atributo `selected` exacto de las opciones), no se probó clic a clic en navegador real dentro de esta sesión.
