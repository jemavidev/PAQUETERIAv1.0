# 04 — Historial de auditoría de cambios en plantillas

**Qué construir:** nueva tabla `plantillas_notificacion_historial` (append-only, sin UPDATE ni DELETE): `id`, `plantilla_id` (FK a `plantillas_notificacion.id`), `evento`, `motivo` (nullable), `canal` (denormalizados, para consultar sin join), `usuario_id` (FK a `Usuario`, quién hizo el cambio), `texto_anterior` (nullable — `NULL` la primera vez que se personaliza una fila), `texto_nuevo`, `asunto_anterior`/`asunto_nuevo` (nullable, solo relevantes para `EMAIL`), `creado_en`. `guardar_plantilla` inserta una fila de historial en cada guardado exitoso. Sin UI ni ruta de consulta en esta rebanada — solo el registro queda disponible para consulta directa a BD o trabajo futuro.

**Bloqueado por:** 01 — puede construirse en paralelo a 02/03, no depende de la UI.

**Estado:** ready-for-agent

- [ ] Migración Alembic crea `plantillas_notificacion_historial` con las columnas descritas.
- [ ] `guardar_plantilla` inserta una fila de historial en cada llamada exitosa, con `texto_anterior`/`asunto_anterior` de la fila previa (o `NULL` si es la primera personalización) y `texto_nuevo`/`asunto_nuevo` con los valores guardados.
- [ ] El historial nunca se edita ni se borra (append-only).
- [ ] Test de dominio: guardar la misma plantilla dos veces deja dos registros de historial; el segundo tiene como `texto_anterior` el texto guardado en la primera llamada.
- [ ] Suite completa (`pytest`) pasa.
