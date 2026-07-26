# 01 — Anunciado notifica + plantillas de mensaje en base de datos

**Qué construir:** `ANUNCIADO` se agrega a los eventos que disparan notificación. Los textos de mensaje se guardan en una tabla nueva (`plantillas_notificacion`), con fallback al texto hardcodeado actual si no hay una plantilla personalizada para ese evento/motivo.

**Bloqueado por:** Ninguno — el Grupo 1 ya está implementado.

**Estado:** ready-for-agent

- [ ] `_EVENTOS_QUE_NOTIFICAN` en `notificacion_service.py` incluye `ANUNCIADO`.
- [ ] Migración Alembic crea `plantillas_notificacion`: `id`, `evento`, `motivo` (nullable), `texto`, `updated_at`; único por `(evento, motivo)`.
- [ ] `construir_mensaje` busca una plantilla personalizada por `(evento, motivo si CANCELADO)`; si existe, renderiza con placeholders (`{recipient_name}`, `{motivo}`); si no, usa el texto por defecto actual (comportamiento de hoy, sin cambios).
- [ ] `notificar_evento` se llama también tras `announce` (en la ruta `/anunciar` y en `/announce`).
- [ ] `tests/data_model/test_notificacion_service.py` extendido: `ANUNCIADO` notifica; sin plantilla usa el default; con plantilla personalizada la usa.
- [ ] Suite completa (`pytest`) pasa.
