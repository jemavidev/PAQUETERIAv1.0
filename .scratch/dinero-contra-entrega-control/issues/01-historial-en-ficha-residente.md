# 01 — Historial de movimientos en la ficha del residente

**What to build:** en la ficha de un residente (`/residentes/{id}`), dentro del modal "Saldo" que ya
existe (hoy solo muestra "Saldo actual: $X" y el formulario para registrar un movimiento nuevo), se
agrega debajo de eso la lista completa del historial de movimientos de ESA Persona — más recientes
primero. Cada fila muestra: monto (verde si es un ingreso/positivo, rojo si es un egreso/negativo),
fecha y hora, qué miembro de staff lo registró, y a qué paquete se aplicó (link a su código de
acceso) o una indicación de "movimiento manual" si no tiene ningún paquete asociado. Si la Persona
nunca tuvo ningún movimiento, se muestra un mensaje de lista vacía, nunca un error ni una sección
rota. Reusa la función de dominio `movimientos_de_persona` (ya existente, hoy solo la consume
`/mis-datos`) — no requiere ninguna función de dominio nueva ni ninguna migración.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] El modal "Saldo" de una Persona con movimientos existentes lista todos ellos, más recientes
      primero, debajo del formulario de "Actualizar".
- [ ] Cada fila muestra monto con color correcto según el signo (verde ≥0 / rojo <0), fecha y hora,
      el nombre del miembro de staff que lo registró, y el paquete asociado (link a su código de
      acceso) o "movimiento manual" si `paquete_id` es nulo.
- [ ] El modal "Saldo" de una Persona SIN ningún movimiento muestra un mensaje de lista vacía, sin
      error.
- [ ] No se agrega ninguna forma de editar ni borrar un movimiento desde este modal — sigue siendo
      estrictamente de solo lectura (append-only, mismo criterio que el resto del módulo).
- [ ] Tests nuevos en el archivo de tests web de la ficha de residentes, verificando lo anterior por
      HTML renderizado (no por aserciones sobre código interno).
