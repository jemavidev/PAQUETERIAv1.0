# 63 — Índices faltantes en `paquetes`/`paquete_fotos`

**Pedido original (cliente):** "estas versiones estan ya listas, verifica y
analiza a fondo que todo fluya de la manera mas optioma, enfocada en la
base de datos" — seguido de un análisis a fondo (agente en background) que
encontró varios hallazgos; el cliente eligió aplicar específicamente los
índices faltantes.

**Status:** implementado

## Contexto

Auditoría de base de datos encontró columnas que se filtran/ordenan/
joinean en código real (`/consultar`, `/paquetes` staff, `/mis-paquetes`
cliente) sin índice de respaldo. La más urgente: `guide_number`, filtro de
`/consultar` -- la única vista PÚBLICA sin sesión del sistema -- cada
búsqueda por guía era un full table scan.

## Implementación

Migración `0025_indices_paquetes` (índices planos, no parciales ni
únicos -- puro apoyo de consulta):

- `paquetes.guide_number`
- `paquetes.announced_by_phone`
- `paquetes.recipient_phone`
- `paquetes.estado`
- `paquetes.announced_at`
- `paquete_fotos.paquete_id` (la FK no traía índice propio -- Postgres no
  las indexa automáticamente)

Los modelos ORM (`app/domain/paquete.py`, `app/domain/paquete_foto.py`)
declaran los mismos índices con nombre explícito idéntico al de la
migración, siguiendo el mismo criterio ya establecido en este archivo
("Constraints con nombre explícito... para que el guard de paridad
esquema↔ORM no reporte drift").

De paso: `paquete_fotos` no estaba registrada en
`test_parity_esquema_orm.py` (el guard que compara el esquema migrado
contra `Base.metadata`) -- se agregó, ya que el índice nuevo de esa tabla
necesitaba quedar cubierto por ese guard.

## Verificación

- `test_migracion_y_orm_no_divergen` (el guard de paridad): pasa, sin
  drift -- ni en las tablas nuevas ni en `paquete_fotos`, recién
  registrada.
- Ciclo manual `upgrade head` → `downgrade -1` → `upgrade head` contra un
  Postgres desechable: limpio, sin typos en ninguna dirección.
- Suite completa (`tests/data_model tests/web`): 637/637, sin
  regresiones.
- Pendiente: desplegar (la migración corre sola en el arranque del
  contenedor -- `alembic -x db_url=... upgrade head` en el `CMD` del
  Dockerfile del repo de deploy).
