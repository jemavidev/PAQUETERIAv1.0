# Restricción de base de datos para el refactor de arquitectura

**Fecha del análisis:** 2026-07-20
**Contexto:** insumo fijo para las decisiones del reporte de `/improve-codebase-architecture` (13 candidatos, ver `architecture-review.html`). Cualquier candidato que toque persistencia debe respetar lo descrito aquí.

## Regla dura

**La estructura real y viva en RDS es la única fuente de verdad.** Ni la carpeta `alembic/versions/` de este repo, ni la del contenedor `prod` en ejecución, representan correctamente el estado actual de la base — las tres versiones no coinciden entre sí (ver abajo). El refactor se diseña **sobre las tablas que existen hoy en RDS**, sin asumir que `alembic upgrade head` reconstruye ese estado desde cero.

## Motor y conexión

- PostgreSQL, vía SQLAlchemy 2.0 + Alembic 1.12 (`psycopg2-binary`), string de conexión en `DATABASE_URL`.
- No corre en el servidor de aplicación — es una instancia AWS RDS separada (`us-east-1`), base `paqueteria_v4`. El contenedor prod (`paqueteria_v1_prod_app`) solo aloja la app, celery, redis y monitoreo.

## Las 28 tablas reales (RDS, hoy)

```
alembic_version, cufe_records, customer_otps, customer_preferences, customers,
file_uploads, invoice_irregularities, invoice_items, invoice_products_v2,
invoice_rejected_files, invoices, invoices_v2, messages, notifications,
package_announcements_new, package_events, package_history, packages,
product_column_config, product_sync_log, products, rates, sms_configuration,
sms_message_templates, supplier_invoices, suppliers, user_preferences, users
```

## Los tres estados no coinciden

| Fuente | Revisión / estado |
|---|---|
| **RDS real** | estampada en `036db1d68539` |
| **Contenedor `prod` en ejecución** | su propio `alembic current` **falla** — no conoce `036db1d68539`. Sus heads (`0001_customer_otp`, `61567198240c`, `create_customer_prefs`, `fix_recipient_length`) no tienen relación con los de este repo. La imagen desplegada es de un punto de código más viejo que lo ya aplicado en RDS — falta reconstruir/redeployar el contenedor. |
| **`staging` (este repo)** | sí contiene `036db1d68539`, pero va por delante de RDS: define 4 tablas sin migración (ver abajo). |

## Tablas huérfanas — fuera de alcance salvo decisión explícita

`reports`, `report_templates`, `dashboard_metrics`, `report_schedules` — modeladas en `src/app/models/report.py` + `src/app/services/report_service.py`, **no existen en RDS y no tienen migración de Alembic escrita**. No hay ruta expuesta (`routes/`) que las use — feature dormida. Si el refactor toca este módulo, requiere escribir la migración faltante antes de considerarlo "terminado"; si no, excluir del alcance.

## Deuda del grafo de migraciones (independiente de lo anterior)

38 migraciones, pero **3 raíces desconectadas** (`down_revision = None`) en vez de 1:

- `b6183f4234d3` — raíz real de la cadena principal.
- `20260119_170057` y `add_blocked_status` — ambas con el comentario sin resolver `# Actualizar con la última revisión`; alguien generó el stub y nunca lo enlazó al head real de su momento.

Esto ya causó incidentes: `fix_migration_conflict.py`, `INSTRUCCIONES_MIGRACION.md`, `INSTRUCCIONES_FIX_MIGRACION.md` (raíz del repo) son arreglos manuales previos sobre este mismo problema. Si el refactor incluye tocar el árbol de migraciones, esta deuda debe resolverse como parte del trabajo, no asumirse resuelta.

## Qué implica para cualquier candidato de refactor

1. No agregar/quitar/renombrar tablas o columnas fuera del alcance explícito del candidato elegido.
2. No asumir que el historial de Alembic es reconstruible de forma limpia — verificar contra RDS, no contra los archivos de migración.
3. El módulo de `reports` está fuera de alcance salvo que se decida terminarlo (requiere migración nueva).
4. Redeploy del contenedor (para que coincida con `staging`) es un problema de operación separado del refactor — no bloquea el análisis, pero sí bloquea cualquier despliegue de los cambios del refactor hasta resolverse.

---

## Nota (2026-07-22): rol de este documento tras el grilling

El rebuild **no hereda** este esquema — parte de una base nueva con un modelo distinto (ver [SYSTEM_REBUILD_BRIEF.md](SYSTEM_REBUILD_BRIEF.md) §6: teléfono como llave, apartamento como agrupador mutable, paquete como snapshot). Estas 28 tablas dejan de ser "el esquema a mantener" y pasan a ser la **fuente de la migración**: son la verdad de los datos existentes que se importarán al modelo nuevo (mapeo en §11 del brief). Es decir, este archivo sigue vigente **para migrar desde**, no **para construir sobre**.
