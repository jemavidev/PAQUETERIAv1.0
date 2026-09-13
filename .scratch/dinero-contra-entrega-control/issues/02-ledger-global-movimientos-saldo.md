# 02 — Ledger global de movimientos de saldo contra entrega

**What to build:** una vista nueva, accesible a cualquier rol de staff (mismo criterio de permisos
que `/residentes/saldos-contra-entrega`, no exclusiva de Admin), en una ruta estática nueva bajo
`/residentes` (registrada antes de `/residentes/{persona_id}`, mismo cuidado de orden que ya tiene la
ruta de resumen existente). Lista TODOS los movimientos de saldo contra entrega de TODOS los
residentes, más recientes primero, paginada (mismo patrón de paginación que el resto de listados
largos del sistema). Incluye dos filtros: por residente (nombre, teléfono o usuario de WhatsApp) y
por tipo (ingreso vs. egreso, según el signo del monto). Cada fila muestra: a qué residente
pertenece, el monto (con el mismo color verde/rojo que el resto del módulo), fecha y hora, quién de
staff lo registró, y el paquete asociado (link a su código de acceso) o una indicación de que fue un
movimiento manual sin paquete. La página de resumen actual (`/residentes/saldos-contra-entrega`)
agrega un link "Ver historial completo" hacia esta vista nueva.

Requiere una función de dominio nueva en `saldo_contra_entrega_service.py` (batch, no una consulta
por fila) que liste movimientos de todas las Personas con los filtros de búsqueda/tipo y paginación —
distinta de `movimientos_de_persona` (ya existente, acotada a una sola Persona).

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Cualquier rol de staff (no solo Admin) puede acceder a la nueva ruta del ledger global.
- [ ] Sin filtros, la vista lista los movimientos más recientes de todos los residentes, paginados.
- [ ] El filtro por residente (nombre, teléfono o WhatsApp) acota la lista a los movimientos de esa
      Persona.
- [ ] El filtro de tipo separa correctamente ingresos (monto positivo) de egresos (monto negativo).
- [ ] Cada fila muestra el residente, monto con color, fecha y hora, quién lo registró, y el paquete
      asociado (link al código de acceso) o "movimiento manual" si no tiene.
- [ ] `/residentes/saldos-contra-entrega` (la página de resumen existente) tiene un link "Ver
      historial completo" que lleva a esta vista nueva.
- [ ] No se agrega ninguna forma de editar ni borrar un movimiento desde esta vista — sigue siendo
      estrictamente de solo lectura.
- [ ] Tests nuevos: uno en `tests/data_model/` para la función de dominio nueva (mezcla movimientos de
      varias Personas, filtra por búsqueda y por tipo, pagina correctamente), y uno en
      `tests/web/test_customers_manage.py` para la ruta (permisos, filtros, paginación, link desde el
      resumen) — por comportamiento externo, no por código interno.
