# 07 — Retirar el campo viejo `segundo_contacto` de `/mis-datos`

**What to build:** quitar el campo de texto libre "Segundo contacto" (`Persona.segundo_contacto`) del formulario de Datos personales en `/mis-datos` — tanto de lectura como de escritura. Reemplazado por completo por el sistema de Ocupantes (tickets 01-06). La columna `Persona.segundo_contacto` se queda en la base de datos como dato histórico neutral, sin migración destructiva — mismo patrón ya usado antes con `documento`/`tipo_documento`. Sin intento de migrar el texto libre viejo a Ocupantes estructurados (no hay forma confiable de parsearlo).

**Blocked by:** 03

**Status:** done

- [x] El campo "Segundo contacto" ya no aparece en la plantilla de `/mis-datos`.
- [x] La ruta de `/mis-datos` ya no lee ni escribe ese campo del formulario.
- [x] La columna `Persona.segundo_contacto` sigue existiendo en el modelo y en la base de datos (sin migración destructiva).
- [x] Tests existentes que dependían de ese campo se actualizan o se retiran según corresponda.

## Implementación

- Quitado el `input_texto` de `segundo_contacto` en `customer/verify.html`; la ruta ya no lo lee del form ni lo pasa a `update_datos_personales`.
- `persona_service.update_datos_personales` SIGUE aceptando `segundo_contacto` (sin tocar) — lo sigue usando `customers_manage.py` (staff, `/residentes/{id}`), fuera de alcance de este ticket/spec.
- `test_guardar_datos_personales_es_parcial` actualizado (ya no ejercita ese campo); test nuevo confirma que el campo no aparece en el HTML.
- Suite completa: 499 passed.
