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

**Status:** ready-for-agent

- [ ] Registro de proveedores en código (ubicación sugerida: junto a
      `app/domain/sms_failover.py`, o un módulo nuevo) declara, por canal, la lista
      ordenada de proveedores disponibles hoy (SMS: AWS SNS, LIWA, Twilio; Email:
      SMTP) y, por cada uno, sus campos de configuración (nombre de variable de
      entorno, tipo, si es secreto) — usando exactamente las variables enumeradas en
      el spec (sección "Variables involucradas hoy").
- [ ] Tabla de base de datos nueva: un registro por `(canal, proveedor)` con
      `habilitado` (bool), `orden` (int, nullable), `updated_at`, `updated_by` (FK
      nullable a `usuarios`, mismo criterio que `PlantillaNotificacionHistorial.
      usuario_id`).
- [ ] Tabla de auditoría nueva, append-only (solo INSERT, nunca UPDATE/DELETE): por
      cada cambio de habilitado/orden guarda canal, proveedor, quién, cuándo, valor
      anterior y nuevo completos.
- [ ] `app/domain/proveedor_config_service.py` (o nombre equivalente): funciones para
      listar la configuración vigente por canal, y para guardar un cambio de
      habilitado/orden (que además escribe la fila de auditoría) — mismo estilo y
      altitud que `notificacion_service.py`.
- [ ] Migración de Alembic que siembra el estado actual real de producción: AWS SNS
      orden 1 habilitado, LIWA orden 2 habilitado, Twilio orden 3 habilitado (SMS);
      SMTP único proveedor habilitado (Email) — desplegar este ticket solo (sin 02 ni
      03) no debe cambiar ningún comportamiento observable.
- [ ] Tests de dominio (`tests/data_model/test_proveedor_config_service.py`):
      habilitar/deshabilitar/reordenar contra una sesión de BD de test; verifica que
      queda una fila de auditoría por cambio con el actor correcto; verifica que
      `usuario_id=None` es honesto cuando no hay actor.
