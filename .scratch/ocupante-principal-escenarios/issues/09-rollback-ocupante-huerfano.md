# 09 — Integridad transaccional: rollback al fallar el paso siguiente a crear un Ocupante

**What to build:** en `/announce` Torre+Apto → nueva persona, y en `/paquetes` → Corregir destinatario → nuevo ocupante: si `agregar_ocupante` tiene éxito pero el paso siguiente de esa misma acción compuesta falla (no hay Anunciante resolvible; `corregir_destinatario` falla por cambio de estado concurrente), la ruta hace `db.rollback()` explícito antes de devolver la respuesta de error — el Ocupante recién creado no debe quedar persistido si la acción completa no se concretó.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] `announce_new.py`: cuando `agregar_ocupante` tiene éxito pero `_anunciar_para` devuelve error (sin Anunciante resolvible), se hace `db.rollback()` antes de `return _error(...)`.
- [ ] `packages.py`: cuando `agregar_ocupante` tiene éxito pero `corregir_destinatario` lanza `TransicionInvalida`, se hace `db.rollback()` antes de devolver el error.
- [ ] Test de regresión explícito en ambos archivos: forzar el fallo del segundo paso y verificar que el Ocupante creado en el primer paso **no existe** en la base después de la request (no solo verificar el status code de la respuesta).
