# 06 — Estadísticas de cobros (admin)

**What to build:** una página de solo lectura bajo `/administracion` con un selector de rango de
fechas (día/mes/año) que muestra cantidad y monto total cobrado, desglose por cliente/apartamento, y
tiempo promedio de bodegaje — sin exportar a archivo ni filtros avanzados en esta versión.

**Blocked by:** 02 — Entrega atómica con cobro.

**Status:** ready-for-agent

- [ ] La página muestra cantidad y monto total recaudado para un rango de fechas dado
- [ ] Muestra el desglose por cliente/apartamento
- [ ] Muestra el tiempo promedio de bodegaje
- [ ] Exclusiva de `require_admin` (un operador recibe 403)
