# 380 — Registro del SMS de "Anunciado" perdido y "Eliminar" con 500 latente

**Pedido original (Jesús):** "soluciona como creas lo relacionado a los sms y el supuesto error 500" (hallazgo 6).
Respuesta de Jesús a la auditoría funcional (`.scratch/auditoria-funcional-2026-09-23/reporte.md`), 2026-09-23 — "soluciona estas cositas"; todo en localhost, el servidor de test se habla después.

**Status:** implementado, pendiente confirmar en vivo (localhost)

## Decisiones

- `/anunciar` y `/announce` hacen commit explícito ANTES de programar el envío en segundo plano (mismo criterio que
  `receive_action`): con FastAPI 0.104 el commit de `get_db` corre después de las BackgroundTasks, y el registro del SMS
  fallaba en silencio por la FK (el paquete aún no existía para otra sesión).
- `fk_registros_sms_paquete` pasa a `ON DELETE SET NULL` (migración): borrar un Anunciado conserva su registro de
  costo SMS, sin paquete, en vez de dar 500.

## Verificación

- `tests/web/test_registro_sms_anuncio.py` (3, fallaban antes): el SMS de `/anunciar` y de `/announce` queda en `registros_sms`; eliminar un Anunciado con su SMS registrado responde 303 y conserva el registro sin paquete. Migración `0059_registros_sms_fk_set_null`.
