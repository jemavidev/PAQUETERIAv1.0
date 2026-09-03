# 02 — `/administracion/notificaciones` gestiona el catálogo y las filas CANCELADO lo reflejan

**What to build:** desde `/administracion/notificaciones`, el ADMIN puede crear, editar y borrar motivos de cancelación (mismo estilo visual que el resto de la pantalla: modales `data-open`/`data-close`, toasts de error/éxito). Las filas del tab CANCELADO (una por motivo, con sus 3 canales de plantilla) pasan a generarse desde ese catálogo en vez del enum fijo — crear un motivo nuevo hace aparecer su fila de plantillas automáticamente, con el texto por defecto hasta que se personalice.

Contexto: spec completo en `.scratch/motivos-cancelacion-catalogo/spec.md`. Depende del seam de dominio del ticket 01 (`motivo_cancelacion_service.py`).

**Blocked by:** 01 — Catálogo de motivos: esquema, dominio y migración de datos existentes.

**Status:** done · 1352 tests verdes

- [x] `_filas_plantillas` (en la ruta de `/administracion/notificaciones`) deja de iterar el enum `MotivoCancelacion` y pasa a iterar `listar_motivos(db)` — cada fila usa la `etiqueta` del motivo como el `motivo` que ya viaja hoy a `_canales_de`/`obtener_texto_actual`/`guardar_plantilla` (sin cambiar la firma de esas funciones, siguen recibiendo un `str`).
- [x] Se agrega una sección de gestión del catálogo en esa misma pantalla: crear un motivo nuevo (un campo de texto), editar el texto de uno existente, y borrarlo.
- [x] Crear/editar con texto vacío muestra un error claro y no guarda nada.
- [x] Crear/editar con un texto que ya existe exactamente igual en otra fila muestra un error claro y no guarda nada.
- [x] Intentar borrar el único motivo que queda en el catálogo muestra un error claro y la fila sigue existiendo.
- [x] Solo `ADMIN` puede crear/editar/borrar motivos — `OPERADOR` recibe 403, igual que el resto de esta pantalla.
- [x] Tests extendidos en `tests/web/test_admin_notificaciones.py` (mismo patrón `_login_admin`/`_login_operador` ya presente): gate de rol sin cambios; crear un motivo lo agrega a las filas CANCELADO mostradas; crear con etiqueta vacía o duplicada devuelve error sin alterar el catálogo; borrar un motivo lo quita de las filas mostradas; borrar el último motivo devuelve error y la fila sigue apareciendo.
