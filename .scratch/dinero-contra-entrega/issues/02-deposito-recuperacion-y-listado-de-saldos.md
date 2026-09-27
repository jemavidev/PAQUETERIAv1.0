# 02 — Depósito/recuperación (staff) + listado de saldos

**What to build:** cualquier miembro del staff registra un depósito o una recuperación desde la
ficha del residente (sin depender de ningún paquete), y una página de búsqueda simple bajo
`/residentes` (no `/administracion` — accesible a cualquier staff) muestra qué residentes tienen
saldo distinto de cero.

**Blocked by:** 01 — Núcleo: entidad y funciones de saldo.

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: 65d8bd0)

- [ ] Cualquier rol de staff registra un depósito/recuperación desde la ficha del residente
- [ ] El listado de saldos muestra solo residentes con saldo distinto de cero
- [ ] Un residente en $0 no aparece en el listado
