# 15 — Tarjetas de SMS: costo estimado

**What to build:** con las cantidades ya en pantalla (14) y el costo configurable ya existiendo (13), las
tarjetas de SMS ganan su costo estimado en Panorama y en Periodo, más "Costo de SMS por paquete".

**Blocked by:** 13, 14

**Status:** implementado (cerrado en la revisión del 2026-09-26; evidencia: `TrioCosto` en el tablero)

- [ ] Panorama → "SMS enviados por AWS" muestra, debajo de cada columna (Hoy/Semana/Mes), el costo
      estimado = cantidad de esa columna × el costo promedio configurado HOY (no un precio histórico).
- [ ] Periodo → "Costo estimado de SMS" = cantidad de SMS por AWS del periodo × el costo configurado hoy.
- [ ] Periodo → "Costo de SMS por paquete" = costo estimado del periodo ÷ total de paquetes con
      movimiento en el periodo (el mismo total del ticket 02).
- [ ] Cambiar el costo configurado en Proveedores (ticket 13) y volver a cargar el tablero recalcula
      TODAS las cifras de costo, incluidas las de periodos pasados — no queda ningún costo "congelado" al
      precio con el que se envió.
- [ ] Sin ningún costo configurado todavía, las tarjetas de costo (en ambas zonas) muestran las
      cantidades igual y, en el lugar del monto, un texto tipo "Configura el costo en Proveedores" con
      enlace a esa pantalla — nunca un error, un $0 engañoso, ni una división por cero.
