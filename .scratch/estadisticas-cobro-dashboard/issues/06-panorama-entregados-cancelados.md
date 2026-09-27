# 06 — Panorama: Entregados y Cancelados

**What to build:** las dos tarjetas fijas de Panorama que faltan junto a Ingresos: Entregados y
Cancelados, cada una con Hoy | Semana | Mes, separadas entre sí (nunca sumadas en "procesados").

**Blocked by:** 01

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `domain/estadisticas_tablero_service.py`)

- [ ] "Entregados" muestra Hoy, Esta semana y Este mes: paquetes ENTREGADO por fecha de entrega, en hora
      de Colombia.
- [ ] "Cancelados" muestra Hoy, Esta semana y Este mes: paquetes CANCELADO por fecha de cancelación, en
      hora de Colombia — en tarjeta separada de Entregados, nunca combinadas en un solo "procesados".
- [ ] Ninguna de las dos tarjetas cambia al tocar los filtros de la barra (Panorama es fijo).
- [ ] Con la base vacía, ambas muestran 0 sin error.
