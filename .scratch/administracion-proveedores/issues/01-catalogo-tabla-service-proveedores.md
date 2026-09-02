# 01 — Catálogo de proveedores en código + tabla de configuración + service de dominio

**What to build:** la base de datos y el service de dominio que van a sostener toda la
feature — un registro en código de qué proveedores/campos existen por canal, una
tabla nueva que guarda habilitado/orden por `(canal, proveedor)`, una tabla de
auditoría append-only (mismo patrón que `PlantillaNotificacionHistorial`), y las
funciones de dominio para leer/escribir ese estado. Sin ruta HTTP ni pantalla
todavía — este ticket es puramente el seam de dominio + su migración de siembra, para
que los tickets 02 y 03 lo consuman sin volver a tocar el modelo de datos.

Ver `.scratch/administracion-proveedores/spec.md` (secciones Implementation
Decisions y User Stories 1, 2, 15-19, 21) para el diseño completo acordado.

**Blocked by:** Ninguno — puede arrancar ya.

**Status:** verificado

- [x] Registro de proveedores en código (ubicación sugerida: junto a
      `app/domain/sms_failover.py`, o un módulo nuevo) declara, por canal, la lista
      ordenada de proveedores disponibles hoy (SMS: AWS SNS, LIWA, Twilio; Email:
      SMTP) y, por cada uno, sus campos de configuración (nombre de variable de
      entorno, tipo, si es secreto) — usando exactamente las variables enumeradas en
      el spec (sección "Variables involucradas hoy"). → `app/domain/
      proveedores_catalogo.py` (módulo nuevo, dedicado — `sms_failover.py` es
      específicamente el mecanismo de retry, no el catálogo de proveedores).
- [x] Tabla de base de datos nueva: un registro por `(canal, proveedor)` con
      `habilitado` (bool), `orden` (int, nullable), `updated_at`, `updated_by` (FK
      nullable a `usuarios`, mismo criterio que `PlantillaNotificacionHistorial.
      usuario_id`). → `app/domain/proveedor_config.py` (`ProveedorConfig`).
- [x] Tabla de auditoría nueva, append-only (solo INSERT, nunca UPDATE/DELETE): por
      cada cambio de habilitado/orden guarda canal, proveedor, quién, cuándo, valor
      anterior y nuevo completos. → `app/domain/proveedor_config_historial.py`
      (`ProveedorConfigHistorial`).
- [x] `app/domain/proveedor_config_service.py`: `listar_config`/
      `guardar_habilitado_orden`, mismo estilo y altitud que `notificacion_service.py`
      — incluye el mismo manejo de carrera (`IntegrityError` → retry como UPDATE) que
      `guardar_plantilla`, agregado tras el `code-review` de este ticket.
- [x] Migración de Alembic (`0037_proveedor_config`) que siembra el estado actual real
      de producción: AWS SNS orden 1 habilitado, LIWA orden 2 habilitado, Twilio orden
      3 habilitado (SMS); SMTP único proveedor habilitado, sin orden (Email).
- [x] Tests de dominio (`tests/data_model/test_proveedor_config_service.py`, 8 tests):
      crear/actualizar, historial con anterior correcto (incluyendo `None` en la
      primera fila), append-only, actor `None` honesto, actor presente, listado
      ordenado por canal.

**Code review** (`code-review`, ejes Standards + Spec): 2 hallazgos confirmados en
Standards, ambos corregidos antes de commitear — (1) faltaba el manejo de carrera de
`guardar_plantilla`, agregado; (2) `canal` pasó de `String(20)` a
`Enum(CanalNotificacion, native_enum=False, length=20)`, igual que
`PlantillaNotificacion`/`PlantillaNotificacionHistorial`. Eje Spec: 0 faltantes, 0
scope creep.

**Verificación:** suite completa (1271 passed) tras los fixes del code review.
