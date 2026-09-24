# 05 — Preferencias de notificación

**What to build:** los residentes que configuraron sus avisos en la v1 conservan esa configuración en la v2 (ver `../spec.md`, historia 21, y el mapeo de `.scratch/migracion-datos-legacy/estructura-migracion.md` §2.5).

**Blocked by:** 01 — Bala trazadora: Personas espejo de punta a punta

**Status:** reemplazado — decisión 2026-09-24 (opción C): las preferencias de la v1 no se importan

- [x] Cada fila de `customer_preferences` se convierte en filas `PersonaPreferenciaNotificacion` por canal (SMS, EMAIL) y evento (ANUNCIADO, RECIBIDO, ENTREGADO). `activo` es el AND del canal y el evento en la v1.
- [x] No se crean filas para CANCELADO, LLAMADA ni WHATSAPP. `notify_payment_due` y `marketing_enabled` se descartan.
- [x] Los clientes sin preferencias no generan filas y quedan con el comportamiento por defecto de la v2.
- [x] La v1 gana en las filas que vienen de la v1. Una segunda pasada idéntica no cambia nada.

## Comments

**2026-09-24 — reemplazado por decisión de Jesús (opción C).** Se había implementado el mapeo, pero
los 7 clientes con preferencias en la v1 tienen SMS prendido en Recibido y Entregado, que en la v2
solo puede activar un ADMIN (política del 2026-08-26). Se retiró el mapeo del servicio y del lector.
Ahora las pruebas (`test_importador_v1_preferencias.py`) fijan lo contrario: la Persona importada
queda con el default de la v2 (SMS solo en Anunciado) y lo que configure en la v2 sobrevive a las
pasadas siguientes.
