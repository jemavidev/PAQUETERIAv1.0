# 01 — Índices GIN de trigramas + reescritura de `condiciones_busqueda_paquetes`

**Status:** implementado y verificado localmente, pendiente revisión final y plan de despliegue.

## Diagnóstico (proceso `diagnosing-bugs`, no solo lectura de código)

Feedback loop: sembré 50.000 paquetes sintéticos en la base de dev local (Postgres real, mismo
esquema, no un mock), medí con `EXPLAIN ANALYZE` + `curl` secuencial contra el servidor de dev
corriendo de verdad, con datos limpiados después de cada ronda.

**Hallazgo 1** (primera ronda): `condiciones_busqueda_paquetes` arma `ILIKE '%texto%'` (comodín al
inicio) sobre 7 columnas de `paquetes` y comparte el `OR` con 2-3 condiciones de `personas` (vía
`outerjoin`). Sin `pg_trgm`, cualquier `ILIKE` con comodín al inicio es un full table scan --
confirmado, ~190ms a 50k filas.

**Hallazgo 2** (segunda ronda, tras instalar `pg_trgm` + índices GIN): los índices funcionan
perfecto en aislamiento (0.177ms para una sola columna, de ~190ms) pero la consulta REAL seguía en
~215ms -- CASI SIN CAMBIO. Confirmado con `enable_seqscan=off`: un `OR` que mezcla columnas de dos
tablas después de un `JOIN` no se puede partir en escaneos de índice por separado -- Postgres tiene
que evaluar la expresión completa fila por fila, así que cae a escanear `paquetes` entera sin
importar qué índices existan. Esto afecta el 100% de las búsquedas (las 2 condiciones de
`personas` están SIEMPRE presentes en la función, nunca son opcionales), y por lo tanto también a
`/residentes` (misma función, vía `contar_paquetes_de_persona`, UNA VEZ POR RESIDENTE de la
página) y al badge "Mostrar conexiones" (calculado en cada búsqueda, se abra o no el panel).

## Diseño de la solución

1. **Índices GIN de trigramas** (`pg_trgm`) sobre las columnas de `paquetes` que se buscan con
   `ILIKE` (`access_code`, `guide_number`, `recipient_name`, `snapshot_torre`,
   `snapshot_apartamento`, `recipient_phone`, `announced_by_phone`) y de `personas` (`nombre`,
   `email`, `whatsapp_usuario`).
2. **Reescritura de `condiciones_busqueda_paquetes`** para que el `OR` final sea EXCLUSIVAMENTE
   sobre columnas de `Paquete` -- la parte de `Persona` (email/WhatsApp del anunciante, "mismo
   destinatario") se resuelve ANTES, en una consulta chica y aparte contra `personas` (tabla mucho
   más chica que `paquetes`, y ahora con sus propios índices de trigramas), y el resultado (0-2
   personas típicamente) se traduce a condiciones de `Paquete`
   (`announced_by_persona_id == id AND lower(recipient_name) == lower(nombre)`) -- comparaciones
   exactas, sin `ILIKE`, 100% indexables. El caller ya no necesita el `outerjoin`.
3. **Índice B-tree en `paquetes.announced_by_persona_id`** (FK sin índice hasta ahora) -- lo usa la
   reescritura de arriba para reconectar con `Paquete` sin el join.

Equivalencia matemática verificada: `(A ∨ B) ∧ D ≡ (A∧D) ∨ (B∧D)` -- combinar las condiciones de
`Persona` en una sola consulta y aplicar la condición de exclusión/inclusión (`mismo_destinatario`)
por resultado es exactamente equivalente a las condiciones AND/OR separadas de antes.

## Implementación

- `alembic/versions/0042_indices_busqueda_paquetes.py` (nueva): `CREATE EXTENSION IF NOT EXISTS
  pg_trgm` + 10 índices GIN + 1 índice B-tree, todos con `CREATE INDEX CONCURRENTLY` (fuera de la
  transacción de la migración, vía `autocommit_block()`) -- son índices de apoyo, no refuerzan
  ningún invariante, así que no hay urgencia que justifique bloquear escrituras en una tabla que ya
  esté grande al momento de desplegar.
- `app/domain/paquete_service.py::condiciones_busqueda_paquetes`: firma cambia de `(q, conectados)`
  a `(session, q, conectados)` -- ya no es una función "pura", necesita resolver personas
  candidatas. `false()` como guardia en el modo `conectados` para que `or_(*condiciones)` nunca
  reciba una lista vacía (antes las 3 condiciones de `Persona` siempre estaban presentes
  sintácticamente; ahora, sin ninguna Persona candidata y sin dígitos de teléfono, la lista podía
  quedar vacía -- `or_()` sin argumentos está deprecado en SQLAlchemy).
- 3 llamadores actualizados (pasan `session`, ya no hacen `.outerjoin(Persona, ...)`):
  `packages.py::_listar`, `packages.py::_contar_conexiones`,
  `paquete_service.py::contar_paquetes_de_persona`.
- `app/domain/paquete.py` / `app/domain/persona.py`: los 11 índices nuevos declarados también en
  `__table_args__` del ORM (guard de paridad esquema↔ORM, `test_parity_esquema_orm`).

## Verificación

- **Re-medido de punta a punta** contra los mismos 50.000 paquetes sintéticos, servidor de dev real
  (no solo `EXPLAIN`):

  | Vista | Antes | Después |
  |---|---|---|
  | `/paquetes` sin búsqueda | 368 ms | 92 ms |
  | `/paquetes?q=3001` (dígitos) | 540 ms | 115 ms |
  | `/paquetes?q=<nombre acotado>` | ~30 ms (match único, ya era rápido) | 30 ms |
  | `/paquetes?q=SINTETICO` (match ~100% de las filas -- caso patológico del dato sintético) | ~400 ms | 255 ms, seq scan correcto (el planner elige NO usar el índice cuando matchea casi toda la tabla -- comportamiento esperado, no un bug) |
  | `/residentes` (20 residentes/página) | **~2990 ms** | **162 ms** |

- `tests/web/test_packages.py`: 217/217 en verde (semántica exacta de issue 308 -- "exacto" vs
  "conectado" -- intacta).
- `tests/web/test_customers_manage.py` + `tests/data_model/test_announce_paquete.py`: 214/214 en
  verde.
- `tests/data_model/test_parity_esquema_orm.py`: sin drift nuevo -- el único drift que reporta
  (4 tablas de `proveedores_*`/`plantillas_notificacion_historial`) es PREEXISTENTE, no relacionado
  con este cambio (esos modelos ya no estaban importados en ese test antes de hoy).
- Datos sintéticos limpiados de la base de dev local después de cada ronda de medición -- la base
  quedó exactamente como estaba (31 paquetes reales).

## Pendiente (decisión del cliente, no implementado todavía)

- Plan de despliegue a test.papyrus.com.co / producción -- la migración corre `CREATE INDEX
  CONCURRENTLY`, diseñada para no bloquear el mostrador durante el despliegue, pero conviene
  confirmar el tamaño real de la tabla en producción antes de desplegar (cuánto puede tardar
  construir 11 índices depende de cuántas filas haya hoy).
