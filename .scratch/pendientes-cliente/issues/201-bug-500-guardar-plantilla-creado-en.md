# 201 — Bug real: 500 al guardar cualquier plantilla (columna `creado_en`/`created_at`)

**Pedido original (cliente):**
"Me acabo de dar cuenta que cuando modifico uno de los mensajes me aparece
este error al guardar los cambios: 'Internal Server Error'."

**Status:** implementado (vía `/diagnosing-bugs`)

## Causa raíz

`0034_plantilla_historial` (ticket 04) creaba originalmente la columna
`creado_en`. El code-review de ese mismo ticket la corrigió a `created_at`
(consistencia con `created_at`/`updated_at` del resto del dominio) --
pero editando el ARCHIVO de la migración 0034 **in-place**, después de que
esa migración ya se había corrido contra el Postgres persistente de
desarrollo local. Alembic solo registra qué revisión ya se aplicó
(`alembic_version`) -- nunca vuelve a ejecutar una migración ya aplicada
aunque su archivo cambie después, así que la tabla física se quedó con
`creado_en` mientras el código (ORM + INSERT real) ya esperaba
`created_at`. La suite de tests seguía en verde porque el Postgres
EFÍMERO de los tests siempre se construye desde cero con el archivo de
migración ya corregido -- nunca tuvo la oportunidad de heredar el nombre
viejo.

**Lección (para no repetirla):** nunca editar una migración que ya corrió
contra una base real (dev persistente, staging, producción) -- corregir
siempre hacia adelante con una migración nueva.

## Fix

- Nueva migración `0035_historial_created_at`: renombra `creado_en` →
  `created_at` SOLO si la columna vieja existe (bloque condicional
  `information_schema`) -- segura tanto para una BD que ya corrió la 0034
  original (la corrige) como para una BD que corre la 0034 ya arreglada
  por primera vez (no hace nada, ya está bien).
- 2 tests de regresión nuevos en `test_migration_graph.py` (Seam B, mismo
  patrón de `empty_db_url` que el resto del archivo): uno simula el
  escenario real (migra hasta 0034, renombra la columna a mano para
  imitar una BD "vieja", confirma que `upgrade head` la corrige); otro
  confirma que 0035 no rompe nada en una BD nueva. Se confirmó el ciclo
  rojo→verde: el primero falla sin la migración 0035, pasa con ella.
- Nuevos helpers `column_exists`/`rename_column` en `tests/_harness.py`.

## Verificación

- Reproducido el 500 real contra el servidor de dev local (mismo
  traceback exacto que capturó el log real: `UndefinedColumn: column
  "created_at"... does not exist`), antes del fix.
- Aplicada la migración 0035 al Postgres persistente de desarrollo local
  (`alembic upgrade head`) -- confirmado por `\d
  plantillas_notificacion_historial` que la columna ya es `created_at`.
- Repetido el MISMO guardado que daba 500: ahora `200` + toast "Plantilla
  guardada", con la fila de historial real insertada correctamente.
- Suite completa: ver commit para el conteo final.

## Pendiente

- Deploy a test.papyrus.com.co (esa base NUNCA corrió la 0034 vieja --
  cuando se despliegue, correrá 0034+0035 juntas de una vez, sin problema).
