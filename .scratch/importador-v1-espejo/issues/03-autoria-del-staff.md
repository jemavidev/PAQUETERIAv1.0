# 03 — Autoría del staff

**What to build:** en el detalle y la línea de tiempo de un paquete importado se ve quién lo recibió, entregó o canceló, igual que en uno nativo. La autoría sale de `package_history.changed_by`, la única traza que tiene la v1 (ver `../spec.md`, historias 31-36).

**Blocked by:** 02 — Paquetes espejo con sus códigos

**Status:** done

- [x] Migración: `origen_v1_id` en `usuarios`, con índice único parcial.
- [x] `rafael`, `maye`, `jveyes` y `jesus` se resuelven por email a usuarios existentes de la v2. `jesus` va al mismo usuario que `jveyes` (JESUS VILLALOBOS).
- [x] `MARIANELLA` se crea como usuario **inactivo** y sin contraseña que sirva. `operator_1` se representa con el usuario técnico inactivo "Operador v1 (sin identificar)". Ninguno de los dos puede iniciar sesión.
- [x] No se copian contraseñas de la v1.
- [x] El primer `RECIBIDO` da `received_by` (y `received_at` si falta), `ENTREGADO` da `delivered_by` y `CANCELADO` da `cancelled_by` más el motivo, que se asigna al motivo equivalente del catálogo de la v2 (`"otro"`).
- [x] Un `changed_by` desconocido queda en el reporte, y el campo queda en `NULL`.
- [x] `announced_by_usuario_id` queda en `NULL`, porque en la v1 anuncia el residente.
- [x] La línea de tiempo del paquete muestra los nombres correctos (prueba en `tests/web` o en el servicio de timeline).
