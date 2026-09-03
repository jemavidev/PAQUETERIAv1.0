# 03 — `/paquetes`: cancelar un paquete usa el catálogo (incluye "Otro" y validación server-side)

**What to build:** el modal "Cancelar paquete" de `/paquetes` muestra como opciones las etiquetas del catálogo de motivos (en orden de creación), en vez del enum fijo. El caso especial "Otro" sigue revelando el campo de texto libre igual que hoy. El servidor valida que el motivo recibido exista en el catálogo (o sea "Otro" con texto no vacío) antes de cancelar. El `{motivo}` que aparece en las notificaciones de CANCELADO deja de forzar mayúscula/capitalización — se muestra tal cual el ADMIN lo escribió o el STAFF lo tecleó.

Contexto: spec completo en `.scratch/motivos-cancelacion-catalogo/spec.md`. Depende del seam de dominio del ticket 01 (`motivo_cancelacion_service.py`); es independiente del ticket 02 (ambos solo dependen de 01, se pueden trabajar en cualquier orden).

**Blocked by:** 01 — Catálogo de motivos: esquema, dominio y migración de datos existentes.

**Status:** done · 1352 tests verdes

- [x] `_render_lista` (en `packages.py`) pasa `listar_motivos(db)` al template en vez de `list(MotivoCancelacion)`; el radiogroup de `packages/_resultados.html` sigue con el mismo mecanismo (radio real oculto + `peer-checked`), solo cambia su fuente de datos.
- [x] El bloque especial de "Otro" (JS que revela `cancelar-otro-wrap-{{ p.id }}`, y la comparación en `cancel_action`) pasa a comparar contra el literal `"Otro"` (la etiqueta legible sembrada por la migración del ticket 01), no contra `"OTRO"`.
- [x] `cancel_action` valida server-side que el `motivo` recibido exista en el catálogo (`motivo_valido`) o sea el caso especial "Otro" con `motivo_otro` no vacío; si no, rechaza con un error claro y el paquete no transiciona — mismo criterio de "el servidor no confía en la forma del POST" que ya usa el resto de `admin.py`/`packages.py`.
- [x] `notificacion_service._variables()` y `variables_ejemplo()` dejan de aplicar `_motivo_legible()` sobre `motivo` — usan el valor tal cual (la función se eliminó por completo, ticket 04 confirmó que no quedaba ningún otro caller).
- [x] Tests extendidos en `tests/web/test_packages.py`: el modal muestra exactamente las etiquetas del catálogo actual; cancelar con un motivo del catálogo persiste `cancel_reason` igual a esa etiqueta; cancelar con "Otro" + `motivo_otro` persiste el texto libre tecleado (sin cambios de comportamiento); cancelar con un motivo que no existe en el catálogo ni es "Otro" devuelve error y el paquete no transiciona.
- [x] Test extendido en `tests/data_model/test_notificacion_service.py`: el `{motivo}` resuelto en un mensaje de CANCELADO es el texto tal cual, sin capitalización ni reemplazo de guiones bajos.
