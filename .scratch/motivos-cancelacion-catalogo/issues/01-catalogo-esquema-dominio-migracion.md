# 01 — Catálogo de motivos: esquema, dominio y migración de datos existentes

**What to build:** la base de datos y el seam de dominio para el catálogo editable de motivos de cancelación — sin cambiar todavía ninguna pantalla visible. Al terminar este ticket, `MotivoCancelacion` (el enum) sigue siendo la fuente real que usan `/paquetes` y `/administracion/notificaciones`; este ticket solo deja lista la infraestructura que los tickets 02 y 03 van a consumir.

Contexto: spec completo en `.scratch/motivos-cancelacion-catalogo/spec.md`. Los motivos son texto simple ("bandera informativa"), sin código estable separado de la etiqueta, sin activo/inactivo, sin orden manual, sin historial de auditoría — decisiones explícitas del cliente a favor de la máxima simplicidad.

**Blocked by:** None — can start immediately.

**Status:** done · 1352 tests verdes

- [x] Nueva tabla `motivos_cancelacion`: `id` (UUID PK), `etiqueta` (`String`, `NOT NULL`, `UNIQUE`), `creado_en` (`DateTime`, default ahora). Sin columna de código separado, sin `activo`, sin `orden`.
- [x] Nuevo módulo de dominio `motivo_cancelacion_service.py` (junto a `notificacion_service.py`) con:
  - `listar_motivos(session)` — todas las filas, ordenadas por `creado_en` ascendente.
  - `crear_motivo(session, etiqueta)` — `ValueError` si la etiqueta queda vacía tras `strip()`, o si ya existe una fila con el mismo texto exacto.
  - `editar_motivo(session, motivo_id, etiqueta)` — misma validación que crear, comparando contra las demás filas (no contra sí misma).
  - `eliminar_motivo(session, motivo_id)` — `ValueError` si es la última fila restante del catálogo (cancelar un paquete sigue exigiendo un motivo obligatorio). Borrado duro: no toca `plantillas_notificacion` ni `paquetes` ya existentes.
  - `motivo_valido(session, etiqueta)` — `True`/`False` según si esa etiqueta existe hoy en el catálogo.
- [x] Migración Alembic (una sola revisión):
  - Crea la tabla `motivos_cancelacion`.
  - Inserta las 4 filas iniciales en este orden: "Anuncio erróneo", "Devuelto al transportador", "No reclamado", "Otro" (mismo orden que el enum original, para que `creado_en` preserve el orden histórico del picker).
  - `UPDATE` sobre `plantillas_notificacion.motivo` y `paquetes.cancel_reason`: reescribe cada valor crudo (`ANUNCIO_ERRONEO`, `DEVUELTO_AL_TRANSPORTADOR`, `NO_RECLAMADO`, `OTRO`) a su etiqueta legible correspondiente. Cualquier `cancel_reason` que no calce con esos 4 valores crudos (texto libre ya tecleado vía "Otro" alguna vez) se deja intacto.
- [x] Tests de dominio nuevos en `tests/data_model/test_motivo_cancelacion.py`: crear guarda y aparece en `listar_motivos`; crear con etiqueta vacía o duplicada lanza `ValueError` sin guardar nada; editar cambia el texto sin crear fila nueva y valida vacío/duplicado contra las demás filas; eliminar borra cuando hay más de una fila; eliminar la última fila lanza `ValueError` y la fila sigue existiendo; `listar_motivos` respeta el orden de `creado_en`; `motivo_valido` distingue etiquetas existentes de inexistentes.
- [x] Migración verificada manualmente contra el ambiente de desarrollo local (`paquetex_dev_pg`), confirmando sobre los datos reales ya presentes (2 paquetes cancelados, 12 filas de `plantillas_notificacion` de CANCELADO) que las etiquetas quedan legibles tras la migración.
- [x] `test_parity_esquema_orm` (guard existente de paridad esquema↔ORM) sigue pasando con la tabla nueva.
