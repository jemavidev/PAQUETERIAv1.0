# 04 — Retirar el enum `MotivoCancelacion`

**What to build:** limpieza final (fase "contract" del expand-contract) — una vez que tanto `/administracion/notificaciones` (ticket 02) como `/paquetes` (ticket 03) leen del catálogo en vez del enum, se elimina `MotivoCancelacion` del código para no dejar dos fuentes de verdad conviviendo. Sin comportamiento nuevo visible para el usuario.

Contexto: spec completo en `.scratch/motivos-cancelacion-catalogo/spec.md`.

**Blocked by:** 02 — `/administracion/notificaciones` gestiona el catálogo y las filas CANCELADO lo reflejan; 03 — `/paquetes`: cancelar un paquete usa el catálogo (ambos consumidores deben haber migrado antes de borrar el enum que usaban).

**Status:** done · 1352 tests verdes

- [x] Se elimina la clase `MotivoCancelacion` de `app/domain/paquete.py`.
- [x] Se eliminan sus imports/referencias residuales en `admin.py` y `packages.py` (confirmado con `grep -rn "MotivoCancelacion"` — solo quedan referencias al catálogo nuevo `motivo_cancelacion.py`/`motivo_cancelacion_service.py`, que reutiliza el mismo nombre de clase para la entidad ORM).
- [x] `paquete_lifecycle.cancel()` pierde la rama `isinstance(motivo, MotivoCancelacion)` — `motivo` es siempre un `str` no vacío (el caller ya resuelve el texto final antes de llamar, igual que hoy hace `cancel_action` para "Otro").
- [x] `_motivo_legible()` (en `notificacion_service.py`) se eliminó en el ticket 03 al no quedar ningún otro caller.
- [x] `tests/data_model/test_cancelar_paquete.py` (único archivo que aún importaba el enum retirado) se actualizó a strings planos ("Anuncio erróneo", "Devuelto al transportador", "No reclamado", "Otro").
- [x] La suite completa de tests sigue pasando sin cambios de comportamiento: 1352 passed, 0 failed. Migración `0039_motivos_cancelacion` verificada también contra el ambiente de desarrollo local (`paquetex_dev_pg`), no solo el Postgres efímero de tests.
